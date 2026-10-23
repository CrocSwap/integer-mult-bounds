"""Portable packet integrity, corrected geometry, ledger and integration controls."""
from pathlib import Path
import copy, hashlib, json, os, subprocess, sys, unittest
import support

class PacketTests(unittest.TestCase):
    def test_source_pins_and_inert_program_names(self):
        support.verify_inputs()
        self.assertTrue(all(not r['local'].endswith('.py') for r in support.pins()['files']))
    def test_all_published_authored_dependencies(self): support.verify_dependencies()
    def test_modified_source_rejected(self):
        row=support.pins()['files'][0];raw=support.read_bytes(row['path'])
        with self.assertRaises(AssertionError):support.check_bytes(raw+b' ',row)
    def test_truncated_source_rejected(self):
        row=support.pins()['files'][0];raw=support.read_bytes(row['path'])
        with self.assertRaises(AssertionError):support.check_bytes(raw[:-1],row)
    def test_assertion_disabled_rejected(self):
        result=subprocess.run([sys.executable,'-O',str(support.HERE/'run_checks.py')],capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0);self.assertIn('assertions',result.stderr.lower())
    def test_exact_candidate(self):
        self.assertEqual(support.sha(support.WORD),support.WORD_SHA)
        self.assertNotEqual(hashlib.sha256(support.WORD.read_bytes()+b' ').hexdigest(),support.WORD_SHA)
    def test_admission_is_bound(self): support.verify_admission()
    def test_corrected_source_geometry(self):
        d=json.loads((support.FRAME/'SOURCE-GEOMETRY-CORRECTION.json').read_text())
        self.assertEqual((d['source_columns'],d['retimed_setups']),(960,480))
        self.assertEqual(sorted(r['source']for r in d['receipts']),list(range(960)))
        self.assertEqual(d['source_paid_histogram'],{'2':960,'17':960})
    def test_literal_ledger_and_rank_guard(self):
        d=json.loads((support.BANK/'split_49_11/RESULT.json').read_text())['literal_profile']
        self.assertEqual((d['stock'],d['children'],d['rank_mass'],d['deficit']),(658275,15002710,65705100,122400))
        self.assertEqual(max(map(int,d['histogram'])),49)
        self.assertLess(2*max(map(int,d['histogram'])),100)
    def test_conditional_kappa(self):
        d=json.loads((support.BANK/'split_49_11/ARITHMETIC-RESULT.json').read_text())
        self.assertEqual(d['assembly']['kappa'],'770003879871513/1000000000000000000')
        self.assertEqual(len(d['assembly']['all_47_strict_slacks']),47)
    def test_new_completion_phase_order(self):
        phases=json.loads((support.LOWER/'extended-phases.json').read_text())
        self.assertEqual(len(phases),730)
        for stage in range(5):
            helpers=[i for i,p in enumerate(phases)if p['kind']=='helper'and p['stage']==stage]
            completion=[i for i,p in enumerate(phases)if p['kind']=='paid_bank_completion'and p['stage']==stage]
            self.assertEqual(len(helpers),60);self.assertEqual([phases[i]['rank']for i in completion],[49,11])
            self.assertLess(max(helpers),min(completion))
    def test_independent_emitted_program_match(self):
        d=json.loads((support.AUDIT/'LOWERING-REVIEW.json').read_text())
        self.assertEqual((d['expanded_scalar_records'],d['boundary_records']),(100887900,921600))
        self.assertEqual(d['program_sha256'],'c0399f5386a5a0321021c9cb2e9ea79e122259af9e750b95a0ed0d0fe705def2')

    def test_full_local_frames_and_containment(self):
        d=json.loads((support.FRAME/'VALIDATION.json').read_text())
        self.assertEqual((d['frames'],d['records'],d['exact_MOVE_containment_pairs']),(15034,389223,44750))
        self.assertTrue(d['all_frame_G_nondegeneracy_certified'])
        self.assertEqual(d['zeroed_basis_row_controls_rejected'],15033)
    def test_full_global_frame_binding(self):
        d=json.loads((support.OUTPUT/'full-frame/RESULT.json').read_text())
        self.assertEqual(d['concrete_frame_stage_records'],116772900)
        self.assertEqual((d['paid_calls'],d['rank_mass'],d['strict_max_rank']),(15002710,65705100,49))
        self.assertTrue(d['actual_local_raw_frame_word_regenerated'])
        self.assertFalse(d['production_primitive_compiler_executed'])

    def test_positive_copied_work_projectors(self):
        d=json.loads((support.AUDIT/'GLOBAL-AUDIT.json').read_text())
        self.assertEqual(d['copy_overrides_checked'],100)
        self.assertEqual(len(d['actual_positive_center_projector_checks']),20)
        self.assertTrue(d['all_copy_negative_directions_rejected'])

    def test_stale_source_correction_producer_rejected(self):
        d=support.verify_correction()
        wrong=copy.deepcopy(d);wrong['checker_sha256']='0'*64
        with self.assertRaises(AssertionError):support.validate_correction(wrong)
        wrong=copy.deepcopy(d);wrong['previous_admission_manifest_sha256']='0'*64
        with self.assertRaises(AssertionError):support.validate_correction(wrong)

if __name__=='__main__':unittest.main()
