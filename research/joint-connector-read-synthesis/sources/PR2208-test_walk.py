#!/usr/bin/env python3
"""Happy-path and failure controls for charged F2 walks and locality bounds."""
from collections import Counter
from fractions import Fraction
from itertools import product
import json
import heapq
from pathlib import Path
import random
import unittest

import families as f
import verify as v
import walk

HERE = Path(__file__).resolve().parent


class WalkTests(unittest.TestCase):
    def test_transfer_bill_depends_on_minimum_read_decomposition(self):
        # Counterexample supplied by the PR9 reviewer. Both words have the
        # minimum read bill, but our chosen decomposition costs more transfers.
        source=[2,0,1,2,1,0];colors=[1,2,1]
        automatic,counts=walk.construct(source,colors)
        alternative=[['A',4,0],['A',5,0],['B',2,0],['A',1,0],['A',4,0],
                     ['B',0,0],['A',1,0],['A',5,0],['C',0],['C',1],
                     ['B',1,0],['A',6,0],['A',7,0],['C',1],['B',2,0],
                     ['A',2,0],['A',3,0],['C',1],['B',1,0],['A',2,0],
                     ['A',6,0],['C',1],['B',0,0],['A',3,0],['A',7,0],['C',0]]
        v.check_endpoint(automatic,3,2);v.check_endpoint(alternative,3,2)
        self.assertEqual(counts['readout_calls'],14)
        self.assertEqual(sum(op[0]=='A' for op in alternative),14)
        self.assertEqual(counts['transfers'],10)
        self.assertEqual(sum(op[0]=='C' for op in alternative),6)
        self.assertEqual([op[1] for op in alternative if op[0]=='B'],source)
        self.assertTrue(all(op[2]==0 for op in alternative if op[0] in ('A','B')))
        index=next(i for i,op in enumerate(alternative) if op[0]=='C')
        with self.assertRaises(ValueError):
            v.check_endpoint(alternative[:index]+alternative[index+1:],3,2)

    def test_shortest_read_plan_against_independent_small_enumeration(self):
        for source in ([0,1,2,0,1,2], [0,0,1,1,2,2]):
            colors=[1,2,3]
            plan,hist=walk.readout_plan(source,colors)
            current=[0,0];queries=set()
            for label in [None,*source]:
                if label is not None:
                    if colors[label]&1:current[0]^=1<<label
                    if colors[label]&2:current[1]^=1<<label
                queries.update((d<<3)|value for d,value in
                               ((1,current[0]),(2,current[1]),(3,current[0]^current[1])))
            distances={0:0};layer={0}
            for length in range(1,7):
                layer={a^b for a in layer for b in queries}
                for value in layer:distances.setdefault(value,length)
            self.assertEqual(set(distances),set(range(32)))
            for mask,reads in plan.items():self.assertEqual(len(reads),distances[mask])
            word,counts=walk.construct(source,colors)
            v.check_endpoint(word,3,2)
            self.assertEqual(counts['readout_calls'],sum(map(len,plan.values())))

    def test_placement_dp_against_whole_graph_shortest_path(self):
        source=[0,1,2,0,1,2];colors=[1,2,3]
        plan,_=walk.readout_plan(source,colors);images=walk.source_cuts(source,colors)
        keys=sorted({(d,images[cut][d-1]) for reads in plan.values() for cut,d in reads})
        indices={key:i for i,key in enumerate(keys)}
        full=(1<<len(keys))-1
        def served(cut,frame,done):
            key=(frame[0],images[cut][frame[0]-1])
            return done | ((1<<indices[key]) if key in indices else 0)
        initial=(0,(1,2),served(0,(1,2),0))
        queue=[(0,initial)];best={initial:0};answer=None
        while queue:
            cost,(cut,frame,done)=heapq.heappop(queue)
            if cost!=best[cut,frame,done]:continue
            if cut==len(source) and frame==(1,2) and done==full:
                answer=cost;break
            following=[]
            for port in (0,1):
                after=walk.change(frame,port)
                following.append((cost+1,(cut,after,served(cut,after,done))))
            if cut<len(source):
                color=colors[source[cut]]
                if (frame[0]&color).bit_count()%2==1 and (frame[1]&color).bit_count()%2==0:
                    following.append((cost,(cut+1,frame,served(cut+1,frame,done))))
            for value,state in following:
                if value<best.get(state,float('inf')):
                    best[state]=value;heapq.heappush(queue,(value,state))
        self.assertIsNotNone(answer)
        self.assertEqual(walk.construct(source,colors)[1]['transfers'],answer)

    def test_complete_fixed_port_program_and_invoice(self):
        fixture=json.loads((HERE/'WALKS.json').read_text())
        for record in fixture['records']:
            word,counts=walk.construct(record['source_word'],record['colors'])
            n=len(record['colors'])
            v.check_endpoint(word,n,2)
            self.assertEqual(counts,record['counts'])
            self.assertTrue(all(op[2]==0 for op in word if op[0] in ('A','B')))
            b=record['source_price'];cost=counts['source_calls']*b+counts['readout_calls']+counts['transfers']
            self.assertEqual(cost,record['query_cost'])
            self.assertLess(cost,f.locality_lower_bound(n,b,1,1))
            self.assertEqual(Counter(op[1] for op in word if op[0]=='B'),Counter({j:2 for j in range(n)}))

    def test_every_short_program_omission_and_dirty_signatures(self):
        word,_=walk.construct([0,1,2,0,1,2],[1,2,3])
        for i in range(len(word)):
            with self.subTest(index=i),self.assertRaises(ValueError):
                v.check_endpoint(word[:i]+word[i+1:],3,2)
        for kind in ('A','B','C'):
            changed=[list(op) for op in word];index=next(i for i,op in enumerate(changed) if op[0]==kind)
            changed[index][-1]^=1
            with self.assertRaises(ValueError):v.check_endpoint(changed,3,2)

    def test_requested_subset_preserves_every_unrequested_output(self):
        source=[0,1,2,0,1,2];colors=[1,2,3];targets=(1,5,7)
        word,counts=walk.construct(source,colors,targets)
        want=v.expected(3,2)
        for mask in range(1,8):
            if mask not in targets:want[f'y{mask}']={(f'y{mask}',)}
        out=v.interpret(word,v.initial(3,2),3,2)
        self.assertEqual(out,want)
        self.assertEqual(v.interpret(list(reversed(word)),out,3,2),v.initial(3,2))
        self.assertEqual(counts['target_outputs'],len(targets))
        self.assertTrue(all(op[1] in targets for op in word if op[0]=='A'))
        for bad in ((),(0,),(8,),(True,),(1,1)):
            with self.assertRaises(ValueError):walk.construct(source,colors,bad)

    def test_locality_exact_global_minimum_without_finite_cutoff(self):
        for n in range(1,11):
            for roots,b in product((1,2),(Fraction(1,3),1,3,49)):
                step=2 if roots==1 else 1;M=(1<<n)-1;base=4 if roots==1 else 3
                upper=2*n
                while f.locality_capacity(n,upper,roots)<M:upper+=step
                brute=min(k*b+max(2*M,base*M-(base-2)*f.locality_capacity(n,k,roots))
                          for k in range(2*n,upper+step,step))
                self.assertEqual(f.locality_lower_bound(n,b,1,roots),brute)
                self.assertGreaterEqual(brute,f.global_lower_bound(n,b,1,roots))
        self.assertEqual(f.locality_lower_bound(9,49,1,1),2638)

    def test_locality_cover_on_actual_closed_unit_walks(self):
        rng=random.Random(4097)
        for n in (3,6,9):
            for _ in range(30):
                source=list(range(n))*2;rng.shuffle(source)
                colors=[rng.randrange(1,4) for _ in range(n)]
                current=[0,0];prefixes=[]
                for label in source:
                    prefixes.append(tuple(current))
                    if colors[label]&1:current[0]^=1<<label
                    if colors[label]&2:current[1]^=1<<label
                paired=set()
                for p,q in product(prefixes,repeat=2):
                    a,b=p[0]^q[0],p[1]^q[1]
                    paired.update((a,b,a^b))
                paired.discard(0)
                self.assertLessEqual(len(paired),f.locality_capacity(n,2*n,2))
                current=0;one=[]
                for label in source:one.append(current);current^=1<<label
                single={a^b for a,b in product(one,repeat=2)}-{0}
                self.assertLessEqual(len(single),f.locality_capacity(n,2*n,1))

    def test_minimum_source_lower_bound_on_actual_read_graphs(self):
        rng=random.Random(7719)
        for n in (3,5,6,9):
            bound=walk.minimum_source_invoice(n,3,2)
            for _ in range(12):
                source=list(range(n))*2;rng.shuffle(source)
                colors=[rng.randrange(1,4) for _ in range(n)]
                plan,_=walk.readout_plan(source,colors)
                self.assertLessEqual(bound['query_lower_bound'],2*n*3+2*sum(map(len,plan.values())))
        self.assertEqual(walk.minimum_source_invoice(9,49,1)['query_lower_bound'],2251)
        for n,b,a in ((13,1,1),(9,0,1),(9,1,0)):
            with self.assertRaises(ValueError):walk.minimum_source_invoice(n,b,a)

    def test_invalid_or_unrestored_source_walks(self):
        for source,colors in (([0,1,2],[1,2,3]),([0,0,1,1,2,2],[1,0,3]),
                              ([0,0,1,1,True,True],[1,2,3]),(list(range(13))*2,[1]*13)):
            with self.assertRaises(ValueError):walk.construct(source,colors)
        for roots in (0,3):
            with self.assertRaises(ValueError):f.locality_lower_bound(9,1,1,roots)
        with self.assertRaises(ValueError):f.locality_lower_bound(9,0,1,1)
        with self.assertRaises(ValueError):f.locality_capacity(9,17,1)


if __name__=='__main__':unittest.main()
