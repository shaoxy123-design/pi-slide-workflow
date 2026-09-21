#!/usr/bin/env python3
"""Read-only content checks for transitional OOXML PowerPoint .pptx files.

Standard library only. Exit 0: snapshot written / covered comparisons passed;
1: protected differences found; 2: invalid input or operation error. A pass is
never a visual-quality or editability certification. See JSON limitations.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import posixpath
import sys
import tempfile
from urllib.parse import unquote
import xml.etree.ElementTree as ET
import zipfile


VERSION = 1
NS = {
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'c': 'http://schemas.openxmlformats.org/drawingml/2006/chart',
    'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math',
}
REL_NS = 'http://schemas.openxmlformats.org/package/2006/relationships'
LIMITATIONS = [
    'A pass covers only the recorded OOXML comparisons. Visual and manual editability reviews are always required.',
    'No rendering or OCR: text inside images, illustration meaning, crops, occlusion, clipping, reading order, and on-slide visibility are not validated.',
    'Text run splits and shape ordering are ignored; exact paragraph strings, line breaks, and paragraph order within each text body are protected. Splitting or merging text bodies is conservatively flagged.',
    'Slide order uses stable presentation slide IDs; a tool that regenerates IDs is conservatively flagged even if the visible order is unchanged.',
    'Chart XML ignores a small set of style nodes; remaining chart structure/data are protected conservatively. Unsupported chart formats and SmartArt data are hashed as evidence, not semantically understood.',
    'Original linked images, media, OLE objects, and embedded workbooks use byte hashes. Re-encoding identical images or resaving workbooks can be flagged; external destinations are recorded but never fetched.',
    'Relationships and minimum object counts cannot prove an original asset remains visible, useful, or editable; orphaned relationships and hidden/off-canvas objects require visual/manual review.',
    'Raster-only detection is a structural heuristic. Source raster slides remain raster unless separately reconstructed and manually validated.',
    'Animations, transitions, comments, accessibility metadata, geometry-only diagrams, macros, and all application-specific extensions are not fully compared. Only transitional OOXML .pptx input is supported.',
    'Notes slide-number placeholders are excluded; slide layout/master text is recorded conservatively, including text that may not render. Dynamic fields are checked by cached text only.',
    'Original-source integrity is verified only when compare receives --source; recorded baseline paths are never followed automatically. The baseline JSON itself must be kept unchanged.',
    'Hyperlinks are bound to their owning object and paragraph character spans; adjacent identically linked runs are coalesced. Regenerating linked object IDs may be conservatively flagged.',
]


class GuardError(ValueError):
    """An input cannot support a trustworthy comparison."""


def digest(data):
    return hashlib.sha256(data).hexdigest()


def stable(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'))


def local(tag):
    return tag.rsplit('}', 1)[-1]


def q(prefix, name):
    return '{' + NS[prefix] + '}' + name


def paragraphs(body):
    """Coalesce run fragments without losing whitespace or explicit breaks."""
    result = []
    for paragraph in body.findall('a:p', NS):
        pieces = []
        for node in paragraph.iter():
            if node.tag == q('a', 't'):
                pieces.append(node.text or '')
            elif node.tag == q('a', 'br'):
                pieces.append('\n')
        result.append(''.join(pieces))
    return result


def text_blocks(root, notes=False):
    blocks = []
    for shape in root.iter(q('p', 'sp')):
        if notes and any(ph.get('type') == 'sldNum' for ph in shape.iter(q('p', 'ph'))):
            continue
        for body in shape.findall('p:txBody', NS):
            block = paragraphs(body)
            if any(block):
                blocks.append(block)
    return sorted(blocks, key=stable)


def tables(root):
    return sorted([
        [[paragraphs(cell.find('a:txBody', NS)) if cell.find('a:txBody', NS) is not None else []
          for cell in row.findall('a:tc', NS)]
         for row in table.findall('a:tr', NS)]
        for table in root.iter(q('a', 'tbl'))
    ], key=stable)


STYLE_NODES = {'spPr', 'txPr', 'rPr', 'defRPr', 'endParaRPr', 'pPr', 'ctrlPr',
               'style', 'layout', 'clrMapOvr'}


def semantic_xml(node):
    """Conservative XML tree fingerprint, omitting known formatting subtrees."""
    if local(node.tag) in STYLE_NODES:
        return None
    attrs = sorted((key, val) for key, val in node.attrib.items()
                   if not key.startswith('{' + NS['r'] + '}'))
    value = node.text or ''
    if not value.strip() and local(node.tag) not in {'t', 'v', 'f'}:
        value = ''
    children = [child for item in node for child in [semantic_xml(item)] if child is not None]
    return [node.tag, attrs, value, children]


def maths(root):
    return sorted(digest(stable(semantic_xml(node)).encode('utf-8'))
                  for node in root.iter(q('m', 'oMath')))


def inventory(root):
    tags = Counter(node.tag for node in root.iter())
    counts = {
        'native_shapes': tags[q('p', 'sp')],
        'pictures': tags[q('p', 'pic')],
        'groups': tags[q('p', 'grpSp')],
        'connectors': tags[q('p', 'cxnSp')],
        'tables': tags[q('a', 'tbl')],
        'charts': tags[q('c', 'chart')],
        'equations': tags[q('m', 'oMath')],
        'ole_objects': tags[q('p', 'oleObj')],
        'text_bodies': len(text_blocks(root)),
    }
    return {
        'counts': counts,
        'raster_only_candidate': bool(counts['pictures'] and not any(
            counts[key] for key in ('native_shapes', 'tables', 'charts', 'equations', 'ole_objects'))),
        'manual_review_required': True,
    }


def bound_hyperlinks(root, relations, part):
    """Record destinations with text/object anchors, independent of run splits."""
    parents = {child: parent for parent in root.iter() for child in parent}
    handled, records = set(), []

    def owner_context(node):
        current = node
        while current is not None:
            if current.tag in {q('p', name) for name in ('sp', 'pic', 'graphicFrame', 'cxnSp')}:
                props = next(current.iter(q('p', 'cNvPr')), None)
                return {'type': local(current.tag), 'id': props.get('id') if props is not None else None,
                        'text': text_blocks(current)}
            current = parents.get(current)
        return {'type': local(root.tag)}

    def descriptor(node):
        rid = node.get(q('r', 'id'))
        target = relations.get(rid, {}).get('target')
        if rid and target is None:
            raise GuardError(f'Unresolved hyperlink {rid} in {part}.')
        return {'type': local(node.tag), 'target': target,
                'action': node.get('action'), 'tooltip': node.get('tooltip')}

    for paragraph in root.iter(q('a', 'p')):
        body = parents.get(paragraph)
        body_paragraphs = body.findall('a:p', NS) if body is not None else [paragraph]
        context = {'owner': owner_context(paragraph),
                   'body_text': paragraphs(body) if body is not None else [],
                   'paragraph_index': body_paragraphs.index(paragraph)}
        cursor, segments = 0, []
        for item in paragraph:
            length = (1 if item.tag == q('a', 'br') else
                      sum(len(node.text or '') for node in item.iter(q('a', 't'))))
            for link in item.iter():
                if local(link.tag) not in {'hlinkClick', 'hlinkMouseOver'}:
                    continue
                handled.add(link)
                segments.append({'anchor': context, **descriptor(link),
                                 'scope': 'text' if local(item.tag) in {'r', 'fld', 'br'} else local(item.tag),
                                 'start': cursor, 'end': cursor + length})
            cursor += length
        # Group per destination/type first so click + hover links can both merge.
        grouped = {}
        for segment in segments:
            key = stable({key: val for key, val in segment.items() if key not in {'start', 'end'}})
            ranges = grouped.setdefault(key, [])
            if ranges and ranges[-1]['end'] == segment['start'] and segment['scope'] == 'text':
                ranges[-1]['end'] = segment['end']
            else:
                ranges.append(segment)
        records.extend(segment for ranges in grouped.values() for segment in ranges)
    for node in root.iter():
        if local(node.tag) in {'hlinkClick', 'hlinkMouseOver'} and node not in handled:
            records.append({'anchor': owner_context(node), 'scope': 'object', **descriptor(node)})
    return sorted(records, key=stable)


class Package:
    def __init__(self, path):
        self.path = Path(path)
        if self.path.suffix.lower() != '.pptx':
            raise GuardError('Only .pptx input is supported (convert .ppt/.pptm explicitly first).')
        self.archive = zipfile.ZipFile(self.path)
        names = self.archive.namelist()
        if len(names) != len(set(names)):
            self.archive.close()
            raise GuardError('Duplicate ZIP member names make the package ambiguous.')
        self.names = set(names)
        self.roots = {}
        self.relations = {}

    def xml(self, part):
        if part not in self.roots:
            self.roots[part] = ET.fromstring(self.archive.read(part))
        return self.roots[part]

    def rels(self, part):
        if part in self.relations:
            return self.relations[part]
        name = posixpath.join(posixpath.dirname(part), '_rels', posixpath.basename(part) + '.rels')
        result = {}
        if name in self.names:
            for node in self.xml(name).findall('{' + REL_NS + '}Relationship'):
                rid, target = node.get('Id'), node.get('Target')
                if not rid or target is None or rid in result:
                    raise GuardError(f'Invalid or duplicate relationship in {name}.')
                external = node.get('TargetMode') == 'External'
                if not external:
                    decoded = unquote(target).split('#', 1)[0]
                    target = posixpath.normpath(decoded.lstrip('/') if decoded.startswith('/')
                                               else posixpath.join(posixpath.dirname(part), decoded))
                    if target.startswith('../') or target not in self.names:
                        raise GuardError(f'Missing or invalid relationship target from {part}: {target}')
                result[rid] = {'kind': node.get('Type', '').rsplit('/', 1)[-1],
                               'target': target, 'external': external}
        self.relations[part] = result
        return result

    def graph_evidence(self, start):
        pending, seen, assets, inherited, notes, links = [start], set(), [], [], [], []
        protected_binary = {'image', 'audio', 'video', 'media', 'oleObject', 'package'}
        while pending:
            part = pending.pop()
            if part in seen:
                continue
            seen.add(part)
            root = self.xml(part) if part.endswith('.xml') else None
            relations = self.rels(part)
            if root is not None:
                if root.tag == q('p', 'notes'):
                    notes.extend(text_blocks(root, notes=True))
                if root.tag in {q('p', 'sldLayout'), q('p', 'sldMaster')}:
                    inherited.extend(text_blocks(root))
                links.extend(bound_hyperlinks(root, relations, part))
            for relation in relations.values():
                kind, target = relation['kind'], relation['target']
                if relation['external']:
                    if kind != 'hyperlink':
                        assets.append({'kind': 'external:' + kind, 'sha256': digest(target.encode('utf-8')),
                                       'part': target})
                    continue
                if kind in {'slide', 'notesMaster'}:
                    continue  # Do not follow notes back-references into unrelated slides.
                if kind == 'slideLayout' and root is not None and root.tag == q('p', 'sldMaster'):
                    continue  # Master layout lists are back-references, not active inheritance.
                if kind in protected_binary or target.startswith(('ppt/media/', 'ppt/embeddings/')):
                    assets.append({'kind': kind, 'sha256': digest(self.archive.read(target)), 'part': target})
                elif kind == 'chart':
                    value = stable(semantic_xml(self.xml(target))).encode('utf-8')
                    assets.append({'kind': 'chart', 'sha256': digest(value), 'part': target})
                elif kind.startswith('diagram') or kind in {'chartEx', 'chartUserShapes'}:
                    assets.append({'kind': kind, 'sha256': digest(self.archive.read(target)), 'part': target})
                pending.append(target)
        return {'assets': assets, 'notes_text': sorted(notes, key=stable),
                'inherited_text': sorted(inherited, key=stable), 'hyperlinks': sorted(links, key=stable)}


def snapshot(path):
    package = Package(path)
    try:
        presentation = package.xml('ppt/presentation.xml')
        if presentation.tag != q('p', 'presentation'):
            raise GuardError('Unsupported presentation namespace; transitional OOXML is required.')
        relations = package.rels('ppt/presentation.xml')
        slides = []
        for index, item in enumerate(presentation.findall('p:sldIdLst/p:sldId', NS), 1):
            relation = relations.get(item.get(q('r', 'id')))
            if not relation or relation['kind'] != 'slide' or relation['external']:
                raise GuardError(f'Cannot resolve logical slide {index}.')
            part = relation['target']
            root = package.xml(part)
            if root.tag != q('p', 'sld'):
                raise GuardError(f'Invalid slide XML: {part}')
            slides.append({'index': index, 'slide_id': item.get('id'), 'part': part,
                           'hidden': root.get('show', '1').lower() in {'0', 'false'},
                           'text': text_blocks(root), 'tables': tables(root), 'math': maths(root),
                           'editability': inventory(root), **package.graph_evidence(part)})
        if not slides:
            raise GuardError('The presentation has no readable slides.')
        ids = [slide['slide_id'] for slide in slides]
        if None in ids or len(ids) != len(set(ids)):
            raise GuardError('Missing or duplicate presentation slide IDs.')
        return {'schema_version': VERSION, 'kind': 'pptx-content-baseline',
                'created_utc': datetime.now(timezone.utc).isoformat(),
                'source': {'path': str(Path(path).resolve()), 'sha256': digest(Path(path).read_bytes())},
                'slide_count': len(slides), 'slides': slides, 'limitations': LIMITATIONS}
    finally:
        package.archive.close()


def asset_counts(slide):
    return Counter((item['kind'], item['sha256']) for item in slide['assets'])


def compare(baseline, candidate, source=None):
    if baseline.get('schema_version') != VERSION or baseline.get('kind') != 'pptx-content-baseline':
        raise GuardError('Unrecognized baseline schema; create a new snapshot with this tool.')
    if not isinstance(baseline.get('slides'), list) or not baseline['slides']:
        raise GuardError('Baseline must contain recorded slides.')
    current = snapshot(candidate)
    differences, additions = [], []

    def changed(check, before, after, slide=None):
        if before != after:
            differences.append({'slide': slide, 'check': check, 'before': before, 'after': after})

    source_integrity = 'not_verified'
    if source is not None:
        current_hash = digest(Path(source).read_bytes())
        changed('source_hash', baseline['source']['sha256'], current_hash)
        source_integrity = 'passed' if current_hash == baseline['source']['sha256'] else 'failed'
    changed('slide_count', len(baseline['slides']), len(current['slides']))
    changed('slide_order', [s['slide_id'] for s in baseline['slides']],
            [s['slide_id'] for s in current['slides']])
    for old, new in zip(baseline['slides'], current['slides']):
        index = new['index']
        for key in ('hidden', 'text', 'tables', 'math', 'notes_text', 'inherited_text', 'hyperlinks'):
            changed(key, old[key], new[key], index)
        before, after = asset_counts(old), asset_counts(new)
        for (kind, sha), count in (before - after).items():
            differences.append({'slide': index, 'check': 'retained_asset', 'kind': kind,
                                'missing_sha256': sha, 'missing_count': count})
        for (kind, sha), count in (after - before).items():
            item = {'slide': index, 'check': 'added_asset', 'kind': kind, 'sha256': sha, 'count': count}
            additions.append(item)
            if kind != 'image':
                differences.append(item)
        for kind in ('pictures', 'tables', 'charts', 'equations', 'ole_objects', 'text_bodies'):
            a, b = old['editability']['counts'][kind], new['editability']['counts'][kind]
            if b < a:
                differences.append({'slide': index, 'check': 'object_loss', 'kind': kind,
                                    'before': a, 'after': b})
    return {'schema_version': VERSION, 'kind': 'pptx-content-comparison',
            'passed': not differences, 'baseline_source': baseline['source'],
            'source_integrity': source_integrity,
            'candidate_source': current['source'], 'differences': differences,
            'added_assets': additions, 'visual_review': 'required', 'editability_review': 'required',
            'candidate_editability': [{'slide': s['index'], **s['editability']} for s in current['slides']],
            'limitations': LIMITATIONS}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    snap = commands.add_parser('snapshot', help='Inventory the untouched source before edits')
    snap.add_argument('input', type=Path)
    snap.add_argument('--output', type=Path, required=True)
    check = commands.add_parser('compare', help='Compare candidate with the original snapshot')
    check.add_argument('baseline', type=Path)
    check.add_argument('candidate', type=Path)
    check.add_argument('--source', type=Path, help='Also verify the untouched original file against its recorded SHA-256')
    check.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.output.suffix.lower() != '.json':
            raise GuardError('Report output must use a .json extension; PowerPoint files are never output targets.')
        inputs = [args.input] if args.command == 'snapshot' else [args.baseline, args.candidate]
        if args.command == 'compare' and args.source:
            inputs.append(args.source)
        if any(args.output.resolve() == path.resolve()
               or (args.output.exists() and path.exists() and args.output.samefile(path)) for path in inputs):
            raise GuardError('Output must not overwrite an input file.')
        if args.command == 'snapshot':
            result = snapshot(args.input)
        else:
            baseline = json.loads(args.baseline.read_text(encoding='utf-8-sig'))
            if not isinstance(baseline, dict):
                raise GuardError('Baseline must be a JSON object.')
            result = compare(baseline, args.candidate, args.source)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', newline='\n',
                                             dir=args.output.parent, prefix='.pptx-guard-',
                                             suffix='.tmp', delete=False) as stream:
                temporary = Path(stream.name)
                json.dump(result, stream, indent=2, ensure_ascii=False)
                stream.write('\n')
            # Replacing the directory entry never mutates the contents of a linked file.
            os.replace(temporary, args.output)
        finally:
            if temporary is not None and temporary.exists():
                temporary.unlink()
        print(f"{args.command}: {'differences found' if result.get('passed') is False else 'written'} -> {args.output}")
        return 1 if result.get('passed') is False else 0
    except (OSError, ValueError, KeyError, TypeError, ET.ParseError, zipfile.BadZipFile) as exc:
        print(f'pptx_guard: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
