import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

spec = importlib.util.spec_from_file_location('visual_bank', Path(__file__).resolve().parents[1] / 'scripts/visual_bank.py')
bank = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bank)


class VisualBankTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'preview.png').write_bytes(b'preview fixture')
        (self.root / 'recipes.mjs').write_text('export function addVisual() {}')
        self.entries = [dict(id='learning', title='Learning together', topics=['teaching', 'learning'], block_types=['objective'], semantic_use='Learning with an existing tool', avoid_when='Does not imply measured outcomes', representation='native_components', selection_unit='native_group', recipe={'module': 'recipes.mjs', 'export': 'addVisual', 'id': 'learning'}, preview='preview.png', provenance={'source': 'fixture'})]
        self.catalog = self.root / 'catalog.json'

    def save(self):
        self.catalog.write_text(json.dumps({'schema_version': 1, 'entries': self.entries}))

    def test_topic_search_and_user_filters(self):
        self.assertEqual(bank.search(self.entries, 'TEACHING learning')[0]['id'], 'learning')
        self.assertEqual(bank.search(self.entries, 'teaching', block_type='evidence'), [])
        self.assertEqual(bank.search(self.entries, 'teaching', representation='replaceable_raster_image'), [])
        self.assertEqual(bank.search(self.entries, 'unrelated astronomy'), [])

    def test_batch_preserves_every_block_order_and_no_match(self):
        payload = {'schema_version': 1, 'blocks': [
            {'id': 'third', 'query': 'teaching'},
            {'id': 'first', 'query': 'astronomy'},
            {'id': 'second', 'query': 'learning'},
        ]}
        result = bank.batch_search(self.entries, payload, limit=1)
        self.assertTrue(result['advisory_only'])
        self.assertEqual(result['method'], 'local_lexical_search')
        self.assertEqual(result['score_kind'], 'lexical_rank_not_confidence')
        self.assertEqual([item['id'] for item in result['results']], ['third', 'first', 'second'])
        self.assertEqual([item['status'] for item in result['results']], ['match', 'no_match', 'match'])
        unmatched = result['results'][1]
        self.assertEqual(unmatched['candidates'], [])
        self.assertIn('pending', unmatched['planner_action'])
        expected_fields = {'id', 'title', 'score', 'semantic_use', 'avoid_when', 'representation', 'selection_unit'}
        self.assertEqual(set(result['results'][0]['candidates'][0]), expected_fields)

    def test_batch_reuses_lexical_scoring_and_block_type(self):
        self.entries.append({**self.entries[0], 'id': 'alternate', 'title': 'Different', 'topics': ['learning'], 'block_types': ['evidence'], 'semantic_use': 'Teaching'})
        payload = {'schema_version': 1, 'blocks': [
            {'id': 'all', 'query': 'teaching learning'},
            {'id': 'evidence', 'query': 'teaching learning', 'block_type': 'evidence'},
        ]}
        result = bank.batch_search(self.entries, payload, limit=1)['results']
        self.assertEqual(result[0]['candidates'][0]['id'], 'learning')
        self.assertEqual(result[0]['candidates'][0]['score'], 15)
        self.assertEqual(len(result[0]['candidates']), 1)
        self.assertEqual(result[1]['candidates'][0]['id'], 'alternate')
        self.assertEqual(result[1]['candidates'][0]['score'], 6)
        self.assertEqual(result[1]['block_type'], 'evidence')

    def test_batch_rejects_invalid_input_and_limit(self):
        good = {'id': 'a', 'query': 'learning'}
        invalid = [
            None, [], {},
            {'schema_version': True, 'blocks': [good]},
            {'schema_version': 1.0, 'blocks': [good]},
            {'schema_version': 2, 'blocks': [good]},
            {'schema_version': 1, 'blocks': []},
            {'schema_version': 1, 'blocks': {}},
            {'schema_version': 1, 'blocks': [good], 'endpoint': 'ignored'},
            *({'schema_version': 1, 'blocks': [block]} for block in [
                None, 'learning', {}, {'id': 'a'},
                {'id': '', 'query': 'learning'}, {'id': '  ', 'query': 'learning'},
                {'id': 1, 'query': 'learning'}, {'id': 'a', 'query': False},
                {'id': 'a', 'query': '  '}, {**good, 'block_type': None},
                {**good, 'block_type': []}, {**good, 'block_type': ''},
                {**good, 'block_type': '  '}, {**good, 'representation': 'native_components'},
            ]),
            {'schema_version': 1, 'blocks': [good, {**good, 'query': 'teaching'}]},
        ]
        for payload in invalid:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                bank.batch_search(self.entries, payload)
        for limit in (0, -1, True, 1.5, '3', None):
            with self.subTest(limit=limit), self.assertRaises(ValueError):
                bank.batch_search(self.entries, {'schema_version': 1, 'blocks': [good]}, limit=limit)

    def test_batch_catalog_read_once_and_hash_matches_used_bytes(self):
        self.save()
        expected_hash = hashlib.sha256(self.catalog.read_bytes()).hexdigest()
        original_read = Path.read_bytes
        with mock.patch.object(Path, 'read_bytes', autospec=True, side_effect=original_read) as read:
            result = bank.batch_catalog(self.catalog, {'schema_version': 1, 'blocks': [{'id': 'a', 'query': 'teaching'}]})
        read.assert_called_once_with(self.catalog)
        self.assertEqual(result['catalog_sha256'], expected_hash)

    def test_batch_cli_fixture_and_positive_limit(self):
        self.save()
        input_file = self.root / 'blocks.json'
        input_file.write_text(json.dumps({'schema_version': 1, 'blocks': [
            {'id': 'a', 'query': 'teaching'}, {'id': 'b', 'query': 'astronomy'},
        ]}), encoding='utf-8')
        command = [sys.executable, '-B', str(Path(bank.__file__)), '--catalog', str(self.catalog), 'batch', str(input_file)]
        result = subprocess.run(command + ['--limit', '1'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload['catalog_sha256'], hashlib.sha256(self.catalog.read_bytes()).hexdigest())
        self.assertEqual([item['status'] for item in payload['results']], ['match', 'no_match'])
        rejected = subprocess.run(command + ['--limit', '0'], capture_output=True, text=True)
        self.assertEqual(rejected.returncode, 2)
        self.assertIn('positive', rejected.stderr)

    def test_missing_recipe_is_reported(self):
        self.save()
        self.assertEqual(bank.validate(self.catalog)['status'], 'PASS')
        (self.root / 'recipes.mjs').unlink()
        self.assertIn('file missing', ' '.join(bank.validate(self.catalog)['errors']))

    def test_duplicate_id_and_escaping_path_are_reported(self):
        self.entries.append({**self.entries[0], 'preview': '../outside.png'})
        self.save()
        errors = ' '.join(bank.validate(self.catalog)['errors'])
        self.assertIn('duplicate', errors)
        self.assertIn('inside the visual bank', errors)

    def test_changed_artwork_invalidates_recorded_hash(self):
        asset = self.root / 'art.png'
        asset.write_bytes(b'original artwork')
        self.entries[0].update(representation='replaceable_raster_image', selection_unit='picture', recipe=None, asset={'path': 'art.png', 'sha256': hashlib.sha256(asset.read_bytes()).hexdigest()})
        self.save()
        self.assertEqual(bank.validate(self.catalog)['status'], 'PASS')
        asset.write_bytes(b'different artwork')
        self.assertIn('SHA-256 mismatch', ' '.join(bank.validate(self.catalog)['errors']))

    def test_recorded_module_and_preview_hashes_are_checked(self):
        (self.root / 'post_export.py').write_text('pass')
        self.entries[0]['recipe']['post_export'] = {'module': 'post_export.py', 'module_sha256': hashlib.sha256((self.root / 'post_export.py').read_bytes()).hexdigest()}
        self.entries[0]['recipe']['module_sha256'] = hashlib.sha256((self.root / 'recipes.mjs').read_bytes()).hexdigest()
        self.entries[0]['preview_sha256'] = hashlib.sha256((self.root / 'preview.png').read_bytes()).hexdigest()
        self.save()
        self.assertEqual(bank.validate(self.catalog)['status'], 'PASS')
        (self.root / 'recipes.mjs').write_text('changed recipe')
        (self.root / 'preview.png').write_bytes(b'changed preview')
        (self.root / 'post_export.py').write_text('changed helper')
        errors = bank.validate(self.catalog)['errors']
        self.assertEqual(sum('SHA-256 mismatch' in error for error in errors), 3)

    def test_loose_native_component_delivery_is_rejected(self):
        self.entries[0]['selection_unit'] = 'loose_components'
        self.save()
        self.assertIn('must be delivered as one native_group', ' '.join(bank.validate(self.catalog)['errors']))


if __name__ == '__main__':
    unittest.main()
