"""Export, integrity and deterministic-artifact contract checks."""
import hashlib,json,os,py_compile,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import model as M


class ExportChecks(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='p104-retiming-')
        self.root=Path(self.temp.name)
        self.package=self.root/'research/p104-shared-chart-retiming'
        shutil.copytree(M.HERE,self.package,ignore=shutil.ignore_patterns('__pycache__'))
        for record in M.read(M.HERE/'SOURCES.json')['files']:
            if record['usage']=='input':
                target=self.root/record['path'];target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(M.ROOT/record['path'],target)
        self.cwd=self.root/'unrelated';self.cwd.mkdir()

    def tearDown(self):self.temp.cleanup()

    def run_file(self,name,*args,success=True):
        result=subprocess.run([sys.executable,'-I','-O','-B',str(self.package/name),*map(str,args)],
                              cwd=self.cwd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                              text=True,encoding='utf-8',timeout=60)
        if success:self.assertEqual(result.returncode,0,result.stdout)
        else:self.assertNotEqual(result.returncode,0,result.stdout)
        return result.stdout

    def hashes(self):
        return {str(p.relative_to(self.root)):hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.root.rglob('*') if p.is_file()}

    def test_read_only_export_and_regeneration(self):
        before=self.hashes();self.run_file('verify.py','--regenerate')
        self.assertEqual(self.hashes(),before)
        output=self.root/'new-artifacts'
        self.run_file('build.py','--out-dir',output)
        for name in ('WORD.json','NATIVE.json'):
            self.assertTrue(M.same(M.read(output/name),M.read(self.package/name)),name)
        receipt=self.root/'new-receipt.json';self.run_file('verify.py','--out',receipt)
        self.assertTrue(M.same(M.read(receipt),M.read(self.package/'RESULT.json')))
        old=receipt.read_bytes()
        self.assertIn('FileExistsError',self.run_file('verify.py','--out',receipt,success=False))
        self.assertEqual(receipt.read_bytes(),old)

    def test_source_integrity_before_execution(self):
        for relative,marker in ((M.INTERPRETER,'live source hash'),
                                ('research/p104-shared-chart-retiming/source/PR2662-WORD.json','predecessor hash')):
            path=self.root/relative;original=path.read_bytes()
            path.write_bytes(original+b'\n')
            self.assertIn(marker,self.run_file('verify.py',success=False))
            path.write_bytes(original)

    def test_typed_receipt_and_literal_word(self):
        path=self.package/'RESULT.json';original=path.read_bytes()
        result=M.read(path);result['schema_version']=True
        path.write_text(json.dumps(result),encoding='utf-8')
        self.assertIn('complete typed result receipt',self.run_file('verify.py',success=False))
        path.write_bytes(original)
        path=self.package/'WORD.json';word=M.read(path)
        word['program'][0][0]='unsupported'
        path.write_text(json.dumps(word),encoding='utf-8')
        self.assertIn('complete literal regeneration',self.run_file('verify.py',success=False))

    def test_historical_provenance_is_not_runtime_input(self):
        for relative in ('docs/research/agent-task-catalog.json','certificates/selected-result.json'):
            path=self.root/relative;path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text('unrelated later provenance revision\n',encoding='utf-8')
        self.run_file('verify.py')

    def test_stale_native_bytecode_is_ignored(self):
        source=self.root/M.INTERPRETER;original=source.read_bytes();stat=source.stat()
        stale=b"raise RuntimeError('STALE_NATIVE_CACHE')\n#"
        source.write_bytes(stale+b' '*(len(original)-len(stale)))
        os.utime(source,ns=(stat.st_atime_ns,stat.st_mtime_ns))
        py_compile.compile(str(source),doraise=True,optimize=1,
                           invalidation_mode=py_compile.PycInvalidationMode.TIMESTAMP)
        source.write_bytes(original);os.utime(source,ns=(stat.st_atime_ns,stat.st_mtime_ns))
        # Confirm the cache really is eligible under ordinary source loading.
        probe=self.package/'cache_probe.py'
        probe.write_text("import importlib.util\np="+repr(str(source))+"\ns=importlib.util.spec_from_file_location('cache_probe',p)\nm=importlib.util.module_from_spec(s)\ns.loader.exec_module(m)\n",encoding='utf-8')
        self.assertIn('STALE_NATIVE_CACHE',self.run_file('cache_probe.py',success=False))
        self.run_file('verify.py')
        # A changed source remains rejected even when that cache is present.
        source.write_bytes(original+b'\n')
        self.assertIn('live source hash',self.run_file('verify.py',success=False))


if __name__=='__main__':unittest.main()
