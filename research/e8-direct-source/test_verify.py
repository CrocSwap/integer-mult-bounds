#!/usr/bin/env python3
"""Independent modular character replay of the physical chronological word."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('candidate',HERE/'verify.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)


def physical(data,events,direction,p,i,character,seed=26):
    def coefficient(q):return q.numerator*pow(q.denominator,-1,p)%p
    phases={}
    def phase(P):
        if P not in phases:
            image=sum((bin(row & character).count('1')%2)<<j for j,row in enumerate(P))
            phases[P]=pow(i,bin(image).count('1'),p)
        return phases[P]
    z=[((j+seed+1)**3+17*j+1)%p for j in range(len(data['initial']))]
    initial=list(z);frames=list(data['initial'])
    adds=[(t,s,coefficient(q)) for t,s,q in data['helper_adds']]
    B=[[coefficient(q) for q in row] for row in data['B']]
    coeffs={q:coefficient(q) for _,_,q in data['adds']}
    for event in events:
        kind=event[0]
        if kind=='move':
            _,r,P=event
            z[r]=z[r]*phase(P)*pow(phase(frames[r]),-1,p)%p;frames[r]=P
        elif kind in ('add','output','cleanup'):
            _,t,s,q=event
            a=coeffs.get(q)
            if a is None:a=coefficient(q)
            if direction=='backward':t,s,a=s,t,-a
            z[t]=(z[t]+a*z[s])%p
        elif kind=='old':
            tmp=[0]*len(z)
            if direction=='forward':
                for r in data['helpers']:tmp[r]=z[r]
                for t,s,a in adds:tmp[t]=(tmp[t]+a*tmp[s])%p
                for t,r in enumerate(data['outputs']):
                    response=tmp[r]+sum(B[t][j]*tmp[g] for j,g in enumerate(data['centers']))
                    z[120+t]=(z[120+t]-response)%p
            else:
                for t,r in enumerate(data['outputs']):tmp[r]=z[120+t]
                for j,r in enumerate(data['centers']):tmp[r]=sum(B[t][j]*z[120+t] for t in range(120))%p
                for t,s,a in reversed(adds):tmp[s]=(tmp[s]+a*tmp[t])%p
                for r in data['helpers']:z[r]=(z[r]+tmp[r])%p
        elif kind=='centers':
            full=phase(c.I)
            if direction=='forward':
                # Actual private copied centers descend FULL -> ZERO.
                bank=[z[r]*pow(full,-1,p)%p for r in data['centers']]
                for t in range(120):z[120+t]=(z[120+t]+sum(B[t][j]*bank[j] for j in range(8)))%p
            else:
                # B^T y at zero, then actual ZERO -> FULL children.
                bank=[sum(B[t][j]*z[120+t] for t in range(120))*full%p for j in range(8)]
                for j,r in enumerate(data['centers']):z[r]=(z[r]-bank[j])%p
    expected=[a*phase(c.I)%p for a in initial]
    for t in range(120):
        logical_x=initial[t]*pow(phase(data['initial'][t]),-1,p)%p
        cap=phase(c.ref.bitadd(c.I,c.ref.outer(data['ports'][t],9)))
        if direction=='forward':
            expected[t]=logical_x*phase(c.I)%p
            expected[120+t]=(initial[120+t]+logical_x)*cap%p
        else:
            expected[t]=(logical_x-initial[120+t])*phase(c.I)%p
            expected[120+t]=initial[120+t]*cap%p
    return z==expected


class Checks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.data=c.build()

    def test_physical_character_replay(self):
        chars=[0]+[1<<j for j in range(9)]+[511,26]
        count=0
        for p,i in [(101,10),(109,33)]:
            self.assertEqual(i*i%p,p-1)
            for direction in ['forward','backward']:
                events=c.word(self.data,direction)
                for character in chars:
                    self.assertTrue(physical(self.data,events,direction,p,i,character))
                    count+=1
        self.assertEqual(count,48)

    def test_moment_separates_profiles(self):
        from fractions import Fraction as Q
        new={1:40680,2:240,7:20160,8:1080,9:48}
        old={1:41040,2:240,7:20160,8:1440,9:48}
        lo,_=c.moment(new,7088,Q(1,14100))
        _,hi=c.moment(old,7208,Q(1,14100))
        self.assertGreater(lo,Q(11,100));self.assertLess(hi,0)

    def test_optimized_execution_refuses_before_output(self):
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)/'receipt.json'
            proc=subprocess.run([sys.executable,'-B','-I','-O',str(HERE/'verify.py'),'--output',str(output)],capture_output=True,text=True)
            self.assertNotEqual(proc.returncode,0)
            self.assertIn('Refusing optimized Python',proc.stderr)
            self.assertFalse(output.exists())


if __name__=='__main__':unittest.main()
