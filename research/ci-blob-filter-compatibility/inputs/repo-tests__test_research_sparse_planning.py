"""Complete sparse/full routing with exact HEAD/index and deletion controls."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('sparse_runner',ROOT/'scripts/research_package.py')
runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)


class SparsePlanningTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/'repo';self.root.mkdir()
        self.git('init','-q');self.git('config','user.name','Fixture')
        self.git('config','user.email','fixture@example.invalid');self.git('config','core.autocrlf','false')
        self.write('scripts/research_package.py',(ROOT/'scripts/research_package.py').read_text())
        self.write('inputs/value.txt','1')
        for name in ['alpha','hidden']:
            self.write('research/'+name+'/VERIFY.json',json.dumps({'inputs':['inputs/value.txt']}))
            self.write('research/'+name+'/README.md','fixture')
        self.base=self.commit()
        self.manifest='research/hidden/VERIFY.json'

    def git(self,*args,input=None):
        return subprocess.run(['git',*args],input=input,cwd=self.root,check=True,
                              stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout

    def write(self,name,text):
        path=self.root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text,encoding='utf-8')

    def commit(self):
        self.git('add','--all');self.git('commit','-qm','fixture')
        return self.git('rev-parse','HEAD').decode().strip()

    def sparse(self,whole_research=False):
        self.git('sparse-checkout','init','--cone')
        paths = ['scripts', 'inputs']
        if not whole_research:
            paths.append('research/alpha')
        self.git('sparse-checkout', 'set', *paths)
        self.assertFalse((self.root/self.manifest).exists())

    def cli(self,base='0'):
        return subprocess.run([sys.executable,'-B',str(self.root/'scripts/research_package.py'),
                               '--changed-since',base],cwd=self.root,capture_output=True,text=True,timeout=20)

    def test_full_and_sparse_matrices_match_for_input_and_global_changes(self):
        self.write('inputs/value.txt','2');self.commit()
        expected=self.cli(self.base);self.assertEqual(expected.returncode,0,expected.stderr)
        self.sparse()
        actual=self.cli(self.base);self.assertEqual(actual.returncode,0,actual.stderr)
        self.assertEqual(actual.stdout,expected.stdout)
        self.assertIn('1 unchanged sparse manifests',actual.stderr)
        self.assertEqual(runner.plan(self.root,['scripts/research_package.py']),['research/alpha','research/hidden'])
        self.assertFalse((self.root/self.manifest).exists())

    def test_explanations_bind_identical_manifest_bytes_in_sparse_checkout(self):
        expected = runner.plan_details(self.root, ['inputs/value.txt'])
        self.sparse()
        actual = runner.plan_details(self.root, ['inputs/value.txt'])
        self.assertEqual(actual, expected)
        self.assertEqual(len(actual), 2)
        for row in actual:
            self.assertEqual(row['causes']['declared_inputs'], ['inputs/value.txt'])
            self.assertEqual(len(row['manifest_sha256']), 64)

    def test_entire_research_directory_may_be_omitted(self):
        self.sparse(whole_research=True)
        self.assertFalse((self.root/'research').exists())
        result=self.cli();self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(len(json.loads(result.stdout)['include']),2)
        self.assertIn('2 unchanged sparse manifests',result.stderr)

    def test_prefix_package_names_keep_the_full_checkout_order(self):
        self.write('research/alpha-extra/VERIFY.json',json.dumps({'inputs':['inputs/value.txt']}))
        self.commit()
        expected=runner.plan(self.root,['inputs/value.txt'])
        self.assertEqual(expected,['research/alpha','research/alpha-extra','research/hidden'])
        self.sparse()
        self.assertEqual(runner.plan(self.root,['inputs/value.txt']),expected)

    def test_ordinary_and_staged_deletion_reject_but_committed_deletion_is_valid(self):
        (self.root/self.manifest).unlink()
        for staged in (False,True):
            if staged:self.git('add','--all')
            result=self.cli()
            self.assertNotEqual(result.returncode,0)
            self.assertEqual(result.stdout,'')
            self.assertIn('not an unchanged sparse HEAD input',result.stderr)
        self.git('commit','-qm','remove opt in')
        result=self.cli(self.base);self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(json.loads(result.stdout),{'include':[]})

    def test_changed_skip_worktree_blob_rejected(self):
        self.sparse()
        blob=self.git('hash-object','-w','--stdin',input=b'{"inputs":[]}').decode().strip()
        self.git('update-index','--cacheinfo','100644,'+blob+','+self.manifest)
        self.git('update-index','--skip-worktree',self.manifest)
        result=self.cli();self.assertNotEqual(result.returncode,0)
        self.assertEqual(result.stdout,'');self.assertIn('not an unchanged sparse HEAD input',result.stderr)

    def test_changed_skip_worktree_mode_rejected(self):
        self.sparse()
        blob=self.git('rev-parse','HEAD:'+self.manifest).decode().strip()
        self.git('update-index','--cacheinfo','100755,'+blob+','+self.manifest)
        self.git('update-index','--skip-worktree',self.manifest)
        self.assertNotEqual(self.cli().returncode,0)

    def test_conflicted_manifest_index_rejected(self):
        self.sparse()
        blob=self.git('rev-parse','HEAD:'+self.manifest).decode().strip()
        text='0 '+'0'*40+'\t'+self.manifest+'\n'
        text+=''.join('100644 '+blob+' '+str(stage)+'\t'+self.manifest+'\n' for stage in [1,2,3])
        self.git('update-index','--index-info',input=text.encode())
        result=self.cli();self.assertNotEqual(result.returncode,0);self.assertEqual(result.stdout,'')

    def test_omitted_invalid_json_and_invalid_inputs_fail_closed(self):
        for text in ['{',json.dumps({'inputs':['../escape']})]:
            self.write(self.manifest,text);self.commit();self.sparse()
            result=self.cli();self.assertNotEqual(result.returncode,0);self.assertEqual(result.stdout,'')
            self.git('sparse-checkout','disable')

    def test_working_edits_and_new_local_manifests_remain_visible(self):
        self.write(self.manifest,json.dumps({'inputs':[]}))
        self.write('research/local/VERIFY.json',json.dumps({'inputs':['inputs/value.txt']}))
        self.assertEqual(runner.plan(self.root,['inputs/value.txt']),['research/alpha','research/local'])

    def test_nonregular_head_manifest_is_never_a_sparse_json_input(self):
        (self.root/self.manifest).unlink()
        (self.root/self.manifest).symlink_to('README.md')
        self.commit();self.sparse()
        result=self.cli();self.assertNotEqual(result.returncode,0);self.assertEqual(result.stdout,'')


if __name__=='__main__':unittest.main()
