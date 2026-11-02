#!/usr/bin/env python3
"""Independent minimal-delta check for the two release reorderings.

Standard library only. Does not import the search, builder or frame optimizer.
The native receipts are separately freshly produced by the unchanged credited
t74-native-fast verifier; this script binds their exact input and outputs.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from pathlib import Path
import argparse
import tempfile
import gzip
import hashlib
import json

HERE=Path(__file__).resolve().parent
WORDS=HERE/'words'
SOURCE={
    'base':'735c540b1fe29d0ceeb4d2f304ec941e5f2bd3bc92bafc8cce2b4f9a67a3b653',
    'extra':'886338fc32da14f3389a82c8120a1bcf9c5e2f0ec3e9b2d377fdae809e1d977f'}
FULL=[256,128,64,32,16,8,4,2,1]

def need(ok,why):
    if not ok:raise ValueError(why)

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):return json.loads(gzip.decompress(path.read_bytes()) if path.suffix=='.gz' else path.read_bytes())

def span(vectors):
    out={0}
    for v in vectors:out|={u^v for u in out}
    return out

def gate_product(gates, registers):
    rows={r:{r:Fraction(1)} for r in registers}
    for g in gates:
        need(g[0]=='add' and g[1]!=g[2],'not an elementary shear')
        target,source=g[1:3]
        for k,v in list(rows[source].items()):
            rows[target][k]=rows[target].get(k,Fraction(0))+Fraction(g[3],g[4])*v
            if rows[target][k]==0:del rows[target][k]
    return rows

def local_check(old,new):
    need(set(old)==set(new),'top-level schema changed')
    need([k for k in old if old[k]!=new[k]]==['B','cleanup','report'],'unexpected changed fields')
    expected=deepcopy(old)
    blocks=[]
    for index,donor,pivot,other,frame in (
        (591,640,644,496,[423,65,20,10]),
        (641,656,660,520,[427,96,24,6])):
        before=old['B'][index:index+2]
        after=new['B'][index:index+2]
        need(before[0][1:3]==[donor,pivot] and before[1][1:3]==[other,pivot],'wrong source shears')
        need(before[0][-1]==before[1][-1]==[429,30],'wrong source frames')
        need(after==[before[1],before[0][:-1]+[frame]],'not the literal commuting reordering')
        need(all(rec[0]!=index+1 for rec in old['warps']),'warp crossed between shears')
        need(not any(rec[1] in (donor,pivot,other) for rec in old['warps']),'changed-register warp')
        need(gate_product(before,[donor,pivot,other])==gate_product(after,[donor,pivot,other]),'operator mismatch')
        need(span([30])<span([429,30])<span(frame),'strict frame nesting')
        for register in (donor,pivot):
            following=[g for g in old['B'][index+2:] if register in (g[1:3] if g[0]=='add' else g[1:2])]
            need(following and span(following[0][-1])==span(frame),'not the next frame')
        previous=[g for g in old['B'][:index] if donor in (g[1:3] if g[0]=='add' else g[1:2])]
        need(previous and span(previous[-1][-1])==span([30]),'wrong donor entrance to segment')
        expected['B'][index:index+2]=after
        blocks.append(dict(index=index,donor=donor,pivot=pivot,other=other,
                           old_jump_ranks=[1,2],new_jump_ranks=[3],scalar_identity=True))
    need(expected['B']==new['B'],'additional B edit')
    # Cleanup contains the same two commuting inverse pairs in reversed order.
    for index in (1009,1061):
        before=old['cleanup'][index:index+2]
        after=new['cleanup'][index:index+2]
        need(after==list(reversed(before)),'cleanup is not inverse reordering')
        regs=sorted(set(before[0][1:3]+before[1][1:3]))
        need(gate_product(before,regs)==gate_product(after,regs),'cleanup operator mismatch')
        need(all(g[-1]==FULL for g in after),'cleanup not FULL')
        expected['cleanup'][index:index+2]=after
    need(expected['cleanup']==new['cleanup'],'additional cleanup edit')
    profile=Counter({int(k):v for k,v in old['report']['local_profile'].items()})
    profile.update({1:-2,2:-2,3:2})
    report=deepcopy(old['report']);report['local_profile']={str(k):v for k,v in sorted(profile.items())}
    need(report==new['report'],'wrong invoice or changed inventory')
    need(sum(k*v for k,v in profile.items())==5135,'rank mass changed')
    return blocks

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path)
    args=parser.parse_args()
    output=args.out.resolve() if args.out else Path(tempfile.mkdtemp(prefix='retiming-proof-'))/'RETIME-INDEPENDENT.json'
    need(output!=HERE and HERE not in output.parents,'output must be outside package')
    need(not output.exists(),'fresh output file required')
    result={}
    for mode in ('base','extra'):
        source=WORDS/f'STAGED644-660-{mode}.json.gz'
        target=WORDS/f'RETIMED644-660-{mode}.json.gz'
        need(sha(source)==SOURCE[mode],'source file mismatch')
        old,new=read(source),read(target)
        blocks=local_check(old,new)
        native=HERE/'receipts'/f'native-{mode}'
        receipt=read(native/'RESULT.json')
        need(receipt['status']=='PASS_COMPLETE_T74_NATIVE_REPLAY','native incomplete')
        need(receipt['word_sha256']==sha(target),'native input mismatch')
        need(all(x['exit_code']==0 for x in receipt['steps']) and [x['step'] for x in receipt['steps']]==['native','ledgers','local-replay','wrappers','phases'],'native stages incomplete')
        replay=read(native/'native/local/INDEPENDENT-LOCAL-REPLAY.json')
        need(replay['status']=='PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY','independent native replay failed')
        prefixes={}
        need(set(replay['local'])=={'forward','backward'},'native orientation coverage')
        for orientation,local in replay['local'].items():
            need(local['all_exact_columns']==632 and local['zero_buffers_returned_to_zero']==91,'native columns/buffers')
            need(Fraction(local['prefix_l1_upper'])<2**128,'local prefix exceeds inherited 128-bit reserve')
            need({int(k):v for k,v in replay['paid_profiles'][orientation].items()}=={int(k):v for k,v in new['report']['local_profile'].items()},'native paid profile mismatch')
            prefixes[orientation]={k:local[k] for k in ('prefix_l1_upper','prefix_bits_upper','charged_payload_bits')}
        result[mode]=dict(source_sha256=sha(source),candidate_sha256=sha(target),
            native_receipt_sha256=sha(native/'RESULT.json'),native_source_sha256=receipt['source_sha256'],
            public_path_normalized_native_commands_sha256=sha(native/'COMMANDS.json'),
            independent_native_receipt_sha256=sha(native/'native/local/INDEPENDENT-LOCAL-REPLAY.json'),
            blocks=blocks,local_profile=new['report']['local_profile'],width_inventory=new['report']['width_inventory'],
            prefixes=prefixes,native_seconds=receipt['seconds'],native_python=receipt['python'])
    controls=[]
    for name in ('coefficient','frame','interface'):
        bad=deepcopy(new)
        if name=='coefficient':bad['B'][592][3]=3
        elif name=='frame':bad['B'][592][-1]=[1]
        else:bad['start_extra']['644']=[30]
        try:local_check(old,bad)
        except ValueError:controls.append(name)
        else:raise ValueError('accepted mutant '+name)
    out=dict(status='PASS_INDEPENDENT_TWO_RELEASE_RETIMING',providers=result,negative_controls=controls,
             exact_profile_delta={'1':-2,'2':-2,'3':2},
             scope='Fresh minimal operator/frame/delta check and both complete native replays. Scientific native receipts are from the fresh research-session replay, authenticated here; command logs are explicitly path-normalized public derivatives with original SHA256 recorded in PUBLICATION-PROVENANCE.json; full native source is not rerun by this capsule. Full global controller/physical/outer validation is separate; unchanged owner interface enables a source-bound reuse proof.')
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(out,indent=2)+'\n')
    print(out['status'],'both providers; both native orientations; 632 columns; prefix 89/95 bits; 3 mutants rejected')

if __name__=='__main__':main()
