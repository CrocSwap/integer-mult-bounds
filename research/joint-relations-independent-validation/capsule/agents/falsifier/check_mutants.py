#!/usr/bin/env python3
"""Semantic mutations of actual PR5383 WORD; no old digest comparison in math path.

Chris R with OpenAI Codex. Inputs read only; imports only independent worker's
algebra module. Coordinator must serialize the full replay modes.
"""
import argparse, copy, gzip, hashlib, importlib.util, json, sys, time
from pathlib import Path
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
EXEC = HERE.parents[1]
CHECKER = EXEC / 'agents/algebra/check_joint.py'
REPO = EXEC / 'repository'
PACKAGE = REPO / 'research/kappa-joint-relations-20261023'

def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)

def digest(value):
    return hashlib.sha256((json.dumps(value,sort_keys=True,separators=(',',':'))+'\n').encode()).hexdigest()

def load_checker():
    spec=importlib.util.spec_from_file_location('independent_joint_algebra_for_mutation',CHECKER)
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module

def mutations(candidate):
    program=candidate['programs']['backward']
    def fork():
        m=dict(candidate); m['programs']=dict(candidate['programs'])
        m['programs']['backward']=list(program); m['owned']=copy.deepcopy(candidate['owned'])
        return m
    m=fork(); del m['programs']['backward'][0]
    yield 'arbitrary_owned_input_clear_removed',m,'replay',None
    m=fork(); m['programs']['backward'][1]=copy.deepcopy(program[1]); m['programs']['backward'][1][1][3]*=-1
    yield 'preparation_sign_reversed',m,'replay',None
    m=fork(); idx=next(i for i,e in enumerate(program) if e[0]=='scalar' and e[1][:2]==['copy',['C',1]])
    m['programs']['backward'][idx]=copy.deepcopy(program[idx]); m['programs']['backward'][idx][1][2]=['L',63]
    yield 'wrong_same_frame_snapshot_source',m,'replay',None
    m=fork(); m['programs']['backward'].pop()
    yield 'arbitrary_owned_output_not_returned_zero',m,'replay',None
    # Preserve every source marker and per-kind subsequence but exchange two
    # adjacent differently tagged events. Source chronology must reject.
    m=fork(); p=m['programs']['backward']
    idx=next(i for i,e in enumerate(p[:-1]) if e[0] in ('phase','adapter') and p[i+1][0]!=e[0])
    p[idx],p[idx+1]=p[idx+1],p[idx]
    yield 'phase_marker_displaced_across_adjacent_event',m,'decode_edits',{'swapped_indices':[idx,idx+1]}
    m=fork(); m['owned']['backward'].remove(['L',225])
    yield 'pivot_laundered_as_borrowed_productive_input',m,'replay',None

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--mode',choices=['manifest','full'],default='manifest'); ap.add_argument('--out',type=Path,default=HERE/'CONTROLS.json'); ap.add_argument('--only',action='append')
    args=ap.parse_args(); candidate=read(PACKAGE/'WORD.json.gz'); source=read(REPO/'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz'); checker=load_checker()
    original_hash=digest(candidate); results={}; start=time.monotonic()
    for name,mutant,engine,extra in mutations(candidate):
        if args.only and name not in args.only: continue
        row={'mutant_payload_sha256_recomputed':digest(mutant),'original_payload_sha256':original_hash,'hash_changed':digest(mutant)!=original_hash,'engine':engine,'old_digest_comparison_used_for_rejection':False,'detail':extra}
        if args.mode=='manifest': row['status']='NOT_RUN_MANIFEST_ONLY'
        else:
            began=time.monotonic()
            try:
                if engine=='decode_edits': checker.decode_edits(source,mutant)
                else: checker.replay(mutant['canonical'],mutant['programs']['backward'],{tuple(r) for r in mutant['owned']['backward']})
            except (ValueError,IndexError,KeyError) as exc:
                row.update(status='REJECTED',reason=str(exc),exception_type=type(exc).__name__)
            else: row.update(status='ACCEPTED_UNEXPECTEDLY')
            row['seconds']=time.monotonic()-began
        results[name]=row
    output={'status':'MANIFEST_ONLY' if args.mode=='manifest' else ('PASS_SEMANTIC_MUTANTS_REJECTED' if all(r['status']=='REJECTED' for r in results.values()) else 'FAIL_SEMANTIC_MUTANT_ACCEPTED'),'candidate_head':'4bd6efa51a495a7c7b7754915cf0244e7e60969e','mutations_of_actual_literal_word':True,'checker_sha256':hashlib.sha256(CHECKER.read_bytes()).hexdigest(),'harness_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'elapsed_seconds':time.monotonic()-start,'controls':results}
    args.out.write_text(json.dumps(output,indent=2,sort_keys=True)+'\n'); print(json.dumps({'status':output['status'],'controls':{k:v['status'] for k,v in results.items()}}))
    if output['status']=='FAIL_SEMANTIC_MUTANT_ACCEPTED': raise SystemExit(1)
if __name__=='__main__': main()
