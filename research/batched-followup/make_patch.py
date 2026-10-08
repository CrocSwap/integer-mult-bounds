"""Append the h30 bit interface and redirect the active layer and assembly.

Retains PR #10's h28 proofs as baseline results; leaves upstream untouched.
"""
from pathlib import Path
from fractions import Fraction as Q
import argparse
import difflib
import json
import re
import shutil
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
from witness import certificate
import make_batched_patch as base


def texq(x):
    return rf'\frac{{{x.numerator}}}{{{x.denominator}}}'


def files():
    roles=json.loads((HERE/'certificate.json').read_text())['bit']['counts']['roles_per_invocation']
    result=certificate(roles)
    original=base.certificate
    base.certificate=lambda:result
    try:rows=list(base.patched_files())
    finally:base.certificate=original
    p=result['assembly']['parameters']
    def redirect(text):
        return text.replace('lem:batched-chunk-swap','lem:dimension30-chunk-swap').replace(
            'prop:batched-simultaneous-layer','prop:dimension30-simultaneous-layer')
    answer=[]
    for name,old,text in rows:
        if name.endswith(('main.tex','00-introduction.tex')):
            text=text.replace('6149999/50000000000000','12649/100000000000')
            if name.endswith('main.tex'):
                marker='review corrections and integration used OpenAI Codex assistance.'
                assert marker in text
                text=text.replace(marker,marker+'\n'
                    'The dimension-thirty refinement is by Rohan Arun with substantial\n'
                    'OpenAI Codex assistance, building on the preceding attributed work.\n'
                    'It changes the bit producer dimension and reuses the complex network.')
        elif name.endswith('04-swap.tex'):
            text+='\n'+(HERE/'proof.tex').read_text()
        elif name.endswith('05-layers.tex'):
            marker=r'\begin{proposition}[Batched simultaneous normalized butterfly layer]'
            assert text.count(marker)==1
            active=text[text.index(marker):]
            active=redirect(active).replace('1-246/10^9','1-253/10^9')
            active=active.replace('[Batched simultaneous normalized butterfly layer]',
                                  '[Layer using dimension-thirty bit interchange]')
            text+='\n\\subsection{Consuming the stronger bit interchange}\n'
            text+='The complex network and guard remain at dimension 28; only the bit\n'
            text+='interchange called by the compact-control interface changes.\n'+active
        elif name.endswith(('06-transforms.tex','07-resampling.tex')):
            text=redirect(text)
        elif name.endswith('08-assembly.tex'):
            text=redirect(text)
            replacements={
                r'\frac{246}{10^9}':r'\frac{253}{10^9}',
                r'\frac{7999999}{16000000}':texq(p['epsilon']),
                r'\frac{6149999}{50000000000000}':texq(p['kappa']),
                r'd^{16000000}\le b^{7999999}':r'd^{100000000}\le b^{49999993}',
                '7999999/16000000':'49999993/100000000',
                '8000001/32000000':'50000007/200000000',
                '8000001/16000000':'50000007/100000000',
                r'p^{1/8000000}':r'p^{7/50000000}',
                r'\frac{95991988001}{160000000000}':texq(p['epsilon']*p['C1']),
                r'\frac{64008011999}{160000000000}':texq(1-p['epsilon']*p['C1']),
            }
            for before,after in replacements.items():
                assert before in text,before
                text=text.replace(before,after)
        answer.append((name,old,text))
    all_text='\n'.join(text for _,_,text in answer)
    untouched={str(p.relative_to(ROOT/'upstream')):p.read_text() for p in (ROOT/'upstream').rglob('*.tex')}
    untouched.update({name:text for name,_,text in answer})
    complete='\n'.join(untouched.values())
    labels=re.findall(r'\\label\{([^}]+)\}',complete)
    assert len(labels)==len(set(labels))
    assert not set(re.findall(r'\\(?:ref|eqref)\{([^}]+)\}',complete))-set(labels)
    assert r'd^{100000000}\le b^{49999993}' in all_text
    assert 'prop:dimension30-simultaneous-layer' in all_text
    return answer


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--materialize',type=Path)
    args=parser.parse_args()
    rows=files()
    patch=''.join(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),
                 fromfile='a/'+name,tofile='b/'+name)) for name,old,new in rows)
    destination=ROOT/'patches/batched-dimension30.patch'
    destination.write_text(patch)
    if args.materialize:
        assert args.materialize.resolve() not in (ROOT.resolve(),(ROOT/'upstream').resolve())
        shutil.copytree(ROOT/'upstream',args.materialize,dirs_exist_ok=True)
        for name,_,text in rows:(args.materialize/name).write_text(text)
    print('PASS integrated h30 bit interface, unchanged h28 complex guard, and new assembly')
    print(destination)


if __name__=='__main__':main()
