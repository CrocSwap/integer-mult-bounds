"""NEW-only counterexamples against frozen initial75bc source; no originals."""
import hashlib
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SOURCE=Path(__file__).resolve().parent.parent/'implementation/prepare_prefix_stage_v2.py'
spec=importlib.util.spec_from_file_location('unit07_counterexamples_new',SOURCE)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


class Counterexamples(unittest.TestCase):
    def test_exact_original_custody_refusal_is_supported(self):
        expected={'outcome':'EXACT_SOURCE_REFUSAL','exception_type':'RuntimeError','message':'Variant current source closure differs','terminal_function':'_vcheck_custody','v03_discriminator':False,'compiler_launches':0,'candidate_image_loads':0,'complete_raw_and_owned_terminal_required':True}
        m.validate_expectation(expected)
    def test_257_rows_fit_actual_entry_record_codec(self):
        owner=m.make_preparation_owner()
        with tempfile.TemporaryDirectory(prefix='unit07-codec-') as directory:
            m.open_existing_directory(owner,directory)
            try:
                pin=m.install_record(owner,directory,'rows.json',{'source_files':[{'path':'/fixture/'+str(i),'sha256':'0'*64,'bytes':1,'mode':0o444,'category':'project'} for i in range(257)]})
                self.assertLess(pin['bytes'],m.RECORD_CAP)
            finally:m.close_preparation(owner)
    def test_operation_bill_accounts_actual_source_stat_calls(self):
        owner=m.make_preparation_owner()
        with tempfile.TemporaryDirectory(prefix='unit07-stat-bill-') as directory:
            p=Path(directory)/'input';raw=b'owned fixture';p.write_bytes(raw)
            pin={'path':str(p),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'identity':m.identity(p.stat())}
            try:
                m.verify_source(owner,pin)
                bill=m.operation_bill(owner)
                # Actual read uses before-path, opened-FD, after-FD, after-path.
                self.assertGreaterEqual(bill['stat_calls'],4)
            finally:m.close_preparation(owner)
    def test_renamed_lookup_context_cannot_emit_stale_absolute_pin(self):
        owner=m.make_preparation_owner()
        with tempfile.TemporaryDirectory(prefix='unit07-context-') as directory:
            parent=Path(directory)/'parent';parent.mkdir();m.open_existing_directory(owner,str(parent))
            parent.rename(Path(directory)/'moved')
            try:
                with self.assertRaises((m.Stop,FileNotFoundError)):
                    m.install_file(owner,str(parent),'input',b'owned DATA')
            finally:m.close_preparation(owner)

if __name__=='__main__':unittest.main(verbosity=2)
