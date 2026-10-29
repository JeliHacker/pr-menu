import json
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import urlopen, Request
from http.server import ThreadingHTTPServer
from pr_menu.__main__ import handler, load_report


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), handler(demo=True))
        cls.url = f'http://127.0.0.1:{cls.server.server_port}'
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def test_demo_does_not_load_personal_snapshot(self):
        data = load_report(demo=True)
        self.assertEqual(data['mode'], 'demo')
        self.assertEqual(data['repo'], 'example/sample-app')
        self.assertNotIn('/Users/', json.dumps(data))

    def test_report_endpoint_and_cache_policy(self):
        with urlopen(self.url + '/api/report') as response:
            self.assertEqual(response.headers['Cache-Control'], 'no-store')
            self.assertEqual(json.load(response)['mode'], 'demo')

    def test_page_is_served(self):
        with urlopen(self.url) as response:
            self.assertIn(b'What should I try next?', response.read())

    def test_workspace_actions_reject_missing_or_cross_origin_tokens(self):
        with urlopen(self.url + '/api/report') as response:
            token = json.load(response)['actionToken']
        for headers in ({'Origin': self.url},
                        {'Origin': 'https://example.test', 'X-Pr-Menu-Token': token}):
            request = Request(self.url + '/api/codex', data=b'{"branch":"feature/search"}',
                              headers={**headers, 'Content-Type': 'application/json'}, method='POST')
            with self.assertRaises(HTTPError) as error:
                urlopen(request)
            self.assertEqual(error.exception.code, 403)

    def test_demo_workspace_action_is_rejected_even_with_valid_token(self):
        with urlopen(self.url + '/api/report') as response:
            token = json.load(response)['actionToken']
        request = Request(self.url + '/api/codex', data=b'{"branch":"feature/search"}',
                          headers={'Origin': self.url, 'X-Pr-Menu-Token': token,
                                   'Content-Type': 'application/json'}, method='POST')
        with self.assertRaises(HTTPError) as error:
            urlopen(request)
        self.assertEqual(error.exception.code, 400)

    def test_arbitrary_local_files_are_not_served(self):
        for path in ('/.pr-menu/inventory.json', '/README.md', '/../LICENSE'):
            with self.subTest(path=path), self.assertRaises(HTTPError) as error:
                urlopen(self.url + path)
            self.assertEqual(error.exception.code, 404)


if __name__ == '__main__':
    unittest.main()
