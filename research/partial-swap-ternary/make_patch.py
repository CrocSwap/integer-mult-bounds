#!/usr/bin/env python3
"""Append partial-swap ternary interfaces to the complete PR17 manuscript."""
from pathlib import Path
from dataclasses import asdict
import difflib,importlib.util,re,subprocess,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE));import witness
spec=importlib.util.spec_from_file_location('prior_patch',ROOT/'research/nested-stream/make_patch.py');prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
tq,exp,once=prior.tq,prior.exp,prior.once

def active(s):
    return s.replace('lem:stream-nested-chunk-swap','lem:partial-swap-ternary-chunk-swap').replace('prop:stream-nested-simultaneous-layer','prop:partial-swap-ternary-layer')

def generate():
    dest=ROOT/'build/partial-swap-ternary/manuscript';prior.generate(dest)
    w=witness.assembly();p=w['parameters'];ow=witness.prior.assembly();op=ow['parameters']
    for name in ('build/main.tex','build/sections/00-introduction.tex'):
        path=dest/name;s=path.read_text()
        s=once(s,r'\kappa='+exp(op['kappa'])+r'>2^{-20}',r'\kappa='+exp(p['kappa'])+r'>2^{-19}')
        if name.endswith('main.tex'):
            marker="The revised bound is conditional on the original manuscript's retained"
            s=once(s,marker,'This extension applies icekylinx\'s partial-swap frames (PR 18) to\nRohan Arun\'s ternary composition (PR 17), removing its source-rank\npenalty while retaining all six recursive blocks. The final bound\nis by Rohan Arun with substantial OpenAI Codex assistance.\n'+marker)
        path.write_text(s)
    path=dest/'build/sections/04-swap.tex';path.write_text(path.read_text()+'\n'+(HERE/'proof.tex').read_text())
    path=dest/'build/sections/05-layers.tex';s=path.read_text()
    marker=r'\begin{proposition}[Nested-stream simultaneous normalized butterfly layer]'
    clone=active(s[s.index(marker):]).replace('Nested-stream simultaneous','Partial-swap ternary simultaneous')
    clone=once(clone,r'\tau=1-'+tq(1-op['tau']),r'\tau=1-'+tq(1-p['tau']))
    clone=once(clone,r'\sigma=1-'+tq(1-op['sigma']),r'\sigma=1-'+tq(1-p['sigma']))
    clone=once(clone,'certify the displayed $\\sigma$.','certify the displayed $\\sigma$ at the sharper exact moment recorded\nin Section~\\ref{sec:partial-swap-ternary}.')
    path.write_text(s+'\n\\subsection{The partial-swap ternary layer interface}\n'+clone)
    for name in ('06-transforms.tex','07-resampling.tex'):
        path=dest/'build/sections'/name;path.write_text(active(path.read_text()))
    path=dest/'build/sections/08-assembly.tex';s=path.read_text()
    start=s.index(r'\begin{equation}\label{eq:fixed-parameters}');end=s.index(r'\end{equation}',start)+len(r'\end{equation}')
    block=r'''\begin{equation}\label{eq:fixed-parameters}
\begin{gathered}
\tau=1-'''+tq(1-p['tau'])+r''',\quad\sigma=1-'''+tq(1-p['sigma'])+r''',\quad
\beta='''+tq(p['beta'])+r''',\quad\zeta=\frac1{10000},\\
C_1=\frac32-\frac\beta2+\zeta='''+tq(p['C1'])+r''',\quad
\epsilon='''+tq(p['epsilon'])+r''',\quad c=1,\quad\delta='''+tq(p['delta'])+r''',\\
\lambda=\tau+\frac1{10^{16}},\quad\lambda'=\tau+\frac2{10^{16}},\quad
\kappa='''+tq(p['kappa'])+r'''>2^{-19}.
\end{gathered}
\end{equation}'''
    s=s[:start]+block+s[end:]
    s=once(s,'1-'+tq(1-ow['recurrence']['leaf']),'1-'+tq(1-w['recurrence']['leaf']))
    start=s.index(r'\endhead')+len(r'\endhead');end=s.index(r'\bottomrule',start)
    rows=[x for x in s[start:end].splitlines() if x.strip()];assert len(rows)==29
    updated=[]
    for row,(ok,ov),(k,v) in zip(rows,ow['constraints'].items(),w['constraints'].items()):
        assert ok==k;left,right=row.split(' & ',1);assert right=='$'+tq(ov)+r'$\\'
        updated.append(left+' & $'+tq(v)+r'$\\')
    s=s[:start]+'\n'+'\n'.join(updated)+'\n'+s[end:]
    replacements={
      'b^{'+exp(op['epsilon'])+'}':'b^{'+exp(p['epsilon'])+'}',
      rf'd^{{{op["epsilon"].denominator}}}\le b^{{{op["epsilon"].numerator}}}':rf'd^{{{p["epsilon"].denominator}}}\le b^{{{p["epsilon"].numerator}}}',
      tq(ow['minimum_margin'])+'>'+tq(op['kappa'])+r'=\kappa':tq(w['minimum_margin'])+'>'+tq(p['kappa'])+r'=\kappa',
      'G_*-\\kappa='+tq(ow['absorption_gap']):'G_*-\\kappa='+tq(w['absorption_gap']),
      r'\epsilon C_1='+tq(op['epsilon']*op['C1']):r'\epsilon C_1='+tq(p['epsilon']*p['C1']),
      r'1-\epsilon C_1='+tq(1-op['epsilon']*op['C1']):r'1-\epsilon C_1='+tq(1-p['epsilon']*p['C1'])}
    for f in (lambda x:(1-x)/2,lambda x:x,lambda x:1-x,lambda x:1-2*x):
        replacements['p^{'+exp(f(op['epsilon']))+'}']='p^{'+exp(f(p['epsilon']))+'}'
    for a,b in replacements.items():s=once(s,a,b)
    marker='The seven margins have the following exact values:';start=s.index(marker);end=s.index('Exact substitution',start)
    table=marker+'\n\\[\n\\begin{array}{c|c}\n'+''.join('g_'+str(i)+'&'+tq(x)+r'\\'+'\n' for i,x in enumerate(w['margins'].values(),1))+'\\end{array}\n\\]\n'
    path.write_text(active(s[:start]+table+s[end:]))
    sources={str(x.relative_to(dest)):x.read_text() for x in dest.rglob('*.tex')}
    text='\n'.join(sources.values());labels=re.findall(r'\\label\{([^}]+)\}',text)
    assert len(labels)==len(set(labels));assert not set(re.findall(r'\\(?:ref|eqref|pageref)\{([^}]+)\}',text))-set(labels)
    for name in ('06-transforms.tex','07-resampling.tex','08-assembly.tex'):
        s=sources['build/sections/'+name];assert 'lem:stream-nested-chunk-swap' not in s and 'prop:stream-nested-simultaneous-layer' not in s
    diff=[]
    for name,new in sources.items():
        old=(ROOT/'upstream'/name).read_text()
        if old!=new:diff.extend(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+name,tofile='b/'+name))
    out=ROOT/'patches/partial-swap-ternary.patch';out.write_text(''.join(diff))
    subprocess.run(['git','apply','--check','--directory=upstream',str(out)],cwd=ROOT,check=True)
    print('PASS partial-swap manuscript;',len(labels),'unique labels; no missing references')
if __name__=='__main__':generate()
