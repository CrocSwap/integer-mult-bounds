"""Finite certificate and adversarial literal-port controls, no theorem claim."""
import copy,gzip,importlib.util,json,pathlib,subprocess,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
HERE=ROOT/'research/depth-coarse'
sys.path.insert(0,str(HERE))
spec=importlib.util.spec_from_file_location('balanced_split_verify',HERE/'verify.py')
verify=importlib.util.module_from_spec(spec);spec.loader.exec_module(verify)

class BalancedSplitControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.word=json.loads(gzip.decompress((HERE/'word-23.json.gz').read_bytes()))

    def rejected(self,change):
        word=copy.deepcopy(self.word);change(word)
        with tempfile.TemporaryDirectory() as directory:
            path=pathlib.Path(directory)/'word.json.gz'
            path.write_bytes(gzip.compress(json.dumps(word).encode()))
            with self.assertRaises(AssertionError):verify.literal_binding(path)

    def test_complete_exact_certificate(self):
        with tempfile.TemporaryDirectory() as directory:
            verify.arithmetic_check(pathlib.Path(directory))

    def test_source_manifest_excludes_runtime_caches(self):
        manifest=json.loads((HERE/'SOURCE.json').read_text())['files']
        for name in manifest:
            path=pathlib.PurePosixPath(name)
            self.assertFalse(path.is_absolute(),name)
            self.assertNotIn('..',path.parts,name)
            self.assertNotIn('__pycache__',path.parts,name)
            self.assertNotIn(path.suffix,('.pyc','.pyo'),name)
        verify.source_check()

    def test_selected_literal_scatter(self):
        for h in (23,25):verify.literal_binding(HERE/f'word-{h}.json.gz')

    def test_canceling_uncharged_scatter_rejected(self):
        def change(w):w['scatter']+=w['scatter'][:1]*2
        self.rejected(change)

    def test_self_scatter_rejected(self):
        def change(w):w['scatter'].append([w['v'],w['v']])
        self.rejected(change)

    def test_dirty_source_coordinate_rejected(self):
        def change(w):w['sources']['-1']=w['sources'].pop('0')
        self.rejected(change)

    def test_aliased_source_rejected(self):
        def change(w):w['sources']['1']=w['sources']['0']
        self.rejected(change)

    def test_negative_xor_index_rejected(self):
        def change(w):w['ops'][0][0]=-1
        self.rejected(change)

    def test_missing_terminal_rejected(self):
        def change(w):w['outputs'].pop()
        self.rejected(change)

    def test_assertion_disabled_verifier_rejected(self):
        result=subprocess.run([sys.executable,'-O',str(HERE/'verify.py'),'--arithmetic-only'],capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('Assertions must remain enabled',result.stderr)

    def test_assertion_disabled_independent_checker_rejected(self):
        result=subprocess.run([sys.executable,'-O',str(HERE/'independent.py')],capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('Assertions must remain enabled',result.stderr)

if __name__=='__main__':unittest.main()
