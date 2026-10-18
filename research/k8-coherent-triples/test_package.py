"""Exact coverage, accounting and dirty-interface failure controls."""
import copy
import importlib.util
from itertools import combinations
import json
from pathlib import Path
import random
import tempfile
import shutil
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('coherent_verify',HERE/'verify.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)

class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pair,cls.prior,cls.lib=v.sources();cls.word,cls.programs,*_=cls.lib.load()
        cls.helpers=cls.prior.domain(cls.lib,cls.word,cls.programs)
        cls.cert=json.loads((HERE/'CERTIFICATE.json').read_bytes())

    def test_full_certificate(self):
        v.check_certificate(v.compute(),self.cert)

    def test_literal_cut_oracle(self):
        independent=v.module('independent_coherent',HERE/'independent.py')
        self.assertEqual(v.canonical(independent.run()),v.canonical(json.loads((HERE/'INDEPENDENT.json').read_bytes())))

    def test_proper_subsets_cannot_take_initial_step(self):
        data=json.loads((HERE/'vendor/pr1310/CERTIFICATE.json').read_bytes())
        for orientation in ('forward','backward'):
            gauges={int(h):k for h,k in data['orientations'][orientation]['gauges'].items()}
            terms=self.prior.terms_from(self.lib,self.programs[orientation],self.helpers)
            base=self.prior.objective(terms,gauges);shift=-1 if orientation=='forward' else 1
            group=[354,469,478];deltas=[]
            for n in (1,2,3):
                for S in combinations(group,n):
                    changed=dict(gauges)
                    for h in S:changed[h]=changed.get(h,0)+shift
                    delta=self.prior.objective(terms,changed)-base;deltas.append((n,delta))
                    self.assertGreaterEqual(delta,0) if n<3 else self.assertEqual(delta,-2)
            # Pricing three independent changes drops their shared-edge cancellation.
            self.assertNotEqual(sum(d for n,d in deltas if n==1),-2)

    def test_synthetic_integer_grid_all_subsets(self):
        rng=random.Random(37)
        # Do not assume stationarity: compare every subset directly, including
        # odd dyadics, repeated edges, external sources and absent interactions.
        for trial in range(60):
            helpers=list(range(5));gauges={h:rng.randrange(-3,4) for h in helpers}
            terms=[]
            for _ in range(18):
                t,s=rng.sample([-1]+helpers,2)
                terms.append((bool(rng.randrange(2)),rng.randrange(-3,4),t,s))
            shifts,singles,corr,adj=v.curves(terms,helpers,gauges);zero=[0]*len(shifts)
            baseline=self.prior.objective(terms,gauges)
            for n in (1,2,3):
                for S in combinations(helpers,n):
                    table=[sum(singles[h][i] for h in S)+sum(corr.get(pair,zero)[i] for pair in combinations(S,2)) for i in range(len(shifts))]
                    direct=[]
                    for d in range(-15,16):
                        changed=dict(gauges)
                        for h in S:changed[h]+=d
                        direct.append(self.prior.objective(terms,changed)-baseline)
                    self.assertEqual(min(table),min(direct))
                    for i,d in enumerate(shifts):self.assertEqual(table[i],direct[d+15])

    def test_dirty_boundary_and_coefficient_faults(self):
        for orientation in ('forward','backward'):
            gauges={int(h):k for h,k in self.cert['orientations'][orientation]['gauges'].items()}
            good=self.prior.transform(self.lib,self.word,self.programs[orientation],gauges)
            entries=[i for i,e in enumerate(good) if e[0]=='scalar' and e[1][0]=='scale' and e[1][1]==['L',354]]
            for index in (entries[0],entries[-1]):
                bad=copy.deepcopy(good);bad.pop(index)
                with self.assertRaises(ValueError):self.lib.replay(bad,orientation)
            bad=copy.deepcopy(good);g=bad[entries[0]][1];g[2],g[3]=g[3],g[2]
            with self.assertRaises(ValueError):self.lib.replay(bad,orientation)
            bad=copy.deepcopy(good);g=next(e[1] for e in bad if e[0]=='scalar' and e[1][0]=='add' and e[1][1]==['L',354]);g[3]*=2
            with self.assertRaises(ValueError):self.lib.replay(bad,orientation)

    def test_unit_discount_and_paid_boundaries_are_not_optional(self):
        lower=v.module('control_lower',v.ROOT/'research/complex-dyadic-lowering/lower.py')
        # Concrete lowerer controls: |e| alone misses the isolated unit discount.
        prices=[len(lower.lower(['add',['L',0],['L',1],(self.lib.power(e)).numerator,(self.lib.power(e)).denominator])) for e in (-2,-1,0,1,2)]
        self.assertEqual(prices,[5,4,2,4,5]);self.assertNotEqual(prices,[5,4,3,4,5])
        self.assertEqual([2*len(lower.lower(['scale',['L',0],2**k,1])) for k in range(4)],[0,2,4,6])

    def test_certificate_and_source_corruptions(self):
        for key in ['triple_minima_sha256','connected_triples','disconnected_triples','evaluations']:
            bad=copy.deepcopy(self.cert);bad['orientations']['forward']['trace'][0][key]=None
            with self.assertRaises(ValueError):v.check_certificate(self.cert,bad)
        with tempfile.TemporaryDirectory(prefix='coherent source control ') as tmp:
            target=Path(tmp);shutil.copytree(HERE/'vendor',target/'vendor');shutil.copy(HERE/'PREDECESSORS.json',target)
            for relative in ['vendor/pr1310/CERTIFICATE.json','vendor/pr1310/vendor/pr1263/vendor/pr1161/engine.py']:
                p=target/relative;p.chmod(0o644);original=p.read_bytes();p.write_bytes(original+b' ');old=v.HERE;v.HERE=target
                try:
                    with self.assertRaises(ValueError):v.sources()
                finally:v.HERE=old;p.write_bytes(original)

if __name__=='__main__':unittest.main()
