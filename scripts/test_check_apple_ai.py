import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch
spec = importlib.util.spec_from_file_location('monitor', Path(__file__).with_name('check_apple_ai.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
TEXT = Path(m.BASELINE).read_text()
OLD = m.parse(TEXT)
NEW_TEXT = TEXT + '\nDOMAIN,new-ai.apple.com\n'
NEW = m.parse(NEW_TEXT)

class FakeGitHub:
    def __init__(self):
        self.calls, self.prs, self.comments = [], [], []
        self.head, self.count = None, 0
        self.files = {'main-sha': TEXT}
    def file(self, ref):
        return self.files[ref]
    def api(self, method, path, data=None, missing=False):
        self.calls.append((method, path, data))
        if path == '/git/ref/heads/main': return {'object': {'sha': 'main-sha'}}
        if method == 'GET' and path.startswith('/pulls?'): return self.prs
        if path == '/git/ref/heads/' + m.BRANCH:
            return {'object': {'sha': self.head}} if self.head else None
        if path.startswith('/compare/'): return {'files': [{'filename': m.BASELINE}]}
        if method == 'GET' and path.startswith('/git/commits/'): return {'tree': {'sha': 'main-tree'}}
        if path == '/git/trees':
            assert len(data['tree']) == 1 and data['tree'][0]['path'] == m.BASELINE
            self.content = data['tree'][0]['content']
            return {'sha': 'new-tree'}
        if path == '/git/commits':
            self.count += 1
            sha = f'commit-{self.count}'
            self.files[sha] = self.content
            return {'sha': sha}
        if path.startswith('/git/refs'):
            self.head = data['sha']
            return {}
        if path == '/pulls':
            self.prs.append(dict(data, number=1, html_url='https://github.com/example/repo/pull/1'))
            return self.prs[0]
        if path == '/pulls/1':
            self.prs[0].update(data)
            return self.prs[0]
        if path.startswith('/issues/1/comments'):
            if method == 'GET': return self.comments
            self.comments.append(data)
            return data
        raise AssertionError((method, path, data))

class Tests(unittest.TestCase):
    def test_real_upstream(self): self.assertEqual(len(OLD), 11)
    def test_formatting(self):
        self.assertEqual(m.parse('# new date\n'+'\n'.join(reversed(m.canonical(OLD).upper().splitlines()))), OLD)
    def test_bad_content(self):
        for text in ['', '<html>Error</html>', '# only comment', '404: Not Found', TEXT+'BOGUS,foo.com\n', TEXT+'DOMAIN,bad domain.com\n', TEXT+'DOMAIN-SUFFIX,gateway.icloud.com\n', 'x'*(m.LIMIT+1)]:
            with self.subTest(text=text[:30]), self.assertRaises(ValueError): m.parse(text)
    def test_anomaly(self):
        with self.assertRaises(ValueError): m.validate_change(OLD, set(sorted(OLD)[:3]))
    def test_match_change(self):
        changed = OLD - {('DOMAIN-SUFFIX','gateway.icloud.com')} | {('DOMAIN','gateway.icloud.com')}
        self.assertIn('`DOMAIN-SUFFIX` → `DOMAIN`', m.report(OLD,changed))
    def test_no_change_no_api(self):
        with patch.object(m,'download',return_value=TEXT), patch.object(m,'GitHub') as api, patch('sys.argv',['check']):
            m.main()
            api.assert_not_called()
    def test_deduplicate_and_update(self):
        gh=FakeGitHub()
        m.sync(gh,'example/repo','main',OLD,NEW,NEW_TEXT)
        self.assertEqual((len(gh.prs),gh.count,len(gh.comments)),(1,1,1))
        start=len(gh.calls)
        m.sync(gh,'example/repo','main',OLD,NEW,NEW_TEXT)
        self.assertTrue(all(method=='GET' for method,_,_ in gh.calls[start:]))
        newer=NEW_TEXT+'DOMAIN,another.apple.com\n'
        m.sync(gh,'example/repo','main',OLD,m.parse(newer),newer)
        self.assertEqual((len(gh.prs),gh.count,len(gh.comments)),(1,2,2))
    def test_retry_comment(self):
        gh=FakeGitHub()
        m.sync(gh,'example/repo','main',OLD,NEW,NEW_TEXT)
        gh.comments.clear()
        m.sync(gh,'example/repo','main',OLD,NEW,NEW_TEXT)
        self.assertEqual((gh.count,len(gh.comments)),(1,1))
    def test_baseline_race(self):
        gh=FakeGitHub(); gh.files['main-sha']=NEW_TEXT
        with self.assertRaises(RuntimeError): m.sync(gh,'example/repo','main',OLD,NEW,NEW_TEXT)
        self.assertTrue(all(method=='GET' for method,_,_ in gh.calls))
    def test_download_failure(self):
        with patch.object(m.OPENER,'open',side_effect=TimeoutError), self.assertRaises(TimeoutError): m.download()

if __name__=='__main__': unittest.main()
