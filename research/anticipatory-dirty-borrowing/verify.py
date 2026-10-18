#!/usr/bin/env python3
"""Read-only source-bound replay of one fixed 80-alias construction.

Child assertion checks run with -I and without -O even when this entry point
is optimized. Exact receipts compare mathematical JSON, not gzip streams.
"""
import argparse,gzip,hashlib,importlib.util,json,subprocess,sys,tempfile
from pathlib import Path
from fractions import Fraction as Q

HERE=Path(__file__).resolve().parent

def need(ok,message):
    if not ok:raise ValueError(message)

def read(path):return json.loads(path.read_text())

def pins():
    for row in read(HERE/'BUNDLE.json'):
        need(hashlib.sha256((HERE/row['path']).read_bytes()).hexdigest()==row['sha256'],'bundle source drift: '+row['path'])
    for row in read(HERE/'SOURCES.json')['retained_sources']:
        need(hashlib.sha256((HERE/row['package_path']).read_bytes()).hexdigest()==row['sha256'],'retained source drift')
    src=read(HERE/'SOURCES.json')['retained_sources'][0]
    need(hashlib.sha256(gzip.decompress((HERE/src['package_path']).read_bytes())).hexdigest()==src['payload_sha256'],'canonical word payload pin')

def frame(b):
    out={0}
    for x in b:out|={v^x for v in out.copy()}
    return out

def incident(e):return e[1:3] if e[0]=='add' else e[1:2]

def audit_witness(w,inv,blocks):
    v=w['v'];n=2*v+w['R'];F=list(map(frame,w['frames']));pairs=inv['pairs']
    need((w['h'],v,n)==(9,112,704),'fixed selected source dimensions')
    need(len(pairs)==80 and sum(x['low'] for x in pairs)==32,'fixed alias inventory')
    need(len({x['register'] for x in pairs})==len(pairs),'recipient uniqueness')
    need(len({x['borrow_from'] for x in pairs})==len(pairs),'lender uniqueness')
    all_block={r for b in blocks for r in b['helpers']}
    last={};cur=w['start'].copy()
    for e in w['A']:
        for r in incident(e):cur[r]=e[-1];last[r]=-1
    for r in w['centers']:last[r]=-1
    for i,e in enumerate(w['B']):
        for r in incident(e):cur[r]=e[-1];last[r]=i
    ordinary=last.copy();tail_time={}
    seen=set()
    for t in inv['early_tail_events']:
        idx=t['old_tail_index'];e=t['gate'];rs=incident(e)
        need(idx not in seen and e==w['tail'][idx],'actual distinct moved tail gate');seen.add(idx)
        need(len(w['frames'][e[-1]])<=4,'rank-four early tail scope')
        before=max([ordinary.get(r,-1)+1 for r in rs]+[tail_time.get(r,0) for r in rs])
        need(before==t['before_B'],'commutation after every last ordinary use')
        for r in rs:last[r]=before-1;cur[r]=e[-1];tail_time[r]=before
    for x in pairs:
        lender=x['borrow_from'];recipient=x['register'];E=frame(x['handoff_basis'])
        need(lender not in all_block and not(v<=lender<2*v),'lender domain')
        need(last[lender]==x['retirement_B_event'] and cur[lender]==x['retirement_frame'],'actual lender retirement')
        need(last[lender]<x['handoff_B'],'strict handoff chronology')
        need(len(F[cur[lender]])==len(E) and x['handoff_paid_rank']==0,'equal-dimensional physical handoff')
        b=next(b for b in blocks if b['base']==x['base'])
        need(recipient in b['helpers'] and x['low']==(recipient in b['low']),'actual recipient block')
        need(x['handoff_B']==b['first_input'] and E<=frame(b['common_frame']),'actual deferred block input frame')
    corrections=inv['initial_corrections']
    need(len(corrections)==64,'fixed initial correction count')
    need(all(2*v<=t['source']<n and len(w['frames'][w['start'][t['source']]])==0 for t in corrections),'initial corrections use only zero-frame helpers')
    need(all(len(t['operator_word'])==1 and 1<=abs(t['operator_word'][0])<=80 for t in corrections),'only compiled monomial operators in initial corrections')
    for part in ['A','B','precondition','compensation','cut','tail']:
        for e in w[part]:
            q=Q(e[3],e[4]) if e[0]=='add' else Q(e[2],e[3])
            need(q.denominator&(q.denominator-1)==0,'source scalar is dyadic')
            if e[0]=='scale':need(q!=0 and abs(q.numerator)&(abs(q.numerator)-1)==0,'source inverse scale is dyadic')
            if e[0]=='add' and not(v<=e[1]<2*v):need(not(v<=e[2]<2*v),'non-target state is independent of Y')
    return {'aliases':80,'low_aliases':32,'initial_corrections':64,'moved_tail_gates':len(seen)}

