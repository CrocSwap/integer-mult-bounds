"""Exact signed linear maps, adjoint signs and inverse/reflection contracts."""
import unittest
import independent_sinks as C

class Signed(unittest.TestCase):
    def test_signed_adjoint_basis(self):
        # The transpose of [[ca,cb],[0,1]] sends a destination covector
        # (1,0) to (ca,cb), and a source covector (0,1) to itself.
        for ca in (-1,1):
            for cb in (-1,1):
                C.check_response_correspondence([(1,0,0)],[(ca,cb)],[0],
                    {1:{0:1}},{0:{0:1}},[{0:cb},{0:ca}],[{0:1},{}],2)
                with self.assertRaisesRegex(ValueError,'adjoint responses equal'):
                    C.check_response_correspondence([(1,0,0)],[(ca,cb)],[0],
                        {1:{0:1}},{0:{0:1}},[{0:cb},{0:-ca}],[{0:1},{}],2)

    def protocol(self):
        p=C.Protocol.__new__(C.Protocol);p.v=1;p.h=1;p.inputs=[1];p.live=[0,1];p.meter=C.Meter()
        p.cs={};p.ds={};p.c=[{},{}];p.d=[{},{}]
        return p

    def events(self,cb):
        # A reflection is its own inverse. The independent X->Y translation
        # occurs while dirty registers carry arbitrary reflected values.
        gate={'kind':'signed_add','dest':('Z',0),'source':('Z',1),'sign':-1,'factor':(cb,1)}
        return [dict(gate),{'kind':'add','dest':('Y',0),'source':('X',0),'factor':(1,1)},dict(gate)]

    def test_both_reflections_preserve_arbitrary_dirty(self):
        for cb in (-1,1):
            p=self.protocol();events=self.events(cb)
            self.assertEqual(p.replay(events)['formal_basis'],4)
            self.assertTrue(p.replay(p.reflected(events),True)['reflected'])

    def test_wrong_signed_inverse_rejected(self):
        for cb in (-1,1):
            p=self.protocol();events=self.events(cb);events[-1]['factor']=(-cb,1)
            with self.assertRaisesRegex(C.IdentityError,'dirty restore'):p.replay(events)

    def test_missing_reflection_sign_rejected(self):
        p=self.protocol();events=self.events(1);events[0]['sign']=1
        with self.assertRaisesRegex(C.IdentityError,'dirty restore'):p.replay(events)

    def test_reflection_inverse_is_same_map(self):
        p=self.protocol()
        for cb in (-1,1):
            e=self.events(cb)[0];self.assertEqual(p.reflected([e])[0],e)

    def test_row_sign_domain(self):
        for sign in (True,False,0,2,0.5):
            with self.assertRaisesRegex(ValueError,'exact row sign'):C.Row({0:1}).scale(sign,C.Meter())

    def test_same_port_signed_gate_rejected(self):
        p=self.protocol();event=self.events(1)[0];event['source']=event['dest']
        with self.assertRaisesRegex(ValueError,'distinct signed row ports'):p.replay([event])

if __name__=='__main__':unittest.main(verbosity=2)
