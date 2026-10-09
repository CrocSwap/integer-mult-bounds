"""Native wiring controls exercise scientific fields, bypassing source hashes."""
import copy
import json
import unittest
import verify as V
import profile_binding as P

class NativeBindingControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.native=P.load_native(V.HERE.parents[1])
        cls.inputs={n:json.loads((V.HERE/'inputs'/n).read_bytes()) for n in P.INPUT_NAMES}
    def test_full_native_binding(self):
        result=P.bind_objects(self.native,self.inputs)
        self.assertEqual(result['zero_rank_target_events'],{'native':6270,'independent_literal_recount':6323,'difference':53})
    def test_positive_paid_component_changed(self):
        inputs=copy.deepcopy(self.inputs);inputs['paired-cube-sinks-input.json']['target_data_histogram']['1']-=1
        with self.assertRaisesRegex(ValueError,'native target_data_histogram mismatch'):P.bind_objects(self.native,inputs)
    def test_logical_reserve_collapsed(self):
        inputs=copy.deepcopy(self.inputs);inputs['paired-cube-complex-input.json']['R']=10688
        with self.assertRaisesRegex(ValueError,'logical scalar profile'):P.bind_objects(self.native,inputs)
    def test_terminal_removal_count_changed(self):
        inputs=copy.deepcopy(self.inputs);inputs['paired-cube-sinks-input.json']['sinks']=43
        with self.assertRaisesRegex(ValueError,'copied terminal population'):P.bind_objects(self.native,inputs)
    def test_zero_rank_is_reported_without_paid_child(self):
        inputs=copy.deepcopy(self.inputs);inputs['paired-cube-sinks-input.json']['target_data_histogram']['0']+=1
        before=P.bind_objects(self.native,self.inputs);after=P.bind_objects(self.native,inputs)
        self.assertEqual(before['paid_component_sha256'],after['paid_component_sha256'])
        self.assertEqual(after['zero_rank_target_events']['difference'],54)

if __name__=='__main__':unittest.main()
