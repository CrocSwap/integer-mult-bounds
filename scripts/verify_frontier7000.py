#!/usr/bin/env python3
"""Authenticate and serially replay the conditional #7000/#7001 selection.

Evidence reuse authenticates recorded executions; it does not rerun them.
Cold replay exports the complete current scientific closure and leaves the
committed receipts untouched. Douglas Colkitt with OpenAI Codex assistance.
Apache-2.0.
"""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import runpy
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
REVIEW = 'docs/research/pr-intake-evidence/pr7000-application'
PREVIOUS = 'docs/research/pr-intake-evidence/pr7000-admission'
PRIMARY = 'research/shared-wire-split-composition'
EXPECTED = ['bit-primary', 'bit-independent', 'complex-primary',
            'complex-independent', 'complex-physical', 'owned-factorizations',
            'lambda-algebra', 'bit-ambient', 'bit-ambient-optimized',
            'interface-bindings', 'interface-bindings-optimized',
            'application', 'application-optimized', 'scalar', 'scalar-optimized',
            'native-catalogue-0', 'native-catalogue-1', 'native-catalogue-2']


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path, root=ROOT):
    return json.loads((root/path).read_bytes())


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def claim_from_sources(result, baseline):
    gate = result['gate']
    k, g = Q(gate['claim']), Q(gate['compiler_gap'])
    need(k == Q('.00363005817') and g == Q(1, 10**14), 'Current tested parameters')
    a, q, ep, be = k+4*g, k+3*g, 1-g, 1-3*g
    xi = ep*(1+q)-Q(3,32)+g
    # Formula names follow kappa-rebuild/controller/outer_parameters.py,
    # confirmed by final4610-independent-admission/checks/outer.py.
    rows = [ep*q, a, 1-ep+q*be, 1-ep+a*be, 1-ep+be,
            Q(3,32)+xi-ep, xi+Q(1,2)-ep, ep, 1-(ep+be+48-128+2)]
    need(min(rows) > k, 'Every outer row strictly exceeds the claim')
    names=['main_transform','global_coordinate_router','fused_gaussian',
           'group_bit_router','group_scans','boundary_algebraic_matrix',
           'sparse_union_movement','polynomial_products','microbox_face_corrections']
    return dict(schema='proposed-conditional-integer-multiplication-claim/1',
        kappa=str(k), source_result=PRIMARY+'/FULL-RESULT.json',
        uniform_templates=[dict(family='complex',rank_encoding='2^'+gate['H'],
                                saving=str(k+6*g),ambient=153),
                           dict(family='BIT before cover',rank_encoding='2^296630000000000',
                                saving=str(Q('.0038525299')),ambient=134)],
        covered_BIT_saving=str(Q('.0038525298')),
        ordinary_BIT_saving=str((1-Q(1,250))*Q('.0038525298')+Q(1,250)*Q('.0038507')),
        admitted_BIT_saving=str(Q('.00385248')),
        complex_BIT_premise=str(Q(gate['BIT_pin'])),
        BIT_bootstrap=[str(Q(x)) for x in ('.0034','.0038507','.00385248')],
        nine_outer_savings={name:str(x) for name,x in zip(names,rows)},
        outer_formula_source=PRIMARY+'/interval_gate.py',
        limiting_outer_saving=str(min(rows)), strict_limiting_slack=str(min(rows)-k),
        assumptions=baseline['assumptions'],
        scope='Conditional shared-native mixed caller with exact common-grid scalar service; '
              'five inherited assumptions. No materialized uniform word, complete multiplier, '
              'independent human proof or formal-kernel acceptance.')


