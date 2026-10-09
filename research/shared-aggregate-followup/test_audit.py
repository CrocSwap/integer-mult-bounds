"""Exact positive and assumption-failure controls for the follow-up."""
import unittest
import audit as a
d=a.d


def swap(P):
    A=d.sub(d.eye(len(P)),P)
    return [r+s for r,s in zip(A,P)]+[s+r for r,s in zip(A,P)]


class FollowupTests(unittest.TestCase):
    def test_pair_scalar_maps_and_span_counts(self):
        for h in (6,7,11):
            r=a.paired_readout(h)
            self.assertEqual(r['readout_rank'],2*h)
            self.assertFalse(r['producer_supplied'])
        h=10;S={0,1,2};T={0,1,3};G=d.metric(h)
        rows=d.independent([d.vector(R,h) for R in d.triples(h) if len(set(R)&S)==1 and len(set(R)&T)!=1])
        self.assertEqual(len(rows),8)
        self.assertEqual(d.rank(d.product(d.product(rows,G),d.transpose(rows))),7)
        with self.assertRaises(AssertionError):a.paired_readout(h)

    def test_pair_physical_readout_paths(self):
        h=6;G=d.metric(h);S={0,1,2};T={0,1,3}
        K=d.sub(d.eye(h),d.projector([d.vector(S,h),d.vector(T,h)],G))
        FK=swap(K)
        for target in (S,T):
            H=d.sub(d.eye(h),d.projector([d.vector(target,h)],G));FH=swap(H)
            exit=d.product(FH,FK)
            self.assertEqual(d.product(exit,FK),FH)  # central entry 0 -> K -> H
            self.assertNotEqual(exit,FH)             # omitting its frame is wrong
            other=T if target==S else S
            unique=[R for R in d.triples(h) if len(set(R)&target)==1 and len(set(R)&other)!=1]
            L=d.projector([d.vector(R,h) for R in unique],G)
            FL=swap(L)
            self.assertEqual(d.rank(d.sub(H,L)),1)
            self.assertEqual(d.product(d.product(FH,FL),FL),FH)
            self.assertNotEqual(FL,FH)

    def test_pairwise_frame_separation(self):
        r=a.source_distances()
        self.assertEqual(r['pairs_checked'],190)
        self.assertEqual(r['sources'],20)

    def test_shared_cancelling_graph_and_sharpness(self):
        r=a.forest_examples()
        self.assertEqual(r['sharp_star']['total_edge_rank'],5)
        self.assertEqual(r['shared_cancellation_dag']['source_floor'],5)
        self.assertEqual(r['dag_scalar_outputs'],[29,6])

    def test_coincident_sources_escape_separation(self):
        P=d.line_projectors(6)[0];Z=d.sub(P,P)
        # Two identical frames merge for free, then one rank-one move.
        frames=[P,P,P,Z];edges=[(0,2),(1,2),(2,3)]
        self.assertEqual(sum(d.rank(d.sub(frames[u],frames[v])) for u,v in edges),1)
        with self.assertRaisesRegex(AssertionError,'source separation'):
            a.forest_control(frames,edges,[0,1],[3])

    def test_changed_frontier_and_unused_input_are_outside_bound(self):
        P=d.line_projectors(6)[0];Z=d.sub(P,P)
        with self.assertRaisesRegex(AssertionError,'root separation'):
            a.forest_control([P,P],[(0,1)],[0],[1])
        with self.assertRaisesRegex(AssertionError,'reach the frontier'):
            a.forest_control([P,Z],[],[0],[1])

    def test_budget_saturation_not_an_exponent(self):
        r=a.budget_consequence()
        self.assertEqual(r['total_rank_floor'],r['useful_rank_capacity'])
        self.assertEqual(r['extra_rank_floor'],1265)
        self.assertEqual(r['shortfall_at_that_profile'],12)
        self.assertGreater(a.Q(r['boundary_singleton_profile_moment'][0]),1)


if __name__=='__main__':unittest.main()
