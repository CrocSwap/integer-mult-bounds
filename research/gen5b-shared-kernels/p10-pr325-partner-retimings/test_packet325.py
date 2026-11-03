"""Portable source, producer, array-contract and emitted-certificate regressions."""
from pathlib import Path
from fractions import Fraction
from unittest.mock import patch
import copy,subprocess,sys,tempfile,unittest
import packet325 as packet
packet.require_assertions()
class Tests(unittest.TestCase):
 def altered(self,path,mutate,check):
  original=packet.read;value=copy.deepcopy(original(path));mutate(value)
  def reader(p):return value if Path(p)==path else original(p)
  with patch.object(packet,'read',side_effect=reader):
   with self.assertRaises(AssertionError):check()
 def test_all_immutable_inputs(self):
  self.assertEqual(len(packet.verify_inputs()['files']),27)
 def test_source_bytes_mutation_rejected(self):
  for z in packet.source_manifest()['files']:
   with self.assertRaises(AssertionError):packet.check_input((packet.INPUTS/z['local']).read_bytes()+b' ',z)
 def test_git_blob_mutation_rejected(self):
  z=copy.deepcopy(packet.source_manifest()['files'][0]);z['git_blob']='0'*40
  with self.assertRaises(AssertionError):packet.check_input((packet.INPUTS/z['local']).read_bytes(),z)
 def test_sources_are_inert(self):
  rows=packet.source_manifest()['files'];self.assertTrue(any(z['local'].endswith('.py.txt')for z in rows));self.assertFalse(any(z['local'].endswith('.py')for z in rows));self.assertEqual({z['head']for z in rows},{packet.HEAD})
 def test_source_complete_producer_binding(self):
  self.assertTrue(packet.verify_source())
  self.altered(packet.SOURCE/'MANIFEST.json',lambda x:x['producers'].pop('check_retimings.py'),packet.verify_source)
 def test_stale_source_manifest_rejected(self):
  self.altered(packet.SOURCE/'MANIFEST.json',lambda x:x.__setitem__('input_manifest_sha256','0'*64),packet.verify_source)
 def test_stale_source_checker_rejected(self):
  self.altered(packet.SOURCE/'RESULT.json',lambda x:x.__setitem__('checker_sha256','0'*64),packet.verify_source)
 def test_full_frame_and_array_contract_bound(self):
  self.assertTrue(packet.verify_frame_binding())
  self.altered(packet.FRAME/'MANIFEST.json',lambda x:x['producers'].pop('validate_local.py'),packet.verify_frame_binding)
 def test_failed_frame_validation_rejected(self):
  self.altered(packet.FRAME/'VALIDATION.json',lambda x:x.__setitem__('all_frame_G_nondegeneracy_certified',False),packet.verify_frame)
 def test_array_payload_contract_cannot_be_omitted(self):
  self.altered(packet.AUDIT/'FULL-FRAME-AUDIT.json',lambda x:x.__setitem__('address_geometry_distinguished_from_F2_payload_values',False),packet.verify_frame_binding)
  self.altered(packet.AUDIT/'FULL-FRAME-AUDIT.json',lambda x:x.__setitem__('pinned_theorems',{}),packet.verify_frame_binding)
 def test_fresh_word_only(self):
  s=packet.read(packet.SOURCE/'RESULT.json');f=packet.read(packet.FRAME/'RESULT.json');g=packet.read(packet.GLOBAL/'RESULT.json')
  self.assertEqual(s['word_gzip_sha256'],packet.WORD);self.assertEqual((s['admitted'],s['rejected'],s['formal_columns']),(480,0,10020));self.assertFalse(s['prior_role_or_frame_selections_imported']);self.assertFalse(f['source_selections_imported_from_old_word']);self.assertFalse(g['prior_role_frame_or_chart_data_imported']);self.assertEqual(g['completion_sweeps'],0)
 def test_complete_global_program(self):
  g=packet.read(packet.GLOBAL/'RESULT.json');a=packet.read(packet.AUDIT/'GLOBAL-AUDIT.json')
  self.assertEqual((a['all_local_records'],a['all_global_stage_records'],a['all_namespaces'],a['phases']),(398660,119604000,300,720));self.assertEqual(a['program_binding'],g['full_program_sha256']);self.assertEqual(a['global_result_sha256'],packet.sha(packet.GLOBAL/'RESULT.json'))
  for folder in [packet.PREPARED,packet.GLOBAL]:
   for n,h in packet.read(folder/'MANIFEST.json').items():self.assertEqual(packet.sha(folder/n),h)
 def test_literal_banks_and_invoice(self):
  b=packet.read(packet.BANK/'BANK-RESULT.json');g=packet.read(packet.GLOBAL/'invoice.json')
  self.assertEqual((b['literal_stock'],b['literal_children'],b['literal_rank_mass'],b['deficit'],b['max_child_rank'],b['completion_children']),(658800,14514000,65757600,122400,42,0));self.assertEqual(b['assignment_count'],2430000);self.assertEqual(b['selector_calls'],170009279400);self.assertEqual(g['coefficient'],24857617667871401);self.assertEqual(g['coefficient'],b['coefficient'])
 def test_independent_equivalent_charts(self):
  b=packet.read(packet.BANK/'BANK-RESULT.json');p=packet.read(packet.PREPARED/'PREPARATION.json')
  self.assertEqual(b['chart_max_factors'],139);self.assertEqual(p['max_chart_factors'],141);self.assertEqual(b['normalizer_factor_bound'],p['normalizer_factor_bound']);self.assertEqual(p['normalizer_factor_bound'],349)
  self.assertEqual(packet.sha(packet.BANK/'literal-bank-assignments.bin.gz'),packet.sha(packet.PREPARED/'literal-bank-assignments.bin.gz'))
 def test_exact_price_and_adjacent_rejections(self):
  p=packet.read(packet.BANK/'PRICE-RESULT.json');a=packet.read(packet.AUDIT/'BANK-PRICE-AUDIT.json')
  self.assertEqual(Fraction(a['kappa']),Fraction(770612425424136,10**18));self.assertEqual(p['assembly']['kappa_decimal'],'0.000770612425424136');self.assertTrue(a['all47exact_slacks_reproduced']);self.assertTrue(a['adjacent_kappa_rejected']);self.assertEqual(len(p['assembly']['all_47_strict_slacks']),47)
 def test_copy_geometry_and_negative_controls(self):
  g=packet.read(packet.GLOBAL/'GEOMETRY-CONTROLS.json');e=packet.read(packet.GLOBAL/'EMISSION-CONTROLS.json');b=packet.read(packet.BANK/'CONTROLS.json')
  self.assertEqual((g['routes'],g['actual_center_projectors'],g['positive_copy_overrides']),(960,20,100));self.assertTrue(g['negative_center_projector_rejected']);self.assertEqual(g['boundary_ranks'],[38,38,19,19,42,42,4,4]);self.assertEqual(e['negative_controls'],12);self.assertEqual(b['count'],21)
 def test_manifest_and_path_protection(self):
  import run_checks
  with tempfile.TemporaryDirectory()as folder,patch.object(packet,'HERE',Path(folder)):
   with self.assertRaises(AssertionError):run_checks.check_packet()
  self.assertEqual(packet.portable({str(packet.GLOBAL/'RESULT.json'):[str(packet.INPUTS/'x')]}),{'$OUTPUT/global/RESULT.json':['$INPUTS/x']})
 def test_every_entrypoint_rejects_optimized_python(self):
  names=['run_checks.py','acquire_inputs.py']+[str(p.relative_to(packet.HERE))for d in ['source','frame','bank','lowering','audit']for p in sorted((packet.HERE/d).glob('*.py'))if p.name!='generic_ir_helpers.py']
  for name in names:
   r=subprocess.run([sys.executable,'-O',str(packet.HERE/name)],env=packet.child_env(),capture_output=True,text=True);self.assertNotEqual(r.returncode,0,name);self.assertIn('Assertions must be enabled',r.stderr,name)
if __name__=='__main__':unittest.main()
