"""Real-Git selection explanations preserve the public matrix and fail closed."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ExplainTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)/'repo'; self.root.mkdir()
        self.report = Path(self.tmp.name)/'why.json'
        self.output = Path(self.tmp.name)/'github-output'
        self.git('init', '-q')
        self.git('config', 'user.name', 'Fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        self.git('config', 'core.autocrlf', 'false')
        self.write('scripts/research_package.py', (ROOT/'scripts/research_package.py').read_text())
        self.write('input/line\n雪.json', '1')
        self.write('input/b.json', '2')
        self.write('research/alpha/VERIFY.json', json.dumps({'inputs':['input/line\n雪.json']}))
        self.write('research/beta/VERIFY.json', json.dumps({'inputs':['input/b.json']}))
        self.write('research/alpha/check.py', 'pass\n')
        self.write('README.md', 'fixture\n')
        self.base = self.commit()

    def write(self, name, text):
        path=self.root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text,encoding='utf-8')

    def git(self, *args):
        return subprocess.check_output(['git',*args],cwd=self.root,stderr=subprocess.PIPE).decode().strip()

    def commit(self):
        self.git('add','--all');self.git('commit','-qm','fixture')
        return self.git('rev-parse','HEAD')

    def run_cli(self, explain=True, extra=(), base=None):
        argv=[sys.executable,'-B',str(self.root/'scripts/research_package.py'),
              '--changed-since',base or self.base]
        if explain: argv+=['--explain-plan',str(self.report)]
        argv+=list(extra)
        return subprocess.run(argv,cwd=self.root,capture_output=True,text=True,encoding='utf-8',timeout=10)

    def test_all_three_causes_and_matrix_bytes_are_retained(self):
        self.write('input/line\n雪.json','3')
        self.write('research/alpha/check.py','changed\n')
        with (self.root/'scripts/research_package.py').open('a') as stream: stream.write('\n# shared\n')
        self.write('README.md','unrelated\n')
        head=self.commit()
        normal=self.run_cli(False, extra=['--matrix-batch-size','1'])
        explained=self.run_cli(extra=['--matrix-batch-size','1','--github-output',str(self.output)])
        self.assertEqual(explained.returncode,0,explained.stderr)
        self.assertEqual(explained.stdout,normal.stdout)
        data=json.loads(self.report.read_text())
        self.assertEqual((data['base'],data['head']),(self.base,head))
        a,b=data['selected']
        self.assertEqual(a['package'],'research/alpha')
        self.assertEqual(a['causes'],{'declared_inputs':['input/line\n雪.json'],
                                     'package_files':['research/alpha/check.py'],
                                     'shared_controls':['scripts/research_package.py']})
        self.assertEqual(b['causes']['declared_inputs'],[])
        self.assertEqual(b['causes']['shared_controls'],['scripts/research_package.py'])
        self.assertEqual(a['manifest_sha256'],hashlib.sha256((self.root/'research/alpha/VERIFY.json').read_bytes()).hexdigest())
        self.assertEqual(data['unmatched_paths'],['README.md'])
        fields=dict(line.split('=',1) for line in self.output.read_text().splitlines())
        self.assertEqual(json.loads(fields['matrix']),json.loads(normal.stdout))
        self.assertEqual(fields['count'],'2')

    def test_removed_and_renamed_inputs_keep_literal_reasons(self):
        self.git('mv','input/line\n雪.json','input/renamed.json')
        (self.root/'input/b.json').unlink()
        self.commit()
        result=self.run_cli();self.assertEqual(result.returncode,0,result.stderr)
        data=json.loads(self.report.read_text())
        self.assertEqual([r['package'] for r in data['selected']],['research/alpha','research/beta'])
        self.assertEqual(data['selected'][0]['causes']['declared_inputs'],['input/line\n雪.json'])
        self.assertEqual(data['selected'][1]['causes']['declared_inputs'],['input/b.json'])
        self.assertEqual(data['unmatched_paths'],['input/renamed.json'])

    def test_unrelated_change_and_all_tracked_mode(self):
        self.write('README.md','new\n');self.commit()
        result=self.run_cli();self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(json.loads(result.stdout),{'include':[]})
        self.assertEqual(json.loads(self.report.read_text())['unmatched_paths'],['README.md'])
        result=self.run_cli(base='0');self.assertEqual(result.returncode,0,result.stderr)
        data=json.loads(self.report.read_text())
        self.assertIsNone(data['base']);self.assertEqual(data['mode'],'all-tracked')
        self.assertEqual(len(data['selected']),2)

    def test_invalid_manifest_never_publishes_partial_report_or_matrix(self):
        self.report.write_text('previous complete report')
        self.write('research/beta/VERIFY.json','{"inputs":["../escape"]}')
        self.commit()
        result=self.run_cli(extra=['--github-output',str(self.output)])
        self.assertNotEqual(result.returncode,0)
        self.assertEqual(result.stdout,'')
        self.assertFalse(self.output.exists())
        self.assertEqual(self.report.read_text(),'previous complete report')

    def test_report_write_failure_prevents_matrix_publication(self):
        self.report=Path(self.tmp.name)/'missing'/'why.json'
        result=self.run_cli(extra=['--github-output',str(self.output)])
        self.assertNotEqual(result.returncode,0)
        self.assertEqual(result.stdout,'')
        self.assertFalse(self.output.exists())

    def test_conflicting_output_paths_rejected(self):
        result=self.run_cli(extra=['--github-output',str(self.report)])
        self.assertNotEqual(result.returncode,0)
        self.assertIn('different files',result.stderr)
        self.assertFalse(self.report.exists())


if __name__ == '__main__':
    unittest.main()
