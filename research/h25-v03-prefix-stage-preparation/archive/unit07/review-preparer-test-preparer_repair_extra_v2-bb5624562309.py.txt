"""Additional NEW-only consequential controls, fresh owned fixture DATA only."""
import hashlib
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'implementation/prepare_prefix_stage_v2.py'
spec=importlib.util.spec_from_file_location('unit07_extra_new',SOURCE)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


class RepairExtra(unittest.TestCase):
    def test_generated_record_raw_survives_aggregate_refusal_before_io(self):
        owner=m.make_preparation_owner();owner.total_bytes=m.TOTAL_CAP
        with tempfile.TemporaryDirectory(prefix='unit07-raw-cap-') as directory:
            m.open_existing_directory(owner,directory)
            try:
                with self.assertRaises(m.Stop):m.install_record(owner,directory,'record.json',{'fixture':'new raw retained'})
                self.assertEqual(owner.generated_records[-1]['raw'],m.canonical({'fixture':'new raw retained'}))
                self.assertFalse((Path(directory)/'record.json').exists())
                self.assertEqual(owner.writes,[])
            finally:m.close_preparation(owner)
    def test_every_actual_source_io_attempt_including_failed_close_is_counted(self):
        owner=m.make_preparation_owner();realclose=os.close;secondary=RuntimeError('owned close failure')
        with tempfile.TemporaryDirectory(prefix='unit07-io-bill-') as directory:
            path=Path(directory)/'source';raw=b'new owned input';path.write_bytes(raw)
            pin={'path':str(path),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'identity':m.identity(path.stat())}
            def close(fd):realclose(fd);raise secondary
            with patch.object(m.os,'close',close):
                with self.assertRaises(RuntimeError) as raised:m.verify_source(owner,pin)
            self.assertIs(raised.exception,secondary)
            self.assertEqual(owner.io_counts,{'stat':2,'open':1,'fstat':2,'read':1,'close':1})
            self.assertEqual(owner.stat_calls,4);self.assertEqual(owner.close_records[-1]['attempted'],True)
            self.assertFalse(owner.close_records[-1]['completed']);self.assertIsNone(owner.fd_slots[-1])
            m.close_preparation(owner)
            self.assertEqual(owner.io_counts['close'],1)  # no second attempt
    def test_current_caller_pin_is_exact_and_rejects_renamed_old_source(self):
        self.assertEqual(m.CALLER_PIN,('25138c2c998762649c6a61cb8a6ae8aacd81bd533591b082ab6f58def712fca2',34716))
        dag_spec=importlib.util.spec_from_file_location('unit07_fixture_builder',HERE/'preparer_data_dag_v2.py')
        dag=importlib.util.module_from_spec(dag_spec);dag_spec.loader.exec_module(dag)
        with tempfile.TemporaryDirectory(prefix='unit07-caller-pin-') as directory:
            root=Path(directory);request,constants=dag.fixture(root)
            constants.pop('CALLER_PIN')
            try:
                with patch.multiple(m,**constants):
                    with self.assertRaises(m.Stop) as caught:m.validate_request(request)
                self.assertEqual(str(caught.exception),'fixed bounded caller source differs')
                self.assertFalse((root/'R/stages/fixture-stage').exists())
            finally:
                for path in sorted(root.rglob('*'),key=lambda p:len(p.parts),reverse=True):
                    if path.is_dir():path.chmod(0o700)
    def test_original_supported_expectations_all_exact_discriminators(self):
        base={'outcome':'EXACT_SOURCE_REFUSAL','exception_type':'RuntimeError','message':'Variant current source closure differs','terminal_function':'_vcheck_custody','v03_discriminator':True,'compiler_launches':0,'candidate_image_loads':0,'complete_raw_and_owned_terminal_required':True}
        m.validate_expectation(base)
        for field,value in (('message','wrong'),('compiler_launches',True),('candidate_image_loads',False),('complete_raw_and_owned_terminal_required',1)):
            with self.subTest(field=field):
                with self.assertRaises(m.Stop):m.validate_expectation(dict(base,**{field:value}))

if __name__=='__main__':unittest.main(verbosity=2)
