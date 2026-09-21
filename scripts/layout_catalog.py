#!/usr/bin/env python3
"""Extract/cache reference layouts and suggest compatible ones. Never edits decks."""
import argparse
from collections import Counter
import json
import math
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import zipfile

from pptx_guard import Package, NS, q, snapshot


def slot_kind(shape):
    if any(True for _ in shape.iter(q('m', 'oMath'))):
        return 'equation'
    if shape.find('.//a:tbl', NS) is not None:
        return 'table'
    if shape.find('.//c:chart', NS) is not None:
        return 'chart'
    if shape.tag == q('p', 'pic'):
        return 'image'
    if shape.find('p:txBody', NS) is not None:
        return 'text'
    return 'shape'


def extract(source, selected_slides=None):
    """Catalog source geometry, types and capacity hints without copying wording."""
    baseline = snapshot(source)
    package = Package(source)
    try:
        size = package.xml('ppt/presentation.xml').find('p:sldSz', NS)
        if size is None:
            raise ValueError('Source has no explicit slide dimensions.')
        width, height = int(size.get('cx', '0')), int(size.get('cy', '0'))
        if width <= 0 or height <= 0:
            raise ValueError('Invalid slide dimensions.')
        selected = selected_slides if selected_slides is not None else list(range(1, baseline['slide_count'] + 1))
        if not selected or any(type(i) is not int or not 1 <= i <= baseline['slide_count'] for i in selected):
            raise ValueError('Select existing one-based slide numbers.')
        if len(set(selected)) != len(selected):
            raise ValueError('Slide selection must not contain duplicates.')
        entries = []
        for slide_info in baseline['slides']:
            if slide_info['index'] not in selected:
                continue
            root = package.xml(slide_info['part'])
            tree = root.find('p:cSld/p:spTree', NS)
            slots, limitations = [], []
            if tree is None:
                raise ValueError('Missing slide shape tree.')
            for shape in tree:
                if shape.tag in {q('p', 'nvGrpSpPr'), q('p', 'grpSpPr'), q('p', 'extLst')}:
                    continue
                if shape.tag == q('p', 'grpSp'):
                    limitations.append('Group coordinates require manual handling; no flattening performed.')
                    continue
                props = shape.find('.//p:cNvPr', NS)
                transform = shape.find('p:spPr/a:xfrm', NS)
                if transform is None:
                    transform = shape.find('p:xfrm', NS)
                if props is None or transform is None:
                    limitations.append('An object has inherited or unsupported geometry.')
                    continue
                off, ext = transform.find('a:off', NS), transform.find('a:ext', NS)
                if off is None or ext is None:
                    limitations.append('An object has incomplete geometry.')
                    continue
                box = [int(off.get('x', '0')) / width, int(off.get('y', '0')) / height,
                       int(ext.get('cx', '0')) / width, int(ext.get('cy', '0')) / height]
                if (box[0] < 0 or box[1] < 0 or min(box[2:]) <= 0
                        or box[0] + box[2] > 1.000001 or box[1] + box[3] > 1.000001
                        or transform.get('rot', '0') != '0'):
                    limitations.append('An object is rotated, empty or outside the slide bounds.')
                slots.append({'source_shape_id': props.get('id'), 'kind': slot_kind(shape),
                              'box': box, 'text_characters': sum(len(n.text or '') for n in shape.iter(q('a', 't')))})
            if slide_info['hidden']:
                limitations.append('Hidden source slide; exclude from automatic reference suggestions.')
            entries.append({'id': f"{baseline['source']['sha256'][:12]}:slide:{slide_info['slide_id']}",
                            'slide': slide_info['index'], 'source_slide_id': slide_info['slide_id'],
                            'aspect_ratio': width / height, 'slots': slots,
                            'eligible_for_matching': not limitations and bool(slots),
                            'limitations': sorted(set(limitations))})
        return {'version': 1, 'kind': 'reference-layout-catalog', 'source': baseline['source'],
                'approval': 'not_recorded', 'layouts': entries,
                'limitations': ['Geometry is advisory, not a content schema or proof of visual fit.',
                                'Original wording, images and chart data are not copied into this catalog.',
                                'Source OOXML shape IDs are not backend object IDs. Resolve backend IDs separately.',
                                'Inherited/grouped geometry is excluded from automatic matching.']}
    finally:
        package.archive.close()


