"""Exact all-dirt checks and full explicit-backend bills; no native claim."""
from pathlib import Path
from collections import Counter
import argparse,hashlib,importlib.util,json,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE));import engine as e
BASE='ce7ad1b6ab09452c3478723a2e96ed5ff212dc08'
def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(p.read_text())
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def sources():
    pins=read(HERE/'SOURCES.json');e.need(pins['base']==BASE,'base pin')
    expected={'vendor/pr1057/'+x for x in ('borrow.py','checks.py','PROOF.md','README.md','NOTICE.md','LICENSE')}|{'BASE-SELECTED.json'}
    e.need(set(pins['package_files'])==expected,'source inventory')
    for p,h in pins['package_files'].items():e.need(sha((HERE/p).read_bytes().replace(b'\r\n',b'\n'))==h,'source pin '+p)
    selected=read(HERE/'BASE-SELECTED.json');e.need(selected['kappa']=='836330098538459/500000000000000000','frozen selection')
    return module('reference',HERE/'vendor/pr1057/borrow.py'),module('oracle',HERE/'vendor/pr1057/checks.py')

def compute():
    ref,oracle=sources();f,t,candidates=e.plan(56,4);oldf,oldt,oldcount=ref.unit_plan(56);oldt=oldt[-1]
    e.need((f[56],oldf[56])==(1088,1568),'fixed call improvement')
    f3,t3,c3=e.plan(56,3);e.need(f3==oldf,'entire binary/ternary table agreement')
    e.need(enc(t3)==enc(oldt) and c3==oldcount,'predecessor tie-breaking and coverage')
    literal_trees=0;leaf_events=0
    # Complete small ordered-tree domain independently verifies DP optima.
    for n in range(1,8):
        trees=e.all_trees(n);e.need(min(e.stats(x)['calls'] for x in trees)==f[n],'small exhaustive optimum')
        for tree in trees:
            literal_trees+=1
            for sign in (1,-1):
                word=e.emit(tree,4,sign);leaf_events+=len(word)
                oracle.free_replay(word,n,6,sign,e.bound(tree,2),2)
    K=2;D=7;P=max(max(K,D*e.bound(tree,K)).bit_length()+1 for tree in (t,oldt))
    cases={}
    matrices=[([[1,1],[0,1]],[[1,0],[1,1]],[[0,-1],[1,0]])[i%3] for i in range(56)]
    for label,tree,dirty in [('predecessor',oldt,3),('quaternary',t,4)]:
        result={};meta=e.stats(tree)
        for sign in (1,-1):
            word=list(ref.instructions(tree,dirty,sign)) if label=='predecessor' else e.emit(tree,dirty,sign)
            e.need(len(word)==meta['calls'],'emitted call count')
            other=list(ref.instructions(tree,dirty,-sign)) if label=='predecessor' else e.emit(tree,dirty,-sign)
            e.need(other==[(s,d,i,-q) for s,d,i,q in reversed(word)],'literal inverse')
            free=oracle.free_replay(word,56,dirty+2,sign,e.bound(tree,K),K)
            initial=[[(3*r+2*j)%15-7 for j in range(2)] for r in range(dirty+2)]
            dense=oracle.dense_replay(word,matrices,initial,sign,D*e.bound(tree,K))
            counts=Counter(i for s,d,i,q in word)
            bill=oracle.invoice(word,56,dirty+2,2,P,meta['nodes'],[counts[i] for i in range(56)])
            for key in ('multiplications','add_subtract','zero_assignments','reads','writes','primitive_commands','head_steps_cells'):
                e.need(dense[key]==bill[key],'literal/invoice '+key)
            result[str(sign)]={'word_sha256':sha(enc(word).encode()),'free':free,'dense':dense,'invoice':bill}
        cases[label]={'stats':meta,'dirty_rows':dirty,'sufficient_individual_width':max(K,D*e.bound(tree,K)).bit_length()+1,'directions':result}
    controls=0
    def reject(fn):
        nonlocal controls
        try:fn()
        except ValueError:controls+=1;return
        raise ValueError('missed control')
    word=e.emit(t)
    for bad in (word[:-1],[(s,d,i,-q) if j==0 else (s,d,i,q) for j,(s,d,i,q) in enumerate(word)]):
        reject(lambda bad=bad:oracle.free_replay(bad,56,6,1,e.bound(t,K),K))
    bad=list(word);s,d,i,q=bad[0];bad[0]=(s,0,i,q)
    reject(lambda:oracle.free_replay(bad,56,6,1,e.bound(t,K),K))
    reject(lambda:e.emit(t,2))
    reject(lambda:e.emit((0,2)))
    reject(lambda:e.emit((0,1,2,3,4)))
    reject(lambda:e.emit((0,1),sign=True))
    reject(lambda:oracle.free_replay(word,56,6,1,1,K))
    # A merely reversible nonlinear leaf does not satisfy the additive contract.
    initial=[-7,-4,-1,2,5,8];bad=oracle.nonlinear_replay(word,initial)
    e.need(bad[2:]!=initial[2:],'nonlinear extension must fail');controls+=1
    e.need(oracle.nonlinear_replay([(s,d,i,-q) for s,d,i,q in reversed(word)],bad)==initial,'nonlinear literal inverse still restores')
    return {'base':BASE,'seed':55,'max_arity':4,'factor_count':56,'calls_saved':480,'common_width':P,'planner_candidates':candidates,
        'tree':t,'all_tree_census':{'max_factors':7,'trees':literal_trees,'signed_leaf_events':leaf_events},'cases':cases,'controls':controls,
        'scope':{'exact_additive_leaves':True,'rounded_admission':False,'native_compiler':False,'new_kappa':False}}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();result=compute()
    if args.write:(HERE/'EXPECTED.json').write_text(json.dumps(result,indent=2)+'\n')
    else:e.need(enc(read(HERE/'EXPECTED.json'))==enc(result),'typed receipt mismatch')
    print('PASS_QUATERNARY_BORROW calls=1088_vs_1568 dirty=4_vs_3 controls='+str(result['controls']))
    print(json.dumps({'common_width':result['common_width'],'census':result['all_tree_census'],'candidates':result['planner_candidates']}))
if __name__=='__main__':main()
