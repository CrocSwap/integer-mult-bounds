import unittest
import independent_sinks as check

class Arithmetic(unittest.TestCase):
    def test_adaptive_denominator(self):
        meter=check.Meter()
        a=check.Row({0:1}); b=check.Row({1:1},2)
        a.add(b,(1,3),meter)
        self.assertEqual(a.denominator,6)
        self.assertEqual(a.data,{0:6,1:1})
        a.add(b,(-1,3),meter)
        self.assertTrue(a.equals({0:1}))
    def test_self_port_refused(self):
        a=check.Row({0:1})
        with self.assertRaisesRegex(ValueError,'distinct row'): a.add(a,(1,1),check.Meter())
    def test_boolean_factor_refused(self):
        with self.assertRaisesRegex(ValueError,'exact factor'):
            check.Row().add(check.Row({0:1}),(True,1),check.Meter())
    def test_float_and_boolean_rows_refused(self):
        for row in ({0:0.5},{True:1},{0:True},{0:0}):
            with self.assertRaisesRegex(ValueError,'exact sparse integer row'): check.Row(row)
    def test_binary_complement(self):
        for a in range(16):
            for b in range(16):
                basis=check.binary_basis((a,b))
                perp=check.complement(basis,4)
                self.assertEqual(len(basis)+len(perp),4)
                self.assertTrue(all(not((x&y).bit_count()%2) for x in basis for y in perp))
    def test_source_label_convention_enforced(self):
        graph={'h':1,'inputs':[1]*8,'labels':[[0]]*7+[[]]}
        with self.assertRaisesRegex(ValueError,'labels and source'):
            check.Protocol(graph,{}, {}, [], [], [],check.Meter())
    def test_disjoint_reorder_keeps_all_responses(self):
        result=check.check_response_correspondence([(1,0,0),(3,2,0)],[(1,1),(1,-1)],[1,0],
                     {1:{0:1}},{3:{0:1}},[{0:1},{0:1},{},{}],[{},{},{0:-1},{0:1}],4)
        self.assertTrue(result['per_role_order_preserved'])
    def test_shared_port_reorder_refused(self):
        with self.assertRaisesRegex(ValueError,'per-role'):
            check.check_response_correspondence([(1,0,0),(2,1,0)],[(1,1),(1,1)],[1,0],{},{},[{}, {}, {}],[{}, {}, {}],3)
    def test_wrong_response_refused(self):
        with self.assertRaisesRegex(ValueError,'adjoint responses equal'):
            check.check_response_correspondence([(1,0,0)],[(1,1)],[0],{1:{0:1}},{},[{}, {0:1}],[{}, {}],2)
    def protocol(self):
        p=check.Protocol.__new__(check.Protocol)
        p.v=1; p.h=1; p.inputs=[1]; p.live=[0]; p.meter=check.Meter()
        p.cs={};p.ds={};p.c=[{}];p.d=[{}]
        return p
    def test_full_target_basis_and_reflection(self):
        p=self.protocol()
        events=[{'kind':'add','dest':('Y',0),'source':('X',0),'factor':(1,1)}]
        self.assertEqual(p.replay(events)['formal_basis'],3)
        self.assertTrue(p.replay(p.reflected(events),True)['reflected'])
    def test_read_target_identity_corruption_detected(self):
        p=self.protocol()
        events=[{'kind':'add','dest':('Y',0),'source':('X',0),'factor':(1,1)},
                {'kind':'add','dest':('X',0),'source':('Y',0),'factor':(1,1)}]
        with self.assertRaisesRegex(check.IdentityError,'source bank'): p.replay(events)
    def test_dirty_corruption_detected(self):
        p=self.protocol()
        events=[{'kind':'add','dest':('Y',0),'source':('X',0),'factor':(1,1)},
                {'kind':'add','dest':('Z',0),'source':('Y',0),'factor':(1,2)}]
        with self.assertRaisesRegex(check.IdentityError,'dirty restore'): p.replay(events)
    def test_immediate_center_flush_before_target_control(self):
        p=self.protocol();p.cs={0:{0:1}}
        events=[{'kind':'read','source':('Z',0),'role':0,'sign':1,'seed':True,'bank':'Y'},
                {'kind':'add','dest':('X',0),'source':('Y',0),'factor':(1,1)},
                {'kind':'read','source':('Z',0),'role':0,'sign':-1,'seed':True,'bank':'Y'},
                {'kind':'add','dest':('X',0),'source':('Y',0),'factor':(-1,1)},
                {'kind':'add','dest':('Y',0),'source':('X',0),'factor':(1,1)}]
        # A delayed scatter would cancel the pending reads and falsely pass.
        # Correct scheduling transfers a nonzero dirty coefficient to X.
        with self.assertRaisesRegex(check.IdentityError,'source bank'): p.replay(events)

if __name__=='__main__': unittest.main(verbosity=2)
