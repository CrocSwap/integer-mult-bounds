#!/usr/bin/env python3
"""Internal full-admission stage. Called after full_replay.py runs the fresh baseline.

All predecessor code is copied into a derivative. Only declared word, owner,
registry and exact candidate-specific centre pins change; strict code remains.
"""
import argparse, collections, gzip, hashlib, importlib.util, json, os, shutil, subprocess, sys, time
from fractions import Fraction as Q
from pathlib import Path

HERE=Path(__file__).resolve().parent
SOURCE=SEED=BASE=None
FULL=[256,128,64,32,16,8,4,2,1]

def rd(p):
    b=Path(p).read_bytes();return json.loads(gzip.decompress(b) if str(p).endswith('.gz') else b)
def wr(p,v):
    p=Path(p);b=(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
    p.write_bytes(gzip.compress(b,mtime=0) if p.suffix=='.gz' else b)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(c,m):
    if not c:raise ValueError(m)

def main():
    global SOURCE,SEED,BASE
    a=argparse.ArgumentParser();a.add_argument('--work',type=Path,required=True);a.add_argument('--source2462',type=Path,required=True);a.add_argument('--source2588',type=Path,required=True);a.add_argument('--baseline',type=Path,required=True);a.add_argument('--words',type=Path,required=True);args=a.parse_args()
    SOURCE=args.source2588.resolve();SEED=args.source2462.resolve();BASE=args.baseline.resolve()
    from common import check_source, check_inputs
    check_source(SEED,'2462');check_source(SOURCE,'2588');check_inputs()
    need(__debug__,'assertions enabled')
    work=args.work.resolve();work.mkdir(exist_ok=False);p=work/'derivative';shutil.copytree(SOURCE,p)
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONPYCACHEPREFIX=str(work/'pycache'),PYTHONINTMAXSTRDIGITS='0',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',FINE_ENGINE_CACHE=str(work/'fine-cache'),BORROW_RECEIPTS=str(work/'borrow-receipts'),AUDIT_FAST_SHARDS='4')
    for k in ('PYTHONOPTIMIZE','WITNESS_DISCOVER','WITNESS_RECORD','WITNESS_SPEC'):env.pop(k,None)
    stages=[]
    def run(name,script,*aa):
        start=time.monotonic();log=work/(name+'.log')
        with log.open('w') as f:r=subprocess.run([sys.executable,'-B',str(script),*map(str,aa)],env=env,stdout=f,stderr=subprocess.STDOUT)
        stages.append(dict(name=name,exit_code=r.returncode,seconds=time.monotonic()-start,log_sha256=sha(log)));wr(work/'STAGES.json',stages)
        need(r.returncode==0,name+': '+log.read_text()[-5000:]);print('PASS',name,flush=True)
    from packing import generate as generate_packing
    fill,order=generate_packing();wr(p/'new/borrow-fill/ORDER.json',order);shutil.copy2(HERE/'inputs/pr2673/DISPATCH.json',p/'new/borrow-fill/DISPATCH.json');prov=rd(p/'new/BORROW-PROVIDERS.json');new_words={}
    if args.words:
        sys.path.insert(0,str(p/'new/borrow'));import word_patch
        mappings=[]
        for tag,pid in [('base','gauge44'),('extra','extra')]:
            old=rd(SOURCE/f'new/borrow/words/BORROW-WORD-43{tag}.json.gz');w=rd(args.words/f'eight-alias-{tag}.json.gz');seed=rd(SEED/f'new/borrow/words/BORROW-WORD-43{tag}.json.gz')
            keys=[k for k in w if k not in ('report','cleanup') and w[k]!=seed[k]]
            patch=dict(kind='EIGHT_SOURCE_PARTNER_ASSIGNMENT_SEARCH',credit='PR2530 zxv; PR2588 Jeremy Kothe; new joint assignment by Mason Hale with OpenAI Codex',fields={k:w[k] for k in keys},report=w['report'],prelude_events=w['prelude_events'],declared_gate_edit=word_patch.kernel_gate_edit(seed['B'],w['B']),removed_added=sorted(set(w['removed'])-set(seed['removed'])))
            need(word_patch.apply_lowfour(seed,patch)==w,'complete generated patch '+tag)
            wr(p/f'new/borrow/inputs/alias8_43{tag}.json',patch);wr(p/f'new/borrow/words/BORROW-WORD-43{tag}.json.gz',w)
            helpers=[r for r in range(224,704) if r not in w['removed']]
            widths=[len(w['helper_final'].get(str(r),FULL))-len(w['start_extra'].get(str(r),[])) for r in helpers]
            need(collections.Counter(widths)==collections.Counter(prov[pid]['widths']),'same width inventory for inherited fill')
            pools=collections.defaultdict(list)
            for i,width in enumerate(widths):pools[width].append(i)
            mapping={i:pools[width].pop(0) for i,width in enumerate(prov[pid]['widths'])};mappings.append(mapping)
            prov[pid].update(widths=widths,actual_paid_profile=w['report']['local_profile']);new_words[tag]=w
        need(mappings[0]==mappings[1],'common compact helper map')
        for row in fill['rows']:row[1]=mappings[0][row[1]]
        levels=new_words['base']['target_levels'];need(levels==new_words['extra']['target_levels'],'shared target map')
        core=p/'independent_core.py';text=core.read_text();oldline="    require(set(levels) == {11,23,29,32,34,35,45,48,50,59,63,71,73,76,81,84,87,90,92,108}, 'twenty source-partner target offsets')\n    require(all(frames[f] in ((30,), (45,)) for f in levels.values()), 'target line30')"
        replacement="    require({str(t): list(frames[f]) for t, f in levels.items()} == "+repr(levels)+", 'candidate exact source-partner target frames')"
        need(text.count(oldline)==1,'target pin boundary');core.write_text(text.replace(oldline,replacement))
        mixed=p/'audit_mixed.py';mixed_text=mixed.read_text()
        old_message="str(_e)=='target line30'"
        need(mixed_text.count(old_message)==1,'target mutation diagnostic boundary')
        mixed.write_text(mixed_text.replace(old_message,"str(_e)=='candidate exact source-partner target frames'"))
        text=core.read_text();oldcounter="    require(Counter(e[4] for e in forward) == {1:8, 7:8}, 'sixteen centre children')"
        need(text.count(oldcounter)==1,'centre count pin boundary')
        # Every changed centre path is independently reconstructed above; this
        # explicit pin describes the nominated candidate's four unsplit centres.
        core.write_text(text.replace(oldcounter,"    require(Counter(e[4] for e in forward) == {1:4, 7:4, 8:4}, 'candidate twelve centre children')"))
        controls=p/'new/borrow/lowfour_controls.py';control_text=controls.read_text()
        old_control="    m=mut();m['A'][ia][1],m['A'][ia+1][1]=m['A'][ia+1][1],m['A'][ia][1];expect('prelude correction targets swapped',m)"
        new_control="    # Distinct sources/coefficients are essential: swapping identical additions only commutes them.\n    jb=next(j for j,e in enumerate(pre) if e[0]=='add' and e[1]!=pre[ia][1] and e[2:]!=pre[ia][2:] and e[-1]==pre[ia][-1])\n    m=mut();m['A'][ia][1],m['A'][jb][1]=m['A'][jb][1],m['A'][ia][1];expect('prelude correction targets swapped',m)"
        need(control_text.count(old_control)==1,'target-swap control boundary')
        controls.write_text(control_text.replace(old_control,new_control))
    wr(p/'new/borrow-fill/FILL.json.gz',fill);wr(p/'new/BORROW-PROVIDERS.json',prov)
    run('reconstruct',p/'reconstruct.py','--out',work/'owners');run('lift',p/'lift_parent.py','--owners',work/'owners','--out',work/'parent-data')
    for n in ['PLAN.json','OWNERS.json.gz','DISPATCH.json','PROFILE.json','CONSTRUCTION.json','GLOBAL-TEMPLATE.json.gz','SPEC.json']:shutil.copy2(work/'parent-data'/n,p/n)
    spec=rd(p/'SPEC.json');spec['outer_refinement']=dict(endpoint_digits=24,grid_digits=18,margin_digits=28,bootstrap_steps=12);spec['expected']['live']=66304
    wr(p/'new/SPEC.json',spec)
    natives={}
    for tag in ['base','extra']:
        w=p/f'new/borrow/words/BORROW-WORD-43{tag}.json.gz'
        if args.words:
            natives[tag]=work/('native-'+tag);run('native-'+tag,p/'new/run_native_borrow.py',w,natives[tag])
        else:natives[tag]=BASE/('native-new-'+tag)
        need(rd(natives[tag]/'local/FULL-WORD.json.gz')==rd(w),'complete native word binding')
        need([x['step'] for x in rd(natives[tag]/'STEPS.json')]==['native','ledgers','local-replay','wrappers','phases'] and all(x['exit_code']==0 for x in rd(natives[tag]/'STEPS.json')),'native completion')
    need(rd(BASE/'RESULT.json')['status']=='PASS_T74_EXACT_FILL_COMPLETE_FINITE_ADMISSION','baseline incomplete')
    need(rd(BASE/'RESULT.json')['manifest_sha256']==sha(SOURCE/'MANIFEST.json'),'baseline manifest binding')
    if args.words:run('rebuild-borrow',p/'new/rebuild_borrow.py')
    run('rebind',p/'new/rebind.py',p,natives['base']/'local',natives['extra']/'local',work/'rebound')
    run('lemma-g',p/'code/lemmag_stage.py',work/'LEMMAG.json',natives['base'],natives['extra'])
    layout=work/'layout';layout.mkdir()
    for child in (BASE/'parent/layout').iterdir():
        if child.name!='packing74':(layout/child.name).symlink_to(child,target_is_directory=child.is_dir())
    runtime=layout/'packing74';runtime.mkdir()
    for n in ['replay.py','freeze_spec.py','audit_mixed.py','independent_core.py','geometry_controls.py','audit_fast.py']:shutil.copy2(p/n,runtime/n)
    for n in ['code','construction']:shutil.copytree(p/n,runtime/n)
    (runtime/'inputs').mkdir();shutil.copy2(p/'inputs/PR589-EXPECTED.json',runtime/'inputs/PR589-EXPECTED.json');shutil.copytree(natives['extra'],runtime/'native-extra')
    data=work/'rebound'
    # Remove all discovery pins except inputs independently required before recomputation.
    spec=rd(data/'SPEC.json');spec['expected']={'gain_baseline_kappa':spec['expected']['gain_baseline_kappa'],'live':66304};spec['providers']={};wr(data/'SPEC.json',spec)
    run('discover',runtime/'replay.py','--data',data,'--work',work/'discovery','--local',natives['base']/'local','--discover')
    run('strict',runtime/'replay.py','--data',data,'--work',work/'strict','--local',natives['base']/'local')
    run('geometry',runtime/'geometry_controls.py','--source',layout/'joint1148-round45/source/research/complex-k492-owner-repair/vendor/multicold','--strict',work/'strict','--out',work/'GEOMETRY.json')
    asm=rd(work/'strict/ASSEMBLY.json');invoice=rd(work/'strict/global/audit/PREFIX-AND-INVOICE.json')
    need(invoice['physical']==66814 and invoice['private_zero_buffers']==78,'private cleanup stock')
    need({str(k):v for k,v in asm['complex_profile'].items()}==rd(data/'PROFILE.json'),'profile binding')
    outer=work/'outer-package';outer.mkdir();shutil.copytree(p/'outer',outer/'outer');shutil.copytree(p/'vendor/pr1673',outer/'vendor/pr1673');shutil.copytree(p/'vendor/pr1786',outer/'vendor/pr1786');(outer/'new').mkdir()
    shutil.copy2(data/'SPEC.json',outer/'new/SPEC.json');claim=rd(p/'CLAIM.json');claim.update(kappa=asm['kappa'],kappa_decimal=asm['kappa_decimal']);wr(outer/'CLAIM.json',claim)
    C=Q(asm['complex_lower']);b=C-Q(1,10**104);wr(outer/'outer/B.json',dict(b=str(b),b_above_endpoint=str(C+Q(1,10**24)),profile=asm['complex_profile'],live=66304,note='24-digit certified endpoint; inherited fixed-grid-maximum outer'))
    run('outer-ledger',outer/'outer/check_ledger.py');run('outer-independent',outer/'outer/independent_check.py')
    ledger=rd(outer/'outer/LEDGER.json');k=Q(ledger['rows']['struct_boundary_radix_union']['kappa']['rational']);old=Q(rd(HERE/'inputs/pr2673/OUTER-CLAIM.json')['kappa_rational']);need(k>old,'strict improvement')
    wr(outer/'outer/OUTER-CLAIM.json',dict(kappa=str(k)))
    run('outer-replay',outer/'outer/run_outer.py',work/'outer-replay')
    result=dict(status='PASS_CHANGED_T74_FULL_CONDITIONAL_ADMISSION',kappa=str(k),kappa_decimal=ledger['rows']['struct_boundary_radix_union']['kappa']['decimal'],comparison_kappa=str(old),gain=str(k-old),profile=asm['complex_profile'],physical=invoice['physical'],private_zero_buffers=78,source_manifest=sha(SOURCE/'MANIFEST.json'),stages=stages)
    result.update(scope='Conditional finite construction. All-size compiler, common-label/mutable-source realization, whole-call hosting, precision/tape, exact recovery, analytic transfer, recurrence and bit H1-H5 premises remain; no unconditional multiplication theorem.', baseline_result_sha256=sha(BASE/'RESULT.json'), strict_assembly_sha256=sha(work/'strict/ASSEMBLY.json'), invoice_sha256=sha(work/'strict/global/audit/PREFIX-AND-INVOICE.json'), outer_ledger_sha256=sha(outer/'outer/LEDGER.json'), outer_independent_sha256=sha(outer/'outer/INDEPENDENT.json'), native_steps_sha256={t:sha(d/'STEPS.json') for t,d in natives.items()}, runtime_sources={x.relative_to(runtime).as_posix():sha(x) for x in runtime.rglob('*') if x.is_file() and 'native-extra' not in x.parts})
    wr(work/'RESULT.json',result);print(result['status'],result['kappa_decimal'],flush=True);check_source(SEED,'2462');check_source(SOURCE,'2588')

if __name__=='__main__':main()
