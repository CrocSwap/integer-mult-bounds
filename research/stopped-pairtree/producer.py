#!/usr/bin/env python3
"""Portable complete producer for the selected power-of-two pair-star tree.

Apache-2.0. Prepared with OpenAI Codex assistance. The scalar change replaces
only each pair-star prefix/suffix network with a shared binary exclusion tree.
All PR107/PR104 scalar, frame and rational-center checks remain active.

Credits: icekylinx for PR104's rational centers/stopped construction; Rohan Arun
for PR107's aligned order refinement; the retained PairedTriple contributors.
Original notices and licenses are preserved in references/stopped-recursion.
"""
from pathlib import Path
import argparse,hashlib,json,os,shlex,subprocess,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
ARCHIVE=ROOT/'references/stopped-recursion/pr107'
SOURCE='research/reversed-rational-centers/producer.py'
SOURCE_SHA='178cb7c5c1685ffbf192ecfc38f7d180560c29571a2c91645e7b13c1a502fe25'
MATCHER='scripts/endpoint_gauge/match_complex_general.cpp'
MATCHER_SHA='fb83c08125521128a38f5ee53f91d192904cc3372ad8f196ad9576e5f4f727da'
BEFORE='''        pre=[0]
        for i in others:pre.append(add(pre[-1],inputs[tuple(sorted((a,b,i)))]))
        suf=[0]*(len(others)+1)
        for j in range(len(others)-1,-1,-1):suf[j]=add(inputs[tuple(sorted((a,b,others[j])))],suf[j+1])
        for j,i in enumerate(others):
            node=add(pre[j],suf[j+1])
            roots.append(node);kind.append(0)
            pair_outputs[a,b,i]=node
            assert support[node] == point_masks[a]&point_masks[b]&~point_masks[i]
            assert types[node]==1
            assert not support[node]&(point_masks[a]^point_masks[b]^point_masks[i])
        pairtotals[a,b]=pre[-1]
        assert support[pre[-1]] == point_masks[a]&point_masks[b]
'''
AFTER='''        vals=[inputs[tuple(sorted((a,b,i)))] for i in others]
        def node_tree(xs):
            if len(xs)==1:return (xs[0],None,None)
            split=1 << ((len(xs)-1).bit_length()-1)
            left=node_tree(xs[:split]);right=node_tree(xs[split:])
            return (add(left[0],right[0]),left,right)
        tree=node_tree(vals);exclusions=[]
        def emit(tree,outside):
            root,left,right=tree
            if left is None:exclusions.append(outside);return
            emit(left,add(outside,right[0]));emit(right,add(outside,left[0]))
        emit(tree,0)
        for i,node in zip(others,exclusions):
            roots.append(node);kind.append(0)
            pair_outputs[a,b,i]=node
            assert support[node] == point_masks[a]&point_masks[b]&~point_masks[i]
            assert types[node]==1
            assert not support[node]&(point_masks[a]^point_masks[b]^point_masks[i])
        pairtotals[a,b]=tree[0]
        assert support[tree[0]] == point_masks[a]&point_masks[b]
'''

# Previous pair-tree matching retained as a diagnostic, not mixed into the new ledger.
UNWEIGHTED_PROFILE={'h': 24, 'v': 2024, 'c': 44340, 'q': 8120, 'baseline_R': 52460, 'matched': 7194, 'R': 45266, 'orientation_changes': 2950, 'rank_sum': 1087488, 'loss': 552, 'histogram': [8930, 42466, 40481, 13012, 16036, 5820, 7718, 3480, 5859, 1392, 3436, 936, 3617, 864, 4816, 888, 3854, 2424, 5273, 2974, 9960, 0, 3048, 24, 24], 'central_disjoint': 24, 'center_denominator': 21}

# Cardinality-preserving local matching exchanges. These integer prices are a
# frozen discovery objective, not mathematical cost claims; acceptance uses the
# complete exact regenerated child histogram and independent physical checks.
WEIGHTED_PATCH=r'''
// Fixed literal integer prices select a legal witness only. Every accepted
// edit preserves matching cardinality; the full integer histogram follows.
assert(h==24); const int64_t prices[]={0,496535241,884750065,1232084102,1552871023,1853918153,2139234832,2411470255,2672507285,2923753724,3166302293,3401025926,3628638102,3849732930,4064812814,4274308189,4478591954,4677990301,4872790971,5063249681,5249595190,5432033350,5610750384,5785915566,5957683435}; auto cost=[&](U r){return prices[r];};
auto profit=[&](U donor,U j){U e=uses[j],target=nd(e),value=e>>31?target:args[target][e&1];U ru=ranks[donor],rv=ranks[value],rt=ranks[target];assert(rt>=ru&&ru>=rv);return cost(h-ru)+cost(rv)+cost(rt-rv)-cost(rt-ru);};
auto legal=[&](U donor,U j){U e=uses[j],target=nd(e),value=e>>31?target:args[target][e&1];return(value==args[donor][0]||value==args[donor][1])&&before(donor*2,e)&&incl(donor*2,e);};
for(U pass=0;pass<3;pass++){
 U exchanged=0;int64_t gain=0;
 for(U x:donors){
  U old=leftmatch[x];
  adjacency(x,[&](U j){
   U y=rightmatch[j];if(y==x)return false;
   if(!old){
    assert(y);int64_t delta=profit(x,j)-profit(y,j);
    if(delta>10){leftmatch[x]=j+1;leftmatch[y]=0;rightmatch[j]=x;gain+=delta;exchanged++;return true;}
   }else if(!y){
    int64_t delta=profit(x,j)-profit(x,old-1);
    if(delta>10){rightmatch[old-1]=0;rightmatch[j]=x;leftmatch[x]=j+1;gain+=delta;exchanged++;return true;}
   }else if(legal(y,old-1)){
    int64_t delta=profit(x,j)+profit(y,old-1)-profit(x,old-1)-profit(y,j);
    if(delta>10){leftmatch[x]=j+1;leftmatch[y]=old;rightmatch[j]=x;rightmatch[old-1]=y;gain+=delta;exchanged++;return true;}
   }
   return false;
  });
 }
 std::cerr<<"weighted pass "<<pass<<" exchanges "<<exchanged<<" excess gain "<<gain<<"\n";
 if(!exchanged)break;
}
V count_check=0;for(U donor:donors)if(leftmatch[donor]){count_check++;assert(rightmatch[leftmatch[donor]-1]==donor&&legal(donor,leftmatch[donor]-1));}assert(count_check==matches);

'''

