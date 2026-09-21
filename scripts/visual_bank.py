"""Read-only, advisory topic search and file checks for the local visual bank."""
import argparse
import hashlib
import json
from pathlib import Path
import re

DEFAULT_CATALOG = Path(__file__).resolve().parents[1] / 'visual-bank/catalog.json'


def parse_catalog(text):
    data = json.loads(text)
    if data.get('schema_version') != 1 or not isinstance(data.get('entries'), list):
        raise ValueError('Expected schema_version 1 and an entries list')
    return data


def load_catalog(path):
    return parse_catalog(Path(path).read_text(encoding='utf-8-sig'))


def words(text):
    return set(re.findall(r'\w+', text.lower(), flags=re.UNICODE))


def search(entries, query, block_type=None, representation=None, limit=5):
    tokens = words(query)
    matches = []
    for entry in entries:
        if block_type and block_type not in entry.get('block_types', []):
            continue
        if representation and representation != entry.get('representation'):
            continue
        score = sum(weight * len(tokens & words(value)) for weight, value in [
            (5, ' '.join(entry.get('topics', []))),
            (4, entry.get('title', '')),
            (3, ' '.join(entry.get('block_types', []))),
            (1, entry.get('semantic_use', '')),
        ])
        if score:
            matches.append({'score': score, **entry})
    return sorted(matches, key=lambda item: (-item['score'], item['id']))[:limit]


def batch_search(entries, payload, limit=3):
    """Return advisory shortlists without dropping blocks or granting approval."""
    if type(limit) is not int or limit < 1:
        raise ValueError('--limit must be a positive integer')
    if not isinstance(payload, dict) or set(payload) != {'schema_version', 'blocks'}:
        raise ValueError('Batch input requires exactly schema_version and blocks')
    if type(payload['schema_version']) is not int or payload['schema_version'] != 1:
        raise ValueError('Batch schema_version must be integer 1')
    blocks = payload['blocks']
    if not isinstance(blocks, list) or not blocks:
        raise ValueError('Batch blocks must be a nonempty list')
    ids = set()
    for block in blocks:
        if not isinstance(block, dict) or not {'id', 'query'} <= set(block) or set(block) - {'id', 'query', 'block_type'}:
            raise ValueError('Each block requires id and query; only block_type is optional')
        for field in block:
            if not isinstance(block[field], str) or not block[field].strip():
                raise ValueError(f'Block {field} must be a nonempty string')
        if block['id'] in ids:
            raise ValueError('Block IDs must be unique')
        ids.add(block['id'])

    fields = ('id', 'title', 'score', 'semantic_use', 'avoid_when', 'representation', 'selection_unit')
    results = []
    for block in blocks:
        matches = search(entries, block['query'], block_type=block.get('block_type'), limit=limit)
        item = {**block, 'status': 'match' if matches else 'no_match',
                'candidates': [{field: match.get(field) for field in fields} for match in matches]}
        if not matches:
            item['planner_action'] = 'Review this block; its required visual task remains pending.'
        results.append(item)
    return {'advisory_only': True, 'method': 'local_lexical_search',
            'score_kind': 'lexical_rank_not_confidence', 'results': results}


def batch_catalog(path, payload, limit=3):
    # Hash the exact bytes searched, with one catalog read for the entire batch.
    raw = Path(path).read_bytes()
    catalog = parse_catalog(raw.decode('utf-8-sig'))
    result = batch_search(catalog['entries'], payload, limit)
    result['catalog_sha256'] = hashlib.sha256(raw).hexdigest()
    return result


