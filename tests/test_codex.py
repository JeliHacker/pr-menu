import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from urllib.parse import parse_qs, urlsplit
from pr_menu.codex import prepare_chat


class CodexTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / 'repo with spaces'
        self.repo.mkdir()
        self.git('init', '-b', 'main')
        self.git('-c', 'user.name=Test', '-c', 'user.email=test@example.test',
                 'commit', '--allow-empty', '-m', 'Initial')
        self.git('branch', 'feature/search')
        self.root = Path(self.temp.name) / 'workspaces'
        self.report = {'mode': 'local', 'repo': str(self.repo),
                       'branches': [{'name': 'feature/search', 'testChecklist': 'Try the search.', 'pr': None},
                                    {'name': 'main'}]}

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.repo), *args],
                                       text=True, stderr=subprocess.DEVNULL).strip()

    def test_new_workspace_does_not_switch_or_modify_current_checkout(self):
        (self.repo / 'uncommitted.txt').write_text('Keep this work')
        result = prepare_chat(self.report, 'feature/search', self.root)
        self.assertTrue(result['created'])
        self.assertEqual(self.git('branch', '--show-current'), 'main')
        self.assertEqual((self.repo / 'uncommitted.txt').read_text(), 'Keep this work')
        self.assertEqual(subprocess.check_output(['git', '-C', result['workspace'],
                         'branch', '--show-current'], text=True).strip(), 'feature/search')
        params = parse_qs(urlsplit(result['url']).query)
        self.assertEqual(params['path'], [result['workspace']])
        self.assertIn('feature/search', params['prompt'][0])
        self.assertTrue(result['url'].startswith('codex://new?'))

    def test_reuses_existing_checkout_including_dirty_work(self):
        (self.repo / 'notes.txt').write_text('In progress')
        result = prepare_chat(self.report, 'main', self.root)
        self.assertFalse(result['created'])
        self.assertEqual(result['workspace'], str(self.repo.resolve()))
        self.assertEqual((self.repo / 'notes.txt').read_text(), 'In progress')

    def test_repeated_click_reuses_prepared_worktree(self):
        one = prepare_chat(self.report, 'feature/search', self.root)
        two = prepare_chat(self.report, 'feature/search', self.root)
        self.assertTrue(one['created'])
        self.assertFalse(two['created'])
        self.assertEqual(one['workspace'], two['workspace'])

    def test_does_not_trust_stale_snapshot_workspace(self):
        self.report['branches'][0]['workspace'] = str(self.repo)
        result = prepare_chat(self.report, 'feature/search', self.root)
        self.assertNotEqual(result['workspace'], str(self.repo))

    def test_unknown_branch_and_demo_are_rejected(self):
        with self.assertRaises(ValueError):
            prepare_chat(self.report, '--help', self.root)
        self.report['mode'] = 'demo'
        with self.assertRaises(ValueError):
            prepare_chat(self.report, 'feature/search', self.root)