def digest(raw):return hashlib.sha256(raw).hexdigest()
def transformed_source():
    raw=(ARCHIVE/SOURCE).read_bytes()
    assert digest(raw)==SOURCE_SHA,'Original producer source changed'
    text=raw.decode();old='others.sort(key=lambda i:((i^1) in (a,b),-i))'
    assert text.count(old)==1 and text.count(BEFORE)==1
    # The only two mathematical edits: original forward aligned leaf order and
    # the explicit binary-tree substitution. Every inherited assertion remains.
    return text.replace(old,'others.sort(key=lambda i:((i^1) in (a,b),i))').replace(BEFORE,AFTER)

def build(h,prefix,central_disjoint,base=2):
    assert not sys.flags.optimize,'Run without -O'
    assert (h,central_disjoint,base)==(24,24,2)
    sys.path.insert(0,str(ARCHIVE/'scripts'))
    namespace={'__name__':'pinned_pairtree_producer','__file__':str(ARCHIVE/SOURCE)}
    exec(compile(transformed_source(),str(HERE/'producer.py')+'::tree-patch','exec'),namespace)
    return namespace['build'](24,Path(prefix),24,2)

def compile_matcher(work,weighted=True):
    work=Path(work);work.mkdir(parents=True,exist_ok=True)
    raw=(ARCHIVE/MATCHER).read_bytes();assert digest(raw)==MATCHER_SHA
    text=raw.decode();include='#include "../partial_swap/binary_io.hpp"'
    assert text.count(include)==1 and text.count('assert(argc==3);')==1
    text=text.replace(include,'#include "'+str(ARCHIVE/'scripts/partial_swap/binary_io.hpp')+'"').replace('assert(argc==3);','assert(argc==4);')
    if weighted:
        point='std::vector<int64_t>hist(h+1);';assert text.count(point)==1
        text=text.replace(point,WEIGHTED_PATCH+point)
    marker='std::cout<<"{\\"h\\":"';assert text.count(marker)==1
    dump='''std::ofstream dump(argv[3],std::ios::binary);U count=matches;dump.write((char*)&count,4);
for(U donor:donors)if(leftmatch[donor]){U e=uses[leftmatch[donor]-1];dump.write((char*)&donor,4);dump.write((char*)&e,4);}assert(dump);
'''
    text=text.replace(marker,dump+marker)
    source=work/'matcher.cpp';source.write_text(text);program=work/'matcher'
    env=os.environ.copy();env.pop('SDKROOT',None)
    subprocess.run([*shlex.split(os.environ.get('CXX','c++')),'-O3','-std=c++17',str(source),'-o',str(program)],env=env,check=True)
    return program

def regenerate(work):
    work=Path(work).resolve();work.mkdir(parents=True,exist_ok=True)
    construction=build(24,work/'graph',24)
    program=compile_matcher(work)
    row=json.loads(subprocess.check_output([str(program),str(work/'graph.bin'),str(work/'graph.labels'),str(work/'matches.bin')],text=True))
    assert (work/'matches.bin').read_bytes()==(HERE/'matches.bin').read_bytes(),'Selected matching witness changed'
    assert row['baseline_R']==construction['R'] and row['R']==row['c']+row['q']-row['matched']
    row.update(central_disjoint=24,center_denominator=21)
    expected=json.loads((HERE/'producer.json').read_text());assert row==expected,'Selected complete producer changed'
    bit=json.loads((ARCHIVE/'certificates/stopped-product-bit-axis.json').read_text())
    for filename,value in [('complex-axis.json',row),('producer.json',row),('complex-construction.json',construction),('constructor.json',construction),('bit-axis.json',bit)]:
        (work/filename).write_text(json.dumps(value,sort_keys=True,indent=2)+'\n')
    diagnostic=work/'unweighted';old_program=compile_matcher(diagnostic,False)
    old_row=json.loads(subprocess.check_output([str(old_program),str(work/'graph.bin'),str(work/'graph.labels'),str(diagnostic/'matches.bin')],text=True))
    old_row.update(central_disjoint=24,center_denominator=21);assert old_row==UNWEIGHTED_PROFILE
    (work/'unweighted-producer.json').write_text(json.dumps(old_row,sort_keys=True,indent=2)+'\n')
    receipt=dict(unweighted_diagnostic_equal=True,h=24,c=row['c'],q=row['q'],R=row['R'],matched=row['matched'],histogram_equal=True,
        source_sha256=SOURCE_SHA,matcher_sha256=MATCHER_SHA,transformed_source_sha256=digest(transformed_source().encode()),
        files={name:digest((work/name).read_bytes())for name in('graph.bin','graph.labels','matches.bin')})
    (work/'producer-check.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    return receipt

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--work-dir',type=Path,required=True);a=p.parse_args()
    print(json.dumps(regenerate(a.work_dir),indent=2));print('PASS selected pair-tree scalar/frame/matcher producer')
