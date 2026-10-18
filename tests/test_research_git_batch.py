"""Behavioral parity and cleanup checks for streamed Git provenance reads."""
from contextlib import closing
import importlib.util
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('research_package_batch', ROOT/'scripts/research_package.py')
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)


class GitBatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        M.git(self.root,'init','-q')
        for key,value in [('user.name','Fixture'),('user.email','fixture@example.invalid'),('core.autocrlf','false')]:
            M.git(self.root,'config',key,value)
        (self.root/'dir').mkdir()
        for name,data in [('empty',b''),('binary',b'\0\n\xff'*65537),('dir/with spaces',b'alpha\n'),('unicode-\u03ba',b'omega')]:
            (self.root/name).write_bytes(data)
        M.git(self.root,'add','.')
        M.git(self.root,'-c','maintenance.auto=false','-c','gc.auto=0','commit','-qm','fixture')

    def test_exact_bytes_oids_empty_binary_unicode_duplicate_and_tree(self):
        names=['empty','binary','dir/with spaces','unicode-\u03ba','empty','dir']
        expected=[(M.git(self.root,'rev-parse','HEAD:'+n).decode().strip(),M.git(self.root,'show','HEAD:'+n)) for n in names]
        self.assertEqual(list(M.git_source_rows(self.root,'HEAD',names)),expected)

    def test_missing_source_rejects_and_process_is_reaped(self):
        real=subprocess.Popen;children=[]
        def popen(*a,**kw):
            p=real(*a,**kw);children.append(p);return p
        with patch.object(M.subprocess,'Popen',side_effect=popen):
            with self.assertRaisesRegex(ValueError,'missing or invalid Git source'):
                list(M.git_source_rows(self.root,'HEAD',['empty','absent']))
        self.assertTrue(children)
        self.assertTrue(all(p.poll() is not None for p in children))

    def test_early_validation_failure_reaps_process(self):
        real=subprocess.Popen;children=[]
        def popen(*a,**kw):
            p=real(*a,**kw);children.append(p);return p
        with patch.object(M.subprocess,'Popen',side_effect=popen):
            with self.assertRaisesRegex(ValueError,'source mismatch'):
                with closing(M.git_source_rows(self.root,'HEAD',['empty','binary'])) as rows:
                    next(rows)
                    raise ValueError('source mismatch')
        self.assertTrue(all(p.poll() is not None for p in children))

    def test_newline_path_retains_legacy_argument_semantics(self):
        # Windows filenames cannot contain LF. Test the exact fallback call
        # boundary without pretending that such a file was created on Windows.
        calls=[]
        def legacy(root,*args):
            calls.append(args)
            return b'a'*40+b'\n' if args[0]=='rev-parse' else b'payload'
        with patch.object(M,'git',side_effect=legacy):
            self.assertEqual(list(M.git_source_rows(self.root,'HEAD',['a\nb'])),[('a'*40,b'payload')])
        self.assertEqual(calls,[('rev-parse','HEAD:a\nb'),('show','HEAD:a\nb')])

    def test_no_cross_invocation_worktree_or_object_cache(self):
        old=list(M.git_source_rows(self.root,'HEAD',['empty']))
        (self.root/'empty').write_bytes(b'changed')
        # Immutable pinned object is unchanged until a new commit is requested.
        self.assertEqual(list(M.git_source_rows(self.root,'HEAD',['empty'])),old)
        M.git(self.root,'add','empty');M.git(self.root,'-c','maintenance.auto=false','-c','gc.auto=0','commit','-qm','change')
        self.assertNotEqual(list(M.git_source_rows(self.root,'HEAD',['empty'])),old)

    def fake_process(self, response, code=0):
        class Process:
            def __init__(self):
                self.stdin=io.BytesIO();self.stdout=io.BytesIO(response)
                self.stderr=io.BytesIO(b'injected reader failure');self.returncode=None
            def __enter__(self):return self
            def __exit__(self,*args):self.stdout.close();self.stderr.close()
            def poll(self):return self.returncode
            def wait(self,timeout=None):self.returncode=code;return code
            def kill(self):self.returncode=-9
        return Process()

    def test_malformed_and_truncated_batch_responses_fail_closed(self):
        oid=b'a'*40
        for response in [b'',oid+b' blob invalid\n',oid+b' blob 3\nab',oid+b' blob 3\nabcX']:
            with self.subTest(response=response):
                child=self.fake_process(response)
                with patch.object(M.subprocess,'Popen',return_value=child):
                    with self.assertRaisesRegex(ValueError,'invalid Git source|truncated Git source'):
                        list(M.git_source_rows(self.root,'HEAD',['empty']))
                self.assertIsNotNone(child.poll())

    def test_valid_payload_followed_by_nonzero_exit_rejects(self):
        child=self.fake_process(b'a'*40+b' blob 0\n\n',code=7)
        with patch.object(M.subprocess,'Popen',return_value=child):
            with self.assertRaisesRegex(ValueError,'Git source reader failed'):
                list(M.git_source_rows(self.root,'HEAD',['empty']))
        self.assertEqual(child.poll(),7)


if __name__=='__main__':unittest.main()