def validate(path):
    path = Path(path).resolve()
    data = load_catalog(path)
    errors, ids = [], set()

    def check_file(relative, label):
        if not isinstance(relative, str) or not relative:
            errors.append(f'{label}: missing relative file path')
            return None
        target = (path.parent / relative).resolve()
        if Path(relative).is_absolute() or not target.is_relative_to(path.parent):
            errors.append(f'{label}: path must stay inside the visual bank')
            return None
        if not target.is_file():
            errors.append(f'{label}: file missing: {relative}')
            return None
        return target

    def check_hash(target, expected, label):
        if expected is None:
            return
        if not isinstance(expected, str) or not re.fullmatch('[0-9a-fA-F]{64}', expected):
            errors.append(f'{label}: invalid SHA-256')
        elif target and hashlib.sha256(target.read_bytes()).hexdigest() != expected.lower():
            errors.append(f'{label}: SHA-256 mismatch')

    for entry in data['entries']:
        ident = entry.get('id')
        if not isinstance(ident, str) or not ident or ident in ids:
            errors.append(f'Invalid or duplicate entry ID: {ident}')
        ids.add(ident)
        for field in ['title', 'semantic_use', 'avoid_when', 'representation', 'provenance']:
            if not entry.get(field):
                errors.append(f'{ident}: missing {field}')
        for field in ['topics', 'block_types']:
            if not isinstance(entry.get(field), list) or not entry[field] or not all(isinstance(x, str) and x for x in entry[field]):
                errors.append(f'{ident}: {field} must be a nonempty string list')
        preview = check_file(entry.get('preview'), f'{ident}.preview')
        check_hash(preview, entry.get('preview_sha256'), f'{ident}.preview')
        kind = entry.get('representation')
        if kind == 'native_components':
            if entry.get('selection_unit') != 'native_group':
                errors.append(f'{ident}: native topic visual must be delivered as one native_group')
            recipe = entry.get('recipe') or {}
            module = check_file(recipe.get('module'), f'{ident}.recipe.module')
            check_hash(module, recipe.get('module_sha256'), f'{ident}.recipe.module')
            if recipe.get('post_export'):
                post_export = recipe['post_export']
                helper = check_file(post_export.get('module'), f'{ident}.recipe.post_export.module')
                check_hash(helper, post_export.get('module_sha256'), f'{ident}.recipe.post_export.module')
            if not recipe.get('export') or not recipe.get('id'):
                errors.append(f'{ident}: missing recipe export or ID')
        elif kind == 'replaceable_raster_image':
            if entry.get('selection_unit') != 'picture':
                errors.append(f'{ident}: artwork must be delivered as one picture')
            asset = entry.get('asset') or {}
            target = check_file(asset.get('path'), f'{ident}.asset.path')
            expected = asset.get('sha256')
            if not isinstance(expected, str) or not re.fullmatch('[0-9a-fA-F]{64}', expected):
                errors.append(f'{ident}: missing/invalid asset SHA-256')
            elif target and hashlib.sha256(target.read_bytes()).hexdigest() != expected.lower():
                errors.append(f'{ident}: asset SHA-256 mismatch')
        else:
            errors.append(f'{ident}: unsupported representation: {kind}')
    return {'status': 'PASS' if not errors else 'FAIL', 'entry_count': len(data['entries']), 'errors': errors, 'scope': 'Catalog and file checks only; semantic fit and editability require rendered/native review.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalog', type=Path, default=DEFAULT_CATALOG)
    commands = parser.add_subparsers(dest='command', required=True)
    find = commands.add_parser('search', help='Return advisory lexical matches')
    find.add_argument('query')
    find.add_argument('--block-type')
    find.add_argument('--representation')
    find.add_argument('--limit', type=int, default=5, help='Search display size only; not a workflow asset cap')
    batch = commands.add_parser('batch', help='Return local advisory matches for every supplied block')
    batch.add_argument('input', type=Path, help='JSON with schema_version 1 and a blocks list')
    batch.add_argument('--limit', type=int, default=3, help='Candidates per block only; not a block or workflow cap')
    commands.add_parser('validate', help='Check metadata, local files and asset hashes')
    args = parser.parse_args()
    try:
        if args.command == 'validate':
            result = validate(args.catalog)
        elif args.command == 'batch':
            payload = json.loads(args.input.read_text(encoding='utf-8-sig'))
            result = batch_catalog(args.catalog, payload, args.limit)
        else:
            if args.limit < 1:
                raise ValueError('--limit must be positive')
            result = {'advisory_only': True, 'matches': search(load_catalog(args.catalog)['entries'], args.query, args.block_type, args.representation, args.limit)}
        print(json.dumps(result, ensure_ascii=True, indent=2))
        return 1 if result.get('status') == 'FAIL' else 0
    except (OSError, ValueError, TypeError, AttributeError) as error:
        parser.exit(2, f'visual bank: {error}\n')


if __name__ == '__main__':
    raise SystemExit(main())
