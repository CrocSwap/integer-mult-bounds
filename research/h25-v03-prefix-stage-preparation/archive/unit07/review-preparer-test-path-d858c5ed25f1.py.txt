"""NEW-only exact derived-path fail-before-I/O control; inert owned fixture."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('unit07_path_fixture_builder',HERE/'preparer_data_dag_v2.py')
dag=importlib.util.module_from_spec(spec);spec.loader.exec_module(dag)
m=dag.m

class PathContract(unittest.TestCase):
    def test_derived_output_65_components_is_rejected_before_first_io(self):
        with tempfile.TemporaryDirectory(prefix='unit07-derived-path-') as directory:
            root=Path(directory);request,constants=dag.fixture(root)
            request['canonical_root']='/'+('/'.join(['component']*60))
            request['runner_source']=dict(request['runner_source'],path=request['canonical_root']+'/run_guarded_v3.py')
            events=[]
            class NoIO:
                def __getattr__(self,name):events.append(name);raise AssertionError('preparation I/O before path rejection')
            try:
                with patch.multiple(m,**constants),patch.object(m,'os',NoIO()):
                    with self.assertRaises(m.Stop) as caught:m.prepare_prefix_stage(request)
                self.assertEqual(str(caught.exception),'path component bound')
                owner=m.PREPARATIONS[-1]
                self.assertIs(owner.primary,caught.exception);self.assertEqual(events,[])
                self.assertEqual(owner.captures,[]);self.assertEqual(owner.writes,[])
                self.assertEqual(owner.final_bill['io_attempts'],{})
                self.assertTrue(owner.cleanup_done)
            finally:
                for path in sorted(root.rglob('*'),key=lambda p:len(p.parts),reverse=True):
                    if path.is_dir():path.chmod(0o700)

if __name__=='__main__':unittest.main(verbosity=2)
