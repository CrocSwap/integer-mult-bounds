#!/usr/bin/env python3
"""Compose a complete manuscript from pinned PR16 and the h30 stream interface."""
from pathlib import Path
from fractions import Fraction as Q
from dataclasses import replace,asdict
import argparse,difflib,hashlib,json,re,shutil,subprocess,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
import verify

def tq(x):
    x=Q(x);return str(x.numerator) if x.denominator==1 else rf'\frac{{{x.numerator}}}{{{x.denominator}}}'
def exp(x):
    x=Q(x);return str(x.numerator) if x.denominator==1 else str(x)
def once(s,a,b):
    if s.count(a)!=1:raise ValueError(('Expected one occurrence',a,s.count(a)))
    return s.replace(a,b)
def active(s):
    return s.replace('lem:nested-chunk-swap','lem:stream-nested-chunk-swap').replace('prop:nested-simultaneous-layer','prop:stream-nested-simultaneous-layer')

def generate(dest):
    upstream=ROOT/'upstream';patch=ROOT/'references/pr16/patches/nested-source.patch'
    manifest=json.loads((ROOT/'references/pr16/SOURCE.json').read_text())
    assert hashlib.sha256(patch.read_bytes()).hexdigest()==manifest['sha256']['patches/nested-source.patch']
    assert dest.resolve().is_relative_to(ROOT/'build') and dest.resolve()!=ROOT/'build'
    if dest.exists():shutil.rmtree(dest)
    shutil.copytree(upstream,dest)
    subprocess.run(['git','apply','--directory='+str(dest.relative_to(ROOT)),str(patch)],cwd=ROOT,check=True)
    w=verify.assembly();p=w['parameters']
    oldp=replace(verify.parameters(),tau=1-Q(196,10**8),sigma=1-Q(4,10**6),epsilon=Q(499999,10**6),
        lam=1-Q(196,10**8)+Q(1,10**16),lamp=1-Q(196,10**8)+Q(2,10**16),kappa=Q(9799,10**10))
    op=asdict(oldp);oldm=verify.fast_margins(oldp);oldmin=min(oldm.values())
    for relative in ('build/main.tex','build/sections/00-introduction.tex'):
        path=dest/relative;s=path.read_text()
        s=once(s,r'\kappa=9799/10000000000>2^{-20}',r'\kappa='+exp(p['kappa'])+r'>2^{-20}')
        if relative.endswith('main.tex'):
            marker="The revised bound is conditional on the original manuscript's retained"
            s=once(s,marker,'Rohan Arun (with OpenAI Codex assistance) combines the smaller dimension-thirty\nproducer of eumemic with the data corners of PRs 14 and 16 and the nested\nbasis of Zhihao Chen. Earlier bounds below are retained as intermediate\ninterfaces; the final assembly uses this new composition.\n'+marker)
        path.write_text(s)
    path=dest/'build/sections/04-swap.tex';path.write_text(path.read_text()+'\n'+(HERE/'proof.tex').read_text())
    path=dest/'build/sections/05-layers.tex';s=path.read_text()
    marker=r'\begin{proposition}[Nested-source simultaneous normalized butterfly layer]'
    clone=s[s.index(marker):]
    clone=active(clone).replace('Nested-source simultaneous','Nested-stream simultaneous')
    clone=once(clone,r'\tau=1-\frac{49}{25000000}',r'\tau=1-'+tq(verify.BIT_SAVING))
    clone=once(clone,r'm_{\rm b}=32768',r'm_{\rm b}=27000')
    s+='\n\\subsection{The combined stream interface}\nThe preceding complex construction is unchanged. We substitute the stronger\nbit interface of Lemma~\\ref{lem:stream-nested-chunk-swap} in its layer proof.\n'+clone
    path.write_text(s)
    for relative in ('06-transforms.tex','07-resampling.tex'):
        path=dest/'build/sections'/relative;path.write_text(active(path.read_text()))
    path=dest/'build/sections/08-assembly.tex';s=path.read_text()
    start=s.index(r'\begin{equation}\label{eq:fixed-parameters}');end=s.index(r'\end{equation}',start)+len(r'\end{equation}')
    block=r'''\begin{equation}\label{eq:fixed-parameters}
\begin{gathered}
\tau=1-'''+tq(verify.BIT_SAVING)+r''',\quad\sigma=1-'''+tq(verify.COMPLEX_SAVING)+r''',\quad
\beta='''+tq(p['beta'])+r''',\quad\zeta=\frac1{10000},\\
C_1=\frac32-\frac\beta2+\zeta='''+tq(p['C1'])+r''',\quad
\epsilon='''+tq(p['epsilon'])+r''',\quad c=1,\quad\delta='''+tq(p['delta'])+r''',\\
\lambda=\tau+\frac1{10^{16}},\quad\lambda'=\tau+\frac2{10^{16}},\quad
\kappa='''+tq(p['kappa'])+r'''>2^{-20}.
\end{gathered}
\end{equation}'''
    s=s[:start]+block+s[end:]
    # Regenerate every displayed slack; retaining the prior table would leave
    # stale h32 numbers even when the new JSON certificate is correct.
    oldcs=verify.fast_constraints(oldp)
    oldex=verify.layer_exponents(oldp.tau,oldp.sigma,oldp.beta,oldp.c)
    oldcs.update(packed_overhead=oldp.lam-oldex['internal'],reserved_axes=oldp.lamp-oldex['preprocessing'])
    start=s.index(r'\endhead')+len(r'\endhead');end=s.index(r'\bottomrule',start)
    rows=[line for line in s[start:end].splitlines() if line.strip()]
    assert len(rows)==len(oldcs)==len(w['constraints'])==29
    updated=[]
    for row,(oldkey,oldvalue),(key,value) in zip(rows,oldcs.items(),w['constraints'].items()):
        assert key==oldkey
        left,right=row.split(' & ',1)
        assert right=='$'+tq(oldvalue)+r'$\\',(key,right,tq(oldvalue))
        updated.append(left+' & $'+tq(value)+r'$\\')
    s=s[:start]+'\n'+'\n'.join(updated)+'\n'+s[end:]
    replacements={
      'b^{'+exp(op['epsilon'])+'}':'b^{'+exp(p['epsilon'])+'}',
      rf'd^{{{op["epsilon"].denominator}}}\le b^{{{op["epsilon"].numerator}}}':rf'd^{{{p["epsilon"].denominator}}}\le b^{{{p["epsilon"].numerator}}}',
      'p^{'+exp((1-op['epsilon'])/2)+'}':'p^{'+exp((1-p['epsilon'])/2)+'}',
      'p^{'+exp(op['epsilon'])+'}':'p^{'+exp(p['epsilon'])+'}',
      'p^{'+exp(1-op['epsilon'])+'}':'p^{'+exp(1-p['epsilon'])+'}',
      'p^{'+exp(1-2*op['epsilon'])+'}':'p^{'+exp(1-2*p['epsilon'])+'}',
      tq(oldmin)+'>'+tq(op['kappa'])+r'=\kappa':tq(w['minimum_margin'])+'>'+tq(p['kappa'])+r'=\kappa',
      'G_*\\!-\\kappa='+tq(oldmin-op['kappa']):'G_*\\!-\\kappa='+tq(w['absorption_gap']),
      'G_*-\\kappa='+tq(oldmin-op['kappa']):'G_*-\\kappa='+tq(w['absorption_gap']),
      r'\epsilon C_1='+tq(op['epsilon']*op['C1']):r'\epsilon C_1='+tq(p['epsilon']*p['C1']),
      r'1-\epsilon C_1='+tq(1-op['epsilon']*op['C1']):r'1-\epsilon C_1='+tq(1-p['epsilon']*p['C1'])}
    for a,b in replacements.items():
        if a.startswith('G_') and a not in s:continue
        s=once(s,a,b)
    marker='The seven margins have the following exact values:';start=s.index(marker);end=s.index('Exact substitution',start)
    table=marker+'\n\\[\n\\begin{array}{c|c}\n'+''.join('g_'+str(i)+'&'+tq(value)+r'\\'+'\n' for i,value in enumerate(w['margins'].values(),1))+'\\end{array}\n\\]\n'
    s=active(s[:start]+table+s[end:]);path.write_text(s)
    sources={str(x.relative_to(dest)):x.read_text() for x in dest.rglob('*.tex')}
    text='\n'.join(sources.values());labels=re.findall(r'\\label\{([^}]+)\}',text)
    assert len(labels)==len(set(labels)),[x for x in set(labels) if labels.count(x)>1]
    missing=set(re.findall(r'\\(?:ref|eqref|pageref)\{([^}]+)\}',text))-set(labels)
    assert not missing,missing
    for name in ('06-transforms.tex','07-resampling.tex','08-assembly.tex'):
        t=sources['build/sections/'+name]
        assert 'lem:nested-chunk-swap' not in t and 'prop:nested-simultaneous-layer' not in t
    differences=[]
    for name,new in sources.items():
        old=(upstream/name).read_text()
        if old!=new:differences.extend(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+name,tofile='b/'+name))
    out=ROOT/'patches/nested-stream.patch';out.write_text(''.join(differences))
    subprocess.run(['git','apply','--check','--directory=upstream',str(out)],cwd=ROOT,check=True)
    print('PASS complete manuscript patch;',len(labels),'unique labels; no missing references')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--materialize',type=Path,default=ROOT/'build/nested-stream-manuscript');args=p.parse_args();generate(args.materialize.resolve())
