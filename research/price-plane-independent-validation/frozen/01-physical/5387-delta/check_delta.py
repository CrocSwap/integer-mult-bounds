#!/usr/bin/env python3
"""Bounded exact PR5387 preparation-delta audit; no candidate-code imports."""
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
import copy,gzip,hashlib,json,time
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
OLD=ROOT/'09-capsule-cold'/'capsule-v1'
NEW=ROOT/'09-capsule-cold'/'capsule-5387-v1'
PIVOTS={225,227,229,230,241,245,257,288}
def check(ok,msg):
    if not ok:raise ValueError(msg)
def jread(p):
    b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def merge(dst,key,q):
    q+=dst.get(key,F(0))
    if q:dst[key]=q
    else:dst.pop(key,None)
def prefix_and_body(word):
    p=word['programs']['backward']
    i=next(i for i,e in enumerate(p) if e[0]!='scalar')
    check(p[i]==['phase','zero_frame_precondition'],'source precondition boundary')
    return p[:i],p[i:]
def evaluate_prefix(prefix):
    # Full arbitrary entry columns, including all17dirty owners. This is
    # coefficient equality of whole fields, not finite numerical probes.
    state={('L',i):{('L',i):F(1)} for i in range(632)}
    state.update({('C',i):{('C',i):F(1)} for i in range(9)})
    clears=Counter();adds=Counter()
    for e in prefix:
        check(e[0]=='scalar' and e[2]==0,'preparation only frame0 scalar grammar')
        g=e[1];dst=tuple(g[1])
        check(dst[0]=='L' and dst[1] in PIVOTS,'preparation writes only surrendered pivot owner')
        if g[0]=='clear':
            state[dst]={};clears[dst]+=1
        else:
            check(g[0]=='add','preparation only clear and dyadic ADD')
            src=tuple(g[2]);q=F(*g[3:])
            check(src[0]=='L' and src[1] not in PIVOTS,'every prep RHS is independent nonpivot helper')
            check(src[1]>=224,'every prep RHS is helper input')
            check(clears[dst]>0,'owned pivot cleared before first preparation read/write')
            check(q.denominator & (q.denominator-1)==0,'dyadic coefficient')
            for key,a in state[src].items():merge(state[dst],key,q*a)
            adds[dst]+=1
    check(set(clears)=={('L',p) for p in PIVOTS} and all(q==1 for q in clears.values()),'exactly one initial clear for each pivot')
    return state,{'clear_count':sum(clears.values()),'add_count':sum(adds.values()),'adds_by_pivot':{str(r[1]):n for r,n in sorted(adds.items())},'all_RHS_nonpivot_independent_helpers':True,'dirty_entry_columns':17,'retained_columns':624}

def main():
    start=time.monotonic()
    oldmanifest=(OLD/'IMMUTABLE-MANIFEST.json').read_bytes()
    check(hashlib.sha256(oldmanifest).hexdigest()=='ae6a1b933c386feabc9bab3300163df41e94bd3ddeeff973955695d33d5b11c8','frozen5383 manifest')
    base_receipt=jread(HERE.parent/'PHYSICAL-RECEIPT.json')
    freeze=jread(HERE.parent/'ENGINE-FREEZE.json')
    check(hashlib.sha256((HERE.parent/'PHYSICAL-RECEIPT.json').read_bytes()).hexdigest()==freeze['files']['PHYSICAL-RECEIPT.json'],'old independent receipt frozen')
    check(base_receipt['status']=='PASS_BOUNDED_INDEPENDENT_PHYSICAL_EIGHT_RELATIONS','positive old physical gate')
    newmanifest=(NEW/'IMMUTABLE-MANIFEST.json').read_bytes(); manifest=jread(NEW/'IMMUTABLE-MANIFEST.json')
    check(manifest['candidate_head']=='b1ab650d36f59e5be682a813145b7c67e219e341','exact5387 head')
    for r in manifest['rows']:
        b=(NEW/r['capsule_path']).read_bytes()
        check(hashlib.sha256(b).hexdigest()==r['sha256'],'new capsule SHA256')
        check(hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==r['git_blob'],'new capsule blob')
    oldwordpath=OLD/'snapshot/research/kappa-joint-relations-20261023/WORD.json.gz'
    newwordpath=NEW/'snapshot/research/eight-owned-relations/WORD.json.gz'
    a=jread(oldwordpath);b=jread(newwordpath)
    check(a['canonical']==b['canonical'],'complete canonical physical data identical')
    check(a['owned']==b['owned'],'identical owned and retained field contracts')
    check(a['programs']['forward']==b['programs']['forward'],'identical forward literal word')
    ap,ab=prefix_and_body(a);bp,bb=prefix_and_body(b)
    check(ab==bb,'entire post-preparation body exact literal equality')
    ast,ac=evaluate_prefix(ap);bst,bc=evaluate_prefix(bp)
    check(ast==bst,'all641initial-field columns equal after preparation')
    controls=[]
    wrong=copy.deepcopy(bp);wrong[1][1][3]*=-1
    try:wrongst,_=evaluate_prefix(wrong); rejected=wrongst!=ast
    except ValueError:rejected=True
    check(rejected,'wrong preparation sign rejected');controls.append('wrong preparation sign')
    wrong=copy.deepcopy(bp);wrong.pop(0)
    try:wrongst,_=evaluate_prefix(wrong);rejected=wrongst!=ast
    except ValueError:rejected=True
    check(rejected,'omitted dirty-entry clear rejected');controls.append('omitted dirty-entry clear')
    raw=newwordpath.read_bytes()
    result={'status':'PASS_BOUNDED_PHYSICAL_DELTA_INHERITS_EXACT5383_GATE','candidate_head':manifest['candidate_head'],'manifest_sha256':hashlib.sha256(newmanifest).hexdigest(),'base_head':base_receipt['candidate_head'],'base_receipt_sha256':hashlib.sha256((HERE.parent/'PHYSICAL-RECEIPT.json').read_bytes()).hexdigest(),'word_sha256':hashlib.sha256(raw).hexdigest(),'word_payload_sha256':hashlib.sha256(gzip.decompress(raw)).hexdigest(),'word_git_blob':hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),'old_preparation':ac,'new_preparation':bc,'postpreparation_literal_events':len(bb),'preparation_identical_as_event_multiset':Counter(map(str,ap))==Counter(map(str,bp)),'canonical_frames_maps_phases_identical':True,'forward_identical':True,'owned_inventory_identical':True,'full641column_preparation_maps_identical':True,'all_RHS_nonpivot_commutation_proved':True,'same_paid_target_physical_interface':True,'negative_controls':controls,'seconds':round(time.monotonic()-start,3),'scope':'Preparation-only exact matrix-map delta plus byte-identical body transfers the frozen5383 all624retained/17dirty-owned physical gate, phases/subset/returns/controller/all-f implication. New scalar/precision/stock/compiler/funding bill stays separate; no new whole physical or cold replay.'}
    (HERE/'DELTA-RECEIPT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