def authenticate(root=ROOT):
    selected = read('certificates/selected-result.json', root)
    need(selected['audited_source_head']=='93effe2a135bf57b9e484cb630d8dd057159aec9',
         'Use the replay for the current selection')
    runpy.run_path(str(root/'scripts/verify_selected_result.py'))['check'](selected, root)
    baseline = read('certificates/checkpoints/frontier6030.json', root)
    need(selected['assumptions']==baseline['assumptions'], 'Inherited assumptions changed')
    need(read(selected['certificate'], root)==claim_from_sources(
        read(PRIMARY+'/FULL-RESULT.json', root), baseline), 'Claim differs from exact source parameters')
    validation = read(REVIEW+'/VALIDATION.json', root)
    need(validation['status']=='admitted_conditional' and validation['remaining']==[], 'Admission incomplete')
    entries = validation['receipts']
    need([e['name'] for e in entries]==EXPECTED, 'Complete replay coverage')
    jobs = []
    for entry in entries:
        p = root/entry['receipt']
        need(digest(p)==entry['sha256'], 'Receipt changed: '+entry['name'])
        receipt = json.loads(p.read_bytes())
        need(receipt['exit_code']==0 and receipt['stop'] is None and receipt['source_unchanged'],
             'Execution did not complete: '+entry['name'])
        need(receipt['name']==entry['name'], 'Receipt name')
        need(digest(p.parent/receipt['log'])==receipt['log_sha256'], 'Execution log changed')
        need(receipt['peak_sampled_descendant_kib']<=receipt['limits']['descendant_kib']
             and receipt['wall_seconds']<=receipt['limits']['seconds']+1, 'Recorded resource bounds')
        for name, expected in receipt['source_sha256'].items():
            source = root/name
            if name=='certificates/selected-result.json':
                source = root/'certificates/checkpoints/frontier6030.json'
            if source.is_file() and digest(source)==expected:
                continue
            alias = validation['historical_input_aliases'].get(expected)
            if alias:
                need(digest(root/alias)==expected, 'Historical orchestration bytes changed')
                continue
            unused = validation['nonexecuted_inventory_changes'].get(entry['name'], {})
            need(unused.get(name)==expected, 'Recorded scientific input changed: '+name)
        # The earlier directory-wide harness did not inventory its own two
        # review checkers. Their exact versions are pinned by its validation.
        for name, expected in validation['prior_review_checker_sha256'].items():
            need(digest(root/PREVIOUS/name)==expected, 'Prior review checker changed')
        jobs.append(receipt)
    chunks=[]
    for entry in entries[-3:]:
        p=root/entry['receipt']; rec=json.loads(p.read_bytes())
        raw=(p.parent/rec['log']).read_text(); result=json.loads(raw[raw.index('{'):])
        need(result['status']=='PASS_CURRENT_NATIVE_CATALOGUE_SLICE'
             and result['phase_control_rejected'], 'Exact native check incomplete')
        chunks.append(result)
    need([(c['slice_start'],c['slice_stop']) for c in chunks]==[(0,1000),(1000,2000),(2000,3057)]
         and {c['catalogue_size'] for c in chunks}=={3057}
         and len({c['catalogue_digest'] for c in chunks})==1
         and sum(c['checked_maps'] for c in chunks)==3057
         and sum(c['main_boundary_pairs'] for c in chunks)==104, 'Native catalogue coverage gap')
    return selected, jobs


def run_bounded(command, root, output, name, limits):
    start=time.monotonic(); peak=0; stop=None; log=output/(name+'.log')
    with log.open('w') as stream:
        process=subprocess.Popen(command,cwd=root,stdout=stream,stderr=subprocess.STDOUT,
                                 start_new_session=True,env={k:v for k,v in os.environ.items()
                                                            if k not in ('PYTHONPATH','PYTHONHOME')})
        while process.poll() is None:
            rows=[tuple(map(int,line.split())) for line in subprocess.check_output(
                ['ps','-axo','pid=,ppid=,rss='],text=True).splitlines() if line.strip()]
            ids={process.pid}
            while True:
                new={pid for pid,parent,rss in rows if parent in ids}-ids
                if not new:break
                ids |= new
            peak=max(peak,sum(rss for pid,parent,rss in rows if pid in ids))
            if peak>limits['descendant_kib'] or time.monotonic()-start>limits['seconds']:
                stop='sampled_descendant_memory' if peak>limits['descendant_kib'] else 'wall_timeout'
                try:os.killpg(process.pid,signal.SIGKILL)
                except ProcessLookupError:pass
                process.wait();break
            time.sleep(.2)
    receipt=dict(name=name,command=command,exit_code=process.returncode,stop=stop,
        wall_seconds=time.monotonic()-start,peak_sampled_descendant_kib=peak,
        limits=limits,log=log.name,log_sha256=digest(log),python=sys.version,platform=platform.platform())
    (output/(name+'.json')).write_text(json.dumps(receipt,indent=2)+'\n')
    print(name,receipt['exit_code'],round(receipt['wall_seconds'],2),peak,stop,flush=True)
    need(process.returncode==0 and stop is None, 'Replay failed; see '+str(log))


def main():
    need(not sys.flags.optimize,'Assertions must remain enabled in the pipeline')
    parser=argparse.ArgumentParser(description=__doc__)
    modes=parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--check-only',action='store_true')
    modes.add_argument('--work',type=Path,help='New isolated export and full serial replay')
    modes.add_argument('--export-only',type=Path,help='Export and authenticate retained evidence; no new scientific execution')
    args=parser.parse_args();selected,jobs=authenticate()
    if args.check_only:
        print('PASS_FRONTIER7000_BINDINGS_AND_RECORDED_EVIDENCE (not a new scientific replay)');return
    work=(args.work or args.export_only).resolve()
    need(not work.exists(),'Export destination must be new')
    manifest=read(selected['source_manifest'])
    names=set(manifest['files'])|{selected['source_manifest'],'certificates/selected-result.json'}
    for name in sorted(names):
        target=work/name;target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes((ROOT/name).read_bytes())
    authenticate(work)
    if args.export_only:
        print('PASS_FRONTIER7000_EXPORTED_RECORDED_EVIDENCE',work);return
    output=work/'replay-output';output.mkdir()
    for job in jobs:
        command=[sys.executable,*job['command'][1:]]
        run_bounded(command,work,output,job['name'],job['limits'])
        authenticate(work)
    print('PASS_FRONTIER7000_CONDITIONAL_COLD_REPLAY',output)


if __name__=='__main__':main()
