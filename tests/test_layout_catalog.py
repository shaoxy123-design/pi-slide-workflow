"""Read-only reference-layout behavior; fixtures are minimal OOXML, not renders."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from test_pptx_guard import deck, slide, text_shape, NS

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import layout_catalog


def fixture(path, text='Original', grouped=False, width=12000000):
    xfrm = '<a:xfrm><a:off x="1000000" y="1000000"/><a:ext cx="9000000" cy="2000000"/></a:xfrm>'
    shape = text_shape(text, style=xfrm)
    if grouped:
        shape = '<p:grpSp>' + shape + '</p:grpSp>'
    presentation = (f'<p:presentation {NS}><p:sldIdLst>'
                    '<p:sldId id="256" r:id="rId1"/></p:sldIdLst>'
                    f'<p:sldSz cx="{width}" cy="6750000"/></p:presentation>')
    return deck(path, [slide(shape)], parts={'ppt/presentation.xml': presentation})


class LayoutCatalogTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def test_extract_normalizes_geometry_preserves_source_and_omits_text(self):
        source = fixture(self.root / 'source.pptx', 'Private lesson wording')
        before = source.read_bytes()
        result = layout_catalog.extract(source)
        self.assertEqual(source.read_bytes(), before)
        slot = result['layouts'][0]['slots'][0]
        self.assertEqual(slot['source_shape_id'], '2')
        self.assertAlmostEqual(slot['box'][0], 1/12)
        self.assertEqual(slot['text_characters'], len('Private lesson wording'))
        self.assertNotIn('Private lesson wording', str(result))
        self.assertEqual(result['approval'], 'not_recorded')

    def test_similar_reference_suggested_but_not_automatically_applied(self):
        source = fixture(self.root / 'source.pptx')
        ref = fixture(self.root / 'ref.pptx', 'A similar amount')
        result = layout_catalog.suggest(source, layout_catalog.extract(ref))
        self.assertEqual(len(result['slides'][0]['suggestions']), 1)
        self.assertTrue(result['manual_fit_review_required'])
        self.assertEqual(result['action'], 'advisory_only')

    def test_missing_required_slots_and_aspect_mismatch_excluded(self):
        source = fixture(self.root / 'source.pptx')
        ref = fixture(self.root / 'ref.pptx', width=9000000)
        self.assertEqual(layout_catalog.suggest(source, layout_catalog.extract(ref))['slides'][0]['suggestions'], [])
        catalog = layout_catalog.extract(source)
        catalog['layouts'][0]['slots'] = []
        self.assertEqual(layout_catalog.suggest(source, catalog)['slides'][0]['suggestions'], [])

    def test_groups_are_marked_for_manual_handling_not_flattened(self):
        source = fixture(self.root / 'source.pptx', grouped=True)
        entry = layout_catalog.extract(source)['layouts'][0]
        self.assertFalse(entry['eligible_for_matching'])
        self.assertIn('group', ' '.join(entry['limitations']).lower())

    def test_bad_slide_selection_and_missing_slide_dimensions_rejected(self):
        source = fixture(self.root / 'source.pptx')
        with self.assertRaises(ValueError):
            layout_catalog.extract(source, [2])
        invalid = deck(self.root / 'invalid.pptx')
        with self.assertRaises(ValueError):
            layout_catalog.extract(invalid)

    def test_json_output_cannot_overwrite_any_existing_file(self):
        target = self.root / 'source.json'
        target.write_text('Original', encoding='utf-8')
        with self.assertRaises(FileExistsError):
            layout_catalog.write_new_json(target, {})
        self.assertEqual(target.read_text(), 'Original')
        with self.assertRaises(ValueError):
            layout_catalog.write_new_json(self.root / 'source.pptx', {})


if __name__ == '__main__':
    unittest.main()
