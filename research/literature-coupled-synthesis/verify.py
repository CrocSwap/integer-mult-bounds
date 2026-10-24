#!/usr/bin/env python3
"""Replay all 25 literature adaptations and candidate composition screens.
No network, Git executable, third-party library, or downloaded paper is required.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
from fractions import Fraction as F
from algebra import need,eye,replay,coupled_program,coupled_program_dual
from experiments import run,HERE,ROOT
from costs import screen
from construction import build
from current_profile import screen as current_screen

def payload(obj):return json.dumps(obj,indent=2,sort_keys=True)+'\n'

def compute():
    sources=json.loads((HERE/'SOURCES.json').read_text())
    for row in sources['files']:
        if row['usage']=='input':
            need(sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'changed source '+row['path'])
    f,results=run();papers=json.loads((HERE/'PAPERS.json').read_text())
    need(len(papers)==len(results)==25,'25-paper coverage')
    need(len({p['url'] for p in papers})==25,'distinct primary papers')
    need([p['id'] for p in papers]==[r['paper_id'] for r in results],'paper to probe coverage')
    need([p['implementation'] for p in papers]==[r['implementation'] for r in results],'implementation registry')
    # Independent analytic endpoint, not merely H^2=I.
    expected=[f.C[i]+[-4*x for x in f.W[i]] for i in range(112)]
    expected += [[3*x for x in f.Z[k]]+[F(13*(k==j)) for j in range(8)] for k in range(8)]
    need(f.H==expected,'all 120 original input columns of balanced H')
    program=coupled_program(f.m,F(-4));bad=[e[:] for e in program]
    j=next(i for i,e in enumerate(bad) if e[0]=='add');bad[j][-1]=str(-F(bad[j][-1]))
    need(replay(bad,eye(120))!=expected,'altered coupling coefficient rejected')
    evidence={'schema_version':1,'status':'PASS_25_PAPER_INTERFACE_SWEEP',
        'scope':'Scoped exact adaptations and candidate screens, not a complete multiplication construction.',
        'papers':results,'composition':build(f),
        'frozen_reference_recursive_screen':screen(f),
        'current_selected_recursive_screen':current_screen(f),
        'failure_controls':['altered coupled ADD coefficient','same-tableau global phase',
            'zero-address false positive versus nonzero residual','missing owned observation initialization',
            'whole-bank ADD replacing main-only ADD','wrong observer owner or version',
            'fresh-decoder recursive bill fails exact .004 screen'],
        'native_endpoint_status':'Pinned premises; original native words not replayed.',
        'new_kappa':None}
    return {'RESULT.json':evidence,'BALANCED-PROGRAM.json':{
        'schema_version':1,'frame':'Kp on main, Km on modes; inverse maps at exit',
        'entrance_monomial_maps':120,'exit_monomial_maps':120,
        'all_inputs_arbitrary':120,'new_owned_fields':0,'paid_Gaussian_calls':0,
        'operations':program},'ROWSUM-PROGRAM.json':{
        'schema_version':1,'gauge':[-12,1],
        'frame':'Kp on main, Km on modes; inverse maps at exit',
        'entrance_monomial_maps':120,'exit_monomial_maps':120,
        'all_inputs_arbitrary':120,'new_owned_fields':0,'paid_Gaussian_calls':0,
        'operations':coupled_program_dual(f.m,F(-12))}}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args()
    artifacts=compute()
    for name,obj in artifacts.items():
        target=HERE/name;raw=payload(obj)
        if args.write:target.write_text(raw)
        else:need(target.read_text()==raw,'changed generated evidence '+name)
    print('PASS_25_PAPER_INTERFACE_SWEEP: 25 probes; 120-column boundary; actual two-generation and 112-coset screens; no new kappa')

if __name__=='__main__':main()
