"""Mathematical failure controls for the coupled gauge result, Apache-2.0."""
import copy
import importlib.util
import itertools
import json
from pathlib import Path
import random
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('coupled_verify',HERE/'verify.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)

class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prior,cls.lib=v.sources()
        cls.word,cls.programs,*_=cls.lib.load()
        cls.helpers=cls.prior.domain(cls.lib,cls.word,cls.programs)
        cls.cert=json.loads((HERE/'CERTIFICATE.json').read_bytes())

    def test_complete_receipt(self):
        self.assertEqual(v.canonical(v.compute()),v.canonical(self.cert))

    def test_single_stationarity_and_joint_escape(self):
        raw=json.loads((HERE/'vendor/pr1263/GAUGES.json').read_bytes())
        for orientation in ('forward','backward'):
            gauges={int(h):k for h,k in raw[orientation].items()}
            terms=self.prior.terms_from(self.lib,self.programs[orientation],self.helpers)
            for h in self.helpers:
                values=dict(self.prior.coordinate_candidates(terms,gauges,h))
                self.assertEqual(min(values.values()),values[gauges.get(h,0)])
            row=self.cert['orientations'][orientation]['trace'][0]
            self.assertEqual(len(row['improving_pairs']),2)
            win=row['winner']
            self.assertEqual(win['separate_single_delta_real'],2)
            self.assertEqual(win['delta_real'],-2)
            self.assertNotEqual(win['delta_real'],win['separate_single_delta_real'])

    def test_all_integer_arrangement_against_tiny_exhaustion(self):
        rng=random.Random(35)
        for trial in range(80):
            helpers=[0,1,2]
            gauges={h:rng.randrange(-2,3) for h in helpers}
            events=[]
            for _ in range(6):
                t,s=rng.sample([-1,0,1,2],2)
                q=self.lib.Q(rng.choice([1,3]),1)*self.lib.power(rng.randrange(-2,3))
                reg=lambda h:['L',h] if h!=-1 else ['C',0]
                events.append(['scalar',['add',reg(t),reg(s),q.numerator,q.denominator],0])
            result=v.exact_census(self.lib,events,helpers,gauges)
            terms=self.prior.terms_from(self.lib,events,helpers)
            before=self.prior.objective(terms,gauges)
            # All vertices lie within [-14,14] for these bounded inputs.
            for row in result['rows']:
                a,b=row[:2]
                best=min(self.prior.objective(terms,{**gauges,a:gauges[a]+x,b:gauges[b]+y})-before
                         for x in range(-14,15) for y in range(-14,15))
                self.assertEqual(row[3],best)

    def test_boundary_omissions_break_dirty_restoration(self):
        for orientation in ('forward','backward'):
            gauges={int(h):k for h,k in self.cert['orientations'][orientation]['gauges'].items()}
            good=self.prior.transform(self.lib,self.word,self.programs[orientation],gauges)
            for index in (1,len(good)-2):
                bad=copy.deepcopy(good);bad.pop(index)
                with self.assertRaises(ValueError):self.lib.replay(bad,orientation)

    def test_wrong_backward_gauge_or_coefficient_breaks_map(self):
        for orientation in ('forward','backward'):
            gauges={int(h):k for h,k in self.cert['orientations'][orientation]['gauges'].items()}
            good=self.prior.transform(self.lib,self.word,self.programs[orientation],gauges)
            bad=copy.deepcopy(good)
            entry=bad[1][1];entry[2],entry[3]=entry[3],entry[2]
            with self.assertRaises(ValueError):self.lib.replay(bad,orientation)
            bad=copy.deepcopy(good)
            gate=next(e[1] for e in bad if e[0]=='scalar' and e[1][0]=='add' and e[1][1]==['L',400])
            gate[3]*=2
            with self.assertRaises(ValueError):self.lib.replay(bad,orientation)

    def test_false_all_pair_claim_and_source_mutation(self):
        changed=copy.deepcopy(self.cert)
        changed['orientations']['forward']['trace'][-1]['pair_minima_sha256']='0'*64
        with self.assertRaises(ValueError):v.check_certificate(self.cert,changed)
        # Actual vendored source corruption in an isolated copy, not the repository.
        import tempfile,shutil
        with tempfile.TemporaryDirectory(prefix='coupled source control ') as tmp:
            target=Path(tmp);shutil.copytree(HERE/'vendor',target/'vendor');shutil.copy(HERE/'PREDECESSORS.json',target)
            old=v.HERE;v.HERE=target
            try:
                f=target/'vendor/pr1263/GAUGES.json';f.write_bytes(f.read_bytes()+b' ')
                with self.assertRaises(ValueError):v.sources()
            finally:v.HERE=old

    def test_independent_grid_and_literal_replay(self):
        module=v.load_module('coupled_independent',HERE/'independent.py')
        got=module.check()
        self.assertEqual(got,json.loads((HERE/'INDEPENDENT.json').read_bytes()))

if __name__=='__main__':unittest.main()
