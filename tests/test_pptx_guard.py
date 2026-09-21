"""Behavior tests using deliberately small OOXML ZIP fixtures (not renderable decks)."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from xml.sax.saxutils import escape
import zipfile


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "pptx_guard.py"
NS = ('xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
      'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
      'xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart" '
      'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" '
      'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"')
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
REL_BASE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/"


def rels(rows):
    return '<Relationships xmlns="' + REL_NS + '">' + ''.join(
        f'<Relationship Id="{rid}" Type="{REL_BASE}{kind}" Target="{target}"'
        + (' TargetMode="External"' if external else '') + '/>'
        for rid, kind, target, external in rows) + '</Relationships>'


def text_shape(text="Original claim", runs=None, style="", extra=""):
    fragments = runs if runs is not None else [text]
    return ('<p:sp><p:nvSpPr><p:cNvPr id="2" name="Text"/></p:nvSpPr>'
            f'<p:spPr>{style}</p:spPr><p:txBody><a:bodyPr/><a:p>'
            + ''.join('<a:r><a:rPr sz="2000"/><a:t>' + escape(t) + '</a:t></a:r>' for t in fragments)
            + extra + '</a:p></p:txBody></p:sp>')


def slide(body, hidden=False):
    return f'<p:sld {NS} show="{0 if hidden else 1}"><p:cSld><p:spTree>{body}</p:spTree></p:cSld></p:sld>'


def deck(path, slides=None, parts=None, slide_rels=None, order=None):
    slides = slides if slides is not None else [slide(text_shape())]
    order = order if order is not None else list(range(len(slides)))
    entries = {
        'ppt/presentation.xml': f'<p:presentation {NS}><p:sldIdLst>'
        + ''.join(f'<p:sldId id="{256+i}" r:id="rId{i+1}"/>' for i in order)
        + '</p:sldIdLst></p:presentation>',
        'ppt/_rels/presentation.xml.rels': rels([
            (f'rId{i+1}', 'slide', f'slides/slide{i+1}.xml', False) for i in range(len(slides))]),
    }
    for i, body in enumerate(slides):
        entries[f'ppt/slides/slide{i+1}.xml'] = body
    for i, rows in (slide_rels or {}).items():
        entries[f'ppt/slides/_rels/slide{i+1}.xml.rels'] = rels(rows)
    entries.update(parts or {})
    with zipfile.ZipFile(path, 'w') as archive:
        for name, data in entries.items():
            archive.writestr(name, data)
    return path


class GuardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)],
                              capture_output=True, text=True)

    def compare(self, original, candidate):
        baseline = self.directory / 'baseline.json'
        result = self.directory / 'check.json'
        snap = self.run_cli('snapshot', original, '--output', baseline)
        self.assertEqual(snap.returncode, 0, snap.stderr)
        checked = self.run_cli('compare', baseline, candidate, '--output', result)
        return checked, json.loads(result.read_text(encoding='utf-8'))

    def test_exact_whitespace_is_protected_but_run_splitting_and_layout_pass(self):
        original = deck(self.directory / 'in.pptx', [slide(text_shape(' A  B '))])
        candidate = deck(self.directory / 'out.pptx', [slide(text_shape(
            runs=[' A', '  B '], style='<a:xfrm><a:off x="500" y="800"/></a:xfrm>'))])
        cli, report = self.compare(original, candidate)
        self.assertEqual(cli.returncode, 0, cli.stderr)
        self.assertTrue(report['passed'])
        self.assertEqual(report['visual_review'], 'required')
        self.assertEqual(report['editability_review'], 'required')
        deck(candidate, [slide(text_shape(' A B '))])
        cli, report = self.compare(original, candidate)
        self.assertEqual(cli.returncode, 1)
        self.assertFalse(report['passed'])

    def test_new_visible_text_and_deleted_text_fail(self):
        original = deck(self.directory / 'in.pptx')
        for body in (text_shape() + text_shape('New caption'), '<p:pic/>'):
            with self.subTest(body=body):
                candidate = deck(self.directory / 'out.pptx', [slide(body)])
                cli, report = self.compare(original, candidate)
                self.assertEqual(cli.returncode, 1)
                self.assertTrue(any('text' in item['check'] for item in report['differences']))

    def test_logical_order_and_hidden_state_are_protected(self):
        slides = [slide(text_shape('First')), slide(text_shape('Second'))]
        original = deck(self.directory / 'in.pptx', slides)
        candidate = deck(self.directory / 'out.pptx', slides, order=[1, 0])
        cli, report = self.compare(original, candidate)
        self.assertEqual(cli.returncode, 1)
        self.assertTrue(any(item['check'] == 'slide_order' for item in report['differences']))
        deck(candidate, [slide(text_shape('First'), hidden=True), slides[1]])
        cli, report = self.compare(original, candidate)
        self.assertEqual(cli.returncode, 1)
        self.assertTrue(any(item['check'] == 'hidden' for item in report['differences']))

    def test_notes_body_protected_but_slide_number_placeholder_ignored(self):
        original = self.directory / 'in.pptx'
        candidate = self.directory / 'out.pptx'
        def write(path, body, page):
            note = (f'<p:notes {NS}><p:cSld><p:spTree>{text_shape(body)}'
                    '<p:sp><p:nvSpPr><p:nvPr><p:ph type="sldNum"/></p:nvPr></p:nvSpPr>'
                    f'<p:txBody><a:p><a:r><a:t>{page}</a:t></a:r></a:p></p:txBody></p:sp>'
                    '</p:spTree></p:cSld></p:notes>')
            return deck(path, parts={'ppt/notesSlides/notesSlide1.xml': note},
                        slide_rels={0: [('note', 'notesSlide', '../notesSlides/notesSlide1.xml', False)]})
        write(original, 'Do not disclose', '1')
        write(candidate, 'Do not disclose', '8')
        self.assertEqual(self.compare(original, candidate)[0].returncode, 0)
        write(candidate, 'Changed note', '1')
        self.assertEqual(self.compare(original, candidate)[0].returncode, 1)

    def test_table_cell_and_equation_changes_fail(self):
        table = '<p:graphicFrame><a:graphic><a:graphicData><a:tbl><a:tr><a:tc><a:txBody><a:p><a:r><a:t>{}</a:t></a:r></a:p></a:txBody></a:tc></a:tr></a:tbl></a:graphicData></a:graphic></p:graphicFrame>'
        math = '<m:oMath><m:r><m:t>{}</m:t></m:r></m:oMath>'
        original = deck(self.directory / 'in.pptx', [slide(table.format('42') + text_shape(extra=math.format('x=2')))])
        for tbl, equation in [('43', 'x=2'), ('42', 'x=3')]:
            candidate = deck(self.directory / 'out.pptx', [slide(table.format(tbl) + text_shape(extra=math.format(equation)))])
            self.assertEqual(self.compare(original, candidate)[0].returncode, 1)

    def test_chart_value_change_and_flattening_fail_but_chart_fill_passes(self):
        body = text_shape() + '<p:graphicFrame><a:graphic><a:graphicData><c:chart r:id="chart"/></a:graphicData></a:graphic></p:graphicFrame>'
        def write(path, value='12', color='FF0000', body=body):
            chart = (f'<c:chartSpace {NS}><c:chart><c:plotArea><c:barChart><c:ser>'
                     f'<c:val><c:numLit><c:pt idx="0"><c:v>{value}</c:v></c:pt></c:numLit></c:val>'
                     f'<c:spPr><a:solidFill><a:srgbClr val="{color}"/></a:solidFill></c:spPr>'
                     '</c:ser></c:barChart></c:plotArea></c:chart></c:chartSpace>')
            return deck(path, [slide(body)], parts={'ppt/charts/chart1.xml': chart},
                        slide_rels={0: [('chart', 'chart', '../charts/chart1.xml', False)]})
        original = write(self.directory / 'in.pptx')
        candidate = write(self.directory / 'out.pptx', color='00FF00')
        self.assertEqual(self.compare(original, candidate)[0].returncode, 0)
        write(candidate, value='99')
        self.assertEqual(self.compare(original, candidate)[0].returncode, 1)
        write(candidate, body=text_shape() + '<p:pic/>')
        self.assertEqual(self.compare(original, candidate)[0].returncode, 1)

    def test_original_assets_must_remain_per_slide_and_new_images_are_allowed(self):
        original = deck(self.directory / 'in.pptx', parts={'ppt/media/image1.png': b'evidence'},
                        slide_rels={0: [('image', 'image', '../media/image1.png', False)]})
        candidate = deck(self.directory / 'out.pptx', parts={'ppt/media/renamed.png': b'evidence',
                                                         'ppt/media/new.png': b'illustration'},
                         slide_rels={0: [('newRid', 'image', '../media/renamed.png', False),
                                         ('added', 'image', '../media/new.png', False)]})
        self.assertEqual(self.compare(original, candidate)[0].returncode, 0)
        deck(candidate, parts={'ppt/media/renamed.png': b'altered'},
             slide_rels={0: [('newRid', 'image', '../media/renamed.png', False)]})
        self.assertEqual(self.compare(original, candidate)[0].returncode, 1)

    def test_embedded_workbook_bytes_are_protected(self):
        original = deck(self.directory / 'in.pptx', parts={'ppt/embeddings/data.xlsx': b'original'},
                        slide_rels={0: [('data', 'package', '../embeddings/data.xlsx', False)]})
        candidate = deck(self.directory / 'out.pptx', parts={'ppt/embeddings/data.xlsx': b'changed'},
                         slide_rels={0: [('data', 'package', '../embeddings/data.xlsx', False)]})
        self.assertEqual(self.compare(original, candidate)[0].returncode, 1)

    def test_hyperlink_destination_change_fails(self):
        body = text_shape(extra='<a:endParaRPr><a:hlinkClick r:id="link"/></a:endParaRPr>')
        original = deck(self.directory / 'in.pptx', [slide(body)],
                        slide_rels={0: [('link', 'hyperlink', 'https://example.org/source', True)]})
        candidate = deck(self.directory / 'out.pptx', [slide(body)],
                         slide_rels={0: [('link', 'hyperlink', 'https://example.org/other', True)]})
        self.assertEqual(self.compare(original, candidate)[0].returncode, 1)

    def test_raster_only_snapshot_exposes_limitation(self):
        original = deck(self.directory / 'in.pptx', [slide('<p:pic/>')])
        output = self.directory / 'baseline.json'
        cli = self.run_cli('snapshot', original, '--output', output)
        self.assertEqual(cli.returncode, 0, cli.stderr)
        report = json.loads(output.read_text(encoding='utf-8'))
        self.assertEqual(report['slides'][0]['editability']['raster_only_candidate'], True)
        self.assertEqual(len(report['source']['sha256']), 64)

    def test_invalid_archive_or_baseline_is_an_error_not_pass(self):
        bad = self.directory / 'bad.pptx'
        bad.write_text('not a ZIP', encoding='utf-8')
        cli = self.run_cli('snapshot', bad, '--output', self.directory / 'out.json')
        self.assertEqual(cli.returncode, 2)
        original = deck(self.directory / 'in.pptx')
        baseline = self.directory / 'bad.json'
        baseline.write_text('{}', encoding='utf-8')
        cli = self.run_cli('compare', baseline, original, '--output', self.directory / 'check.json')
        self.assertEqual(cli.returncode, 2)

    def test_broken_relation_target_errors_and_input_cannot_be_overwritten(self):
        original = deck(self.directory / 'in.pptx',
                        slide_rels={0: [('image', 'image', '../media/missing.png', False)]})
        cli = self.run_cli('snapshot', original, '--output', self.directory / 'baseline.json')
        self.assertEqual(cli.returncode, 2)
        original_bytes = original.read_bytes()
        cli = self.run_cli('snapshot', original, '--output', original)
        self.assertEqual(cli.returncode, 2)
        self.assertEqual(original.read_bytes(), original_bytes)

    def test_same_asset_moved_to_other_slide_does_not_pass(self):
        bodies = [slide(text_shape('First')), slide(text_shape('Second'))]
        parts = {'ppt/media/image1.png': b'evidence'}
        rel = [('asset', 'image', '../media/image1.png', False)]
        original = deck(self.directory / 'in.pptx', bodies, parts, {0: rel})
        candidate = deck(self.directory / 'out.pptx', bodies, parts, {1: rel})
        self.assertEqual(self.compare(original, candidate)[0].returncode, 1)

    def test_slide_layout_text_is_protected(self):
        def write(path, title):
            layout = f'<p:sldLayout {NS}><p:cSld><p:spTree>{text_shape(title)}</p:spTree></p:cSld></p:sldLayout>'
            return deck(path, parts={'ppt/slideLayouts/slideLayout1.xml': layout},
                        slide_rels={0: [('layout', 'slideLayout', '../slideLayouts/slideLayout1.xml', False)]})
        original = write(self.directory / 'in.pptx', 'Original attribution')
        candidate = write(self.directory / 'out.pptx', 'Changed attribution')
        self.assertEqual(self.compare(original, candidate)[0].returncode, 1)

    def test_explicit_break_cannot_be_deleted(self):
        first = text_shape(extra='<a:br/><a:r><a:t>Second line</a:t></a:r>')
        second = text_shape('Original claimSecond line')
        original = deck(self.directory / 'in.pptx', [slide(first)])
        candidate = deck(self.directory / 'out.pptx', [slide(second)])
        self.assertEqual(self.compare(original, candidate)[0].returncode, 1)

    def test_source_file_changes_are_reported(self):
        original = deck(self.directory / 'in.pptx')
        baseline = self.directory / 'baseline.json'
        candidate = deck(self.directory / 'out.pptx')
        self.assertEqual(self.run_cli('snapshot', original, '--output', baseline).returncode, 0)
        deck(original, [slide(text_shape('Overwritten source'))])
        result = self.directory / 'result.json'
        cli = self.run_cli('compare', baseline, candidate, '--source', original, '--output', result)
        self.assertEqual(cli.returncode, 1)
        report = json.loads(result.read_text(encoding='utf-8'))
        self.assertTrue(any(item['check'] == 'source_hash' for item in report['differences']))

    def test_malformed_baseline_slide_returns_error_without_traceback(self):
        baseline = self.directory / 'baseline.json'
        baseline.write_text(json.dumps({'schema_version': 1, 'kind': 'pptx-content-baseline',
                                        'slides': [3]}), encoding='utf-8')
        original = deck(self.directory / 'in.pptx')
        cli = self.run_cli('compare', baseline, original, '--output', self.directory / 'check.json')
        self.assertEqual(cli.returncode, 2)
        self.assertNotIn('Traceback', cli.stderr)

    def test_compare_rejects_pptx_output_even_without_source_argument(self):
        original = deck(self.directory / 'in.pptx')
        candidate = deck(self.directory / 'out.pptx')
        baseline = self.directory / 'baseline.json'
        self.assertEqual(self.run_cli('snapshot', original, '--output', baseline).returncode, 0)
        before = original.read_bytes()
        cli = self.run_cli('compare', baseline, candidate, '--output', original)
        self.assertEqual(cli.returncode, 2)
        self.assertEqual(original.read_bytes(), before)

    def test_snapshot_rejects_hardlink_alias_of_known_input(self):
        original = deck(self.directory / 'in.pptx')
        alias = self.directory / 'alias.json'
        os.link(original, alias)
        before = original.read_bytes()
        cli = self.run_cli('snapshot', original, '--output', alias)
        self.assertEqual(cli.returncode, 2)
        self.assertEqual(original.read_bytes(), before)

    def test_atomic_report_replaces_unknown_hardlink_without_mutating_source(self):
        original = deck(self.directory / 'in.pptx')
        candidate = deck(self.directory / 'out.pptx')
        baseline = self.directory / 'baseline.json'
        self.assertEqual(self.run_cli('snapshot', original, '--output', baseline).returncode, 0)
        alias = self.directory / 'alias.json'
        os.link(original, alias)
        before = original.read_bytes()
        cli = self.run_cli('compare', baseline, candidate, '--output', alias)
        self.assertEqual(cli.returncode, 0, cli.stderr)
        self.assertEqual(original.read_bytes(), before)
        self.assertTrue(json.loads(alias.read_text(encoding='utf-8'))['passed'])

    def test_selected_layout_switch_is_detected_without_following_sibling_layouts(self):
        def write(path, selected, other_text='Layout B'):
            parts = {
                'ppt/slideLayouts/a.xml': f'<p:sldLayout {NS}>{text_shape("Layout A")}</p:sldLayout>',
                'ppt/slideLayouts/b.xml': f'<p:sldLayout {NS}>{text_shape(other_text)}</p:sldLayout>',
                'ppt/slideMasters/master.xml': f'<p:sldMaster {NS}>{text_shape("Master")}</p:sldMaster>',
                'ppt/slideLayouts/_rels/a.xml.rels': rels([('master', 'slideMaster', '../slideMasters/master.xml', False)]),
                'ppt/slideLayouts/_rels/b.xml.rels': rels([('master', 'slideMaster', '../slideMasters/master.xml', False)]),
                'ppt/slideMasters/_rels/master.xml.rels': rels([
                    ('a', 'slideLayout', '../slideLayouts/a.xml', False),
                    ('b', 'slideLayout', '../slideLayouts/b.xml', False)]),
            }
            return deck(path, parts=parts, slide_rels={0: [('layout', 'slideLayout', f'../slideLayouts/{selected}.xml', False)]})
        original = write(self.directory / 'in.pptx', 'a')
        candidate = write(self.directory / 'out.pptx', 'b')
        cli, report = self.compare(original, candidate)
        self.assertEqual(cli.returncode, 1)
        self.assertTrue(any(item['check'] == 'inherited_text' for item in report['differences']))
        write(candidate, 'a', other_text='Unused layout modified')
        self.assertEqual(self.compare(original, candidate)[0].returncode, 0)

    def test_hyperlinks_are_bound_to_anchors_but_identical_linked_run_splits_pass(self):
        def body(items):
            content = ''.join(f'<a:r><a:rPr><a:hlinkClick r:id="{rid}"/></a:rPr><a:t>{text}</a:t></a:r>'
                              for text, rid in items)
            return '<p:sp><p:txBody><a:p>' + content + '</a:p></p:txBody></p:sp>'
        relationships = {0: [('one', 'hyperlink', 'https://example.org/one', True),
                             ('two', 'hyperlink', 'https://example.org/two', True)]}
        original = deck(self.directory / 'in.pptx', [slide(body([('Alpha', 'one'), ('Beta', 'two')]))],
                        slide_rels=relationships)
        candidate = deck(self.directory / 'out.pptx', [slide(body([('Alpha', 'two'), ('Beta', 'one')]))],
                         slide_rels=relationships)
        cli, report = self.compare(original, candidate)
        self.assertEqual(cli.returncode, 1)
        self.assertTrue(any(item['check'] == 'hyperlinks' for item in report['differences']))
        deck(candidate, [slide(body([('Al', 'one'), ('pha', 'one'), ('Beta', 'two')]))], slide_rels=relationships)
        self.assertEqual(self.compare(original, candidate)[0].returncode, 0)


if __name__ == '__main__':
    unittest.main()