def child(script,args,expect=True):
    p=subprocess.run([sys.executable,'-I','-B',str(HERE/script),*map(str,args)],capture_output=True,text=True,timeout=240)
    if expect:need(p.returncode==0,p.stdout[-2000:]+p.stderr[-2000:])
    else:need(p.returncode!=0,'corrupted program unexpectedly accepted')
    return p

def run():
    pins();w=json.loads(gzip.decompress((HERE/'inputs/selected-complex-word.json.gz').read_bytes()))
    inv=read(HERE/'WITNESS.json');blocks=read(HERE/'inputs/selected-block-certificate.json')['sources'][0]['blocks']
    audit=audit_witness(w,inv,blocks)
    with tempfile.TemporaryDirectory(prefix='anticipatory-borrow-') as tmp:
        d=Path(tmp);out=d/'replay.json'
        def replay(word=HERE/'inputs/selected-complex-word.json.gz',inventory=HERE/'WITNESS.json',expect=True):
            return child('replay.py',['--word',word,'--blocks',HERE/'inputs/selected-block-certificate.json','--inventory',inventory,'--recover-cold','--output',out],expect)
        replay();result=read(out);result.pop('seconds');result.pop('favorable_numerical_moment_at_a_0_00177')
        need(result['independent_input_columns']==624 and result['remaining_registers']==624,'all remaining arbitrary inputs')
        need(result['local_mass']==5276 and len(result['exact_cold_restoration'])==40,'complete local profile and cold outputs')
        need(result['initial_anticipatory_corrections']==inv['initial_corrections'],'fixed initial correction witness')
        native=d/'operators.json';child('operators.py',['--replay',out,'--output',native]);operators=read(native)
        need(operators['physical_rank_zero_products_checked']==160,'all physical handoff and exit products')
        spec=importlib.util.spec_from_file_location('fixed_borrow_price',HERE/'price_engine.py');C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C)
        H={int(r):n for r,n in result['local_profile'].items()};prices={}
        for m,L in [(57,7),(73,9),(89,11)]:
            moment=C.relax(H,m,(L-1)*112,L,64,Q(177,100000));ab=C.ceiling(H,m,(L-1)*112,L,64)
            need(moment[0]>1,'campaign target must remain rejected')
            prices[str(m)]={'stages':L,'families':(L-1)*112,'centre':64,'idle_rank_cap':C.max_idle_rank(m),'primitive_target':'177/100000','target_moment_interval':list(map(str,moment)),'favorable_primitive_ceiling':list(map(str,ab))}
        mutations=[]
        for name in ['missing-initial-compensation','wrong-compensation-sign','duplicate-lender']:
            x=json.loads(json.dumps(inv))
            if name=='missing-initial-compensation':x['initial_corrections']=[]
            elif name=='wrong-compensation-sign':x['initial_corrections'][0]['coefficient']=str(-Q(x['initial_corrections'][0]['coefficient']))
            else:x['pairs'][1]['borrow_from']=x['pairs'][0]['borrow_from']
            path=d/(name+'.json');path.write_text(json.dumps(x));replay(inventory=path,expect=False);mutations.append(name)
        x=json.loads(json.dumps(w));e=x['cut'][0];need(e[0]=='add','cut fixture');e[3]*=2
        path=d/'wrong-centre-map.json.gz';path.write_bytes(gzip.compress(json.dumps(x).encode(),mtime=0));replay(word=path,expect=False);mutations.append('wrong-centre-map')
    return {'status':'PASS_ANTICIPATORY_DIRTY_BORROWING_COMPONENT','audit':audit,'replay':result,'operators':operators,'prices':prices,
      'external_mutations_rejected':mutations,'scope':'fixed scalar/operator component and exact local rank profile; full native lowering, both hosted orientations, ownership, precision, bit rail and kappa admission remain open'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--record',type=Path);args=p.parse_args();out=run()
    if args.record:args.record.write_text(json.dumps(out,indent=2)+'\n')
    else:need(json.loads(json.dumps(out))==read(HERE/'RESULT.json'),'canonical receipt mismatch')
    print('PASS_ANTICIPATORY_DIRTY_BORROWING inputs=624 helpers=480->400 cold=40 physical_products=160 mutations=4 plus_internal_controls no_new_kappa')

if __name__=='__main__':main()