def suggest(source, catalog, limit=3):
    if not isinstance(catalog, dict) or catalog.get('kind') != 'reference-layout-catalog' or catalog.get('version') != 1:
        raise ValueError('Expected a version 1 reference-layout-catalog.')
    references = catalog.get('layouts')
    if not isinstance(references, list) or not 1 <= limit <= 10:
        raise ValueError('Invalid layout list or suggestion limit.')
    for ref in references:
        if not isinstance(ref, dict) or not isinstance(ref.get('slots'), list):
            raise ValueError('Malformed reference layout.')
        ratio = ref.get('aspect_ratio')
        if type(ratio) not in (int, float) or not math.isfinite(ratio) or ratio <= 0:
            raise ValueError('Invalid reference aspect ratio.')
        for slot in ref['slots']:
            if (slot.get('kind') not in {'text', 'table', 'chart', 'image', 'equation', 'shape'}
                    or type(slot.get('text_characters')) is not int or slot['text_characters'] < 0):
                raise ValueError('Invalid slot type or text capacity.')
    target = extract(source)
    result = []
    for entry in target['layouts']:
        candidates = []
        if entry['eligible_for_matching']:
            profile = Counter(s['kind'] for s in entry['slots'])
            chars = sum(s['text_characters'] for s in entry['slots'])
            for ref in references:
                if not ref.get('eligible_for_matching') or abs(entry['aspect_ratio'] - ref['aspect_ratio']) > .01:
                    continue
                ref_profile = Counter(s['kind'] for s in ref['slots'])
                if any(ref_profile[kind] < count for kind, count in profile.items()):
                    continue
                ref_chars = sum(s['text_characters'] for s in ref['slots'])
                # Structural similarity and source text amount are hints, never a fit guarantee.
                penalty = sum(abs(profile[k] - ref_profile[k]) for k in set(profile) | set(ref_profile))
                penalty += abs(chars - ref_chars) / max(chars, ref_chars, 1)
                candidates.append({'layout_id': ref['id'], 'reference_slide': ref['slide'],
                                   'distance': round(penalty, 4),
                                   'reason': 'Compatible aspect ratio and enough same-type object slots; inspect actual fit.'})
        candidates.sort(key=lambda c: (c['distance'], c['layout_id']))
        result.append({'slide': entry['slide'], 'source_slide_id': entry['source_slide_id'],
                       'suggestions': candidates[:limit], 'limitations': entry['limitations']})
    return {'version': 1, 'source': target['source'], 'reference_source': catalog.get('source'),
            'action': 'advisory_only', 'manual_fit_review_required': True, 'slides': result}


def write_new_json(output, data):
    output = Path(output)
    if output.suffix.lower() != '.json':
        raise ValueError('Output must be a new .json file.')
    payload = json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + '\n'
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x', encoding='utf-8') as stream:
        stream.write(payload)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    build = commands.add_parser('extract')
    build.add_argument('source', type=Path)
    build.add_argument('--slides', help='Comma-separated one-based slide numbers; otherwise all')
    build.add_argument('--output', type=Path, required=True)
    match = commands.add_parser('suggest')
    match.add_argument('source', type=Path)
    match.add_argument('--catalog', type=Path, required=True)
    match.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == 'extract':
            selected = [int(s) for s in args.slides.split(',')] if args.slides else None
            result = extract(args.source, selected)
        else:
            result = suggest(args.source, json.loads(args.catalog.read_text(encoding='utf-8-sig')))
        write_new_json(args.output, result)
        print(f'{args.command}: wrote {args.output}; advisory only')
        return 0
    except (OSError, ValueError, KeyError, TypeError, AttributeError, ET.ParseError, zipfile.BadZipFile) as error:
        print(f'layout_catalog: {error}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
