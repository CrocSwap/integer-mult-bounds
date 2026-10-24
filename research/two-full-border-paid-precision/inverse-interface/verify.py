#!/usr/bin/env python3
"""Source-bound macro inverses of both round-three 632+1 register words.

Yiyang (@Lyy-iiis), substantial OpenAI Codex assistance. Apache-2.0.
This is an inverse-interface construction, not a Gaussian compiler theorem.
"""
import argparse
from collections import Counter
from fractions import Fraction as F
import gzip
from hashlib import sha1, sha256
import json
from pathlib import Path

SOURCE_SHA='7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05'
SOURCE_BLOB='46d929df83817b85a5387bcdb9745e0627d6366e'
PROFILE={1:2201,2:412,3:510,4:127,5:40,8:8}


def need(ok, why):
    if not ok:
        raise ValueError(why)


def parse(program):
    nodes=[]; i=0
    while i<len(program):
        e=program[i]
        if e[0]=='phase':
            i+=1; continue
        if e[0]=='scalar' and e[1][0]=='clear':
            first=i; block=[e]; i+=1
            while i<len(program):
                block.append(program[i]);i+=1
                if block[-1][0]=='scalar' and block[-1][1][0]=='clear':
                    break
            need(len(block)==26,'literal 26-record center macro')
            need(block[0][1]==['clear',['C',0]] and block[-1][1]==['clear',['C',0]],'center allocation/clear')
            child_positions=[j for j,b in enumerate(block) if b[0]=='center']
            need(len(child_positions)==1,'one owned child inside macro')
            child_pos=child_positions[0];child=block[child_pos]
            need(child[0]=='center' and child[1]==0,'one owned paid child')
            need(block[0][2]==child[2] and block[-1][2]==child[3],'center frame itinerary')
            capture=[];capture_mode='sum'
            for j,b in enumerate(block[1:child_pos],1):
                need(b[0]=='scalar' and b[1][0] in ('copy','add') and b[1][1]==['C',0] and b[1][2][0]=='L','capture only reads persistent roles')
                need(b[2]==child[2],'capture input frame')
                if b[1][0]=='copy':
                    need(j==1 and not capture,'copy only initializes the captured linear form')
                    capture_mode='copy';capture.append([b[1][2][1],1,1])
                else:
                    capture.append([b[1][2][1],b[1][3],b[1][4]])
            need(capture,'nonempty owned capture')
            fan=[]
            for b in block[child_pos+1:-1]:
                need(b[0]=='scalar' and b[1][0]=='add' and b[1][1][0]=='L' and b[1][2]==['C',0],'fanout only reads owned value')
                need(b[2]==child[3],'fanout output frame')
                dst=b[1][1][1]
                fan.append([dst,b[1][3],b[1][4]])
            need(fan,'nonempty owned fanout')
            need(not ({r for r,a,b in capture}&{r for r,a,b in fan}),'all capture sources must be unchanged by fanout')
            nodes.append({'kind':'center_macro','event':first,'child_event':first+child_pos,
                          'capture':capture,'capture_mode':capture_mode,'fanout_event':first+child_pos+1,
                          'old':child[2],'new':child[3],'rank':child[4],'fanout':fan,'fanout_sign':1,
                          'child_execution':'same_retained_orientation','owned_role':['C',0]})
            continue
        k=e[0]
        need(k in ('scalar','climb','warp','adapter'),'supported source node '+k)
        if k=='scalar':
            g=e[1]
            need(g[0] in ('add','scale') and g[1][0]=='L','persistent scalar must be reversible')
            if g[0]=='add':
                need(g[2][0]=='L' and g[1]!=g[2],'distinct persistent add roles')
            else:
                c=F(g[2],g[3]);need(c!=0,'nonzero scalar')
                need(abs(c.numerator)&(abs(c.numerator)-1)==0 and c.denominator&(c.denominator-1)==0,'dyadic-unit scale')
        nodes.append({'kind':k,'event':i,'record':e,'execution':'forward'})
        i+=1
    need(len([x for x in nodes if x['kind']=='center_macro'])==8,'all eight centers captured')
    return nodes


def inverse_node(n):
    x=json.loads(json.dumps(n))
    if x['kind']=='center_macro':
        x['fanout_sign']=-1
        # Crucial: the owned oracle retains this source macro's orientation.
        return x
    x['execution']='actual_inverse'
    e=x['record']
    if x['kind']=='scalar':
        g=e[1]
        if g[0]=='add':
            g[3]=-g[3]
        else:
            c=1/F(g[2],g[3]);g[2],g[3]=c.numerator,c.denominator
    elif x['kind']=='climb':
        e[3],e[4]=e[4],e[3]
    elif x['kind']=='warp':
        e[2]=-e[2];e[3],e[4]=e[4],e[3]
    elif x['kind']=='adapter':
        need(e[1] in ('old_to_new','new_to_old'),'typed boundary adapter')
        e[1]='new_to_old' if e[1]=='old_to_new' else 'old_to_new'
    return x


def frames(nodes, initial):
    now=list(initial); paid=Counter()
    for n in nodes:
        k=n['kind']
        if k=='center_macro':
            need(all(now[r]==n['old'] for r,a,b in n['capture']),'all center capture source frames')
            need(all(now[d]==n['new'] for d,a,b in n['fanout']),'center target frames')
            paid[n['rank']]+=1
        elif k=='scalar':
            g,f=n['record'][1:]
            need(now[g[1][1]]==f,'scalar destination frame')
            if g[0]=='add':need(now[g[2][1]]==f,'scalar source frame')
        elif k=='climb':
            _,phase,r,old,new,rank=n['record']
            need(now[r]==old,'paid field entrance frame');now[r]=new;paid[rank]+=1
        elif k=='warp':
            _,r,op,old,new=n['record'];need(now[r[1]]==old,'warp entrance frame');now[r[1]]=new
    return now,dict(sorted(paid.items()))


def addv(a,b,c):
    return tuple(x+c*y for x,y in zip(a,b))


def oracle(v, event, inverse=False):
    # Each site has its own near-identity dyadic shear, so unrelated paid
    # sites do not obey the ideal Gaussian/frame relations. Its SAME inverse
    # is nonetheless exact and private-workspace free.
    c=F((event%11)-5,16)
    return (v[0]+(-c if inverse else c)*v[1],v[1])


def nonlinear_center(v,event):
    # Deterministic nonlinear rounded query. The center inverse needs this
    # very same function, not its inverse or an independently perturbed one.
    return (F((3*v[0]+v[1])//2)+(event%3), F((v[0]-5*v[1])//4))


def execute(nodes, values, wrong=None):
    a=list(values)
    for n in nodes:
        k=n['kind']
        if k=='center_macro':
            event=n['child_event']+(1 if wrong=='fresh_center' and n['fanout_sign']==-1 else 0)
            captured=(F(0),F(0))
            for j,(r,num,den) in enumerate(n['capture']):
                if wrong=='different_capture' and n['fanout_sign']==-1 and j==0:num+=den
                captured=addv(captured,a[r],F(num,den))
            z=nonlinear_center(captured,event)
            sign=1 if wrong=='positive_fanout' else n['fanout_sign']
            for dst,num,den in n['fanout']:
                a[dst]=addv(a[dst],z,F(sign*num,den))
        elif k=='scalar':
            g=n['record'][1];r=g[1][1]
            if g[0]=='add':a[r]=addv(a[r],a[g[2][1]],F(g[3],g[4]))
            else:a[r]=tuple(F(g[2],g[3])*v for v in a[r])
        elif k in ('climb','warp','adapter'):
            e=n['record']
            r=e[2] if k in ('climb','adapter') else e[1][1]
            inv=n['execution']=='actual_inverse'
            event=n['event']+(1 if wrong=='fresh_paid_inverse' and inv and k=='climb' else 0)
            a[r]=oracle(a[r],event,inv)
    return a


def run(source):
    raw=source.read_bytes();need(sha256(raw).hexdigest()==SOURCE_SHA,'actual round-three source bytes')
    need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==SOURCE_BLOB,'actual round-three git blob')
    src=json.loads(gzip.decompress(raw));c=src['canonical']
    need(set(src['programs'])=={'forward','backward'},'both retained source orientations')
    orientations={};recipes={}
    for orientation in ('forward','backward'):
        p=src['programs'][orientation]
        original=parse(p);inverse=[inverse_node(n) for n in reversed(original)]
        final,pf=frames(original,c['start']);start,pi=frames(inverse,c['final'])
        need(final==c['final'] and start==c['start'],'both complete persistent frame endpoints: '+orientation)
        need(pf==pi==PROFILE,'complete paid profiles preserved exactly: '+orientation)
        tests=[]
        for seed in (1,7):
            x=[(F(((i+3)*seed)%19-9,4),F(((2*i+5)*seed)%23-11,8)) for i in range(632)]
            y=execute(original,x)
            need(execute(inverse,y)==x,'actual same-oracle inverse round trip: '+orientation)
            z=execute(inverse,x)
            need(execute(original,z)==x,'inverse then original round trip: '+orientation)
            tests.append({'seed':seed,'persistent_roles':632,'coordinates_per_role':2,'both_orders':'PASS'})
        for bad in ('fresh_center','positive_fanout','fresh_paid_inverse','different_capture'):
            need(execute(inverse,y,bad)!=x,'reject '+orientation+' '+bad)
        broken=json.loads(json.dumps(p))
        first=next(n for n in original if n['kind']=='center_macro')
        broken[first['fanout_event']][1][1]=['L',first['capture'][0][0]]
        caught=False
        try:parse(broken)
        except ValueError:caught=True
        need(caught,'reject source-overwriting center fanout: '+orientation)
        centers=[{k:v for k,v in n.items() if k!='fanout'}|{'fanout_count':len(n['fanout'])} for n in original if n['kind']=='center_macro']
        expected_shape=(1,22,8,0) if orientation=='forward' else (22,1,0,8)
        for n in original:
            if n['kind']=='center_macro':
                need((len(n['capture']),len(n['fanout']),len(c['frames'][n['old']]),len(c['frames'][n['new']]))==expected_shape,'retained orientation macro shape')
        orientations[orientation]={'source_events':len(p),'center_macros':centers,'paid_original':pf,'paid_inverse':pi,
                                  'tests':tests,'negative_controls':['fresh center realization','unnegated inverse fanout','fresh nominal paid inverse','different captured linear form','source-overwriting fanout']}
        recipes[orientation]={'input_frames':c['final'],'output_frames':c['start'],'nodes':inverse}
    recipe={'format':'SOURCE_TYPED_MACRO_INVERSE_IR_V2','source_sha256':SOURCE_SHA,'orientations':recipes}
    payload=(json.dumps(recipe,sort_keys=True,separators=(',',':'))+'\n').encode()
    result={'status':'PASS_SOURCE_MACRO_INVERSE_INTERFACE_NOT_A_GAUSSIAN_BOUND',
            'source_sha256':SOURCE_SHA,'source_head':'1eb8da6cfb35512c0cc2533413e5ca42f48e13c6',
            'source_upstream_path':'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz',
            'source_git_blob':SOURCE_BLOB,
            'retrieved_unchanged_via':'PR4694 head 2add42d1edf14a263abe90a3bcde67fc1ba30768 research/retained-center-extension/inputs/round3-native.json.gz',
            'identical_source_revisions':['0ce1b5c9fb7163d0b2f0ac3db95fc418dbbcec62','1eb8da6cfb35512c0cc2533413e5ca42f48e13c6','cef4b52f2a59009865bf8eabde1be3f159063703'],
            'attribution':'Cao Yifan round-three native word in the PR4610 lineage; this contribution changes the inverse interpretation of its owned macros.',
            'orientations':orientations,'persistent_roles':632,'reused_owned_roles':1,'other_explicit_owned_or_zero_roles':0,
            'center_macro_count':16,'paid_overhead_per_orientation':{},
            'center_inverse_child_contract':'same deterministic oracle in its retained orientation, unchanged capture-source set, identical captured linear form, exact coefficient ADD and clear after fanout',
            'persistent_paid_child_contract':'actual inverse of the same realized bijection, with private workspace restored',
            'inverse_recipe_payload_sha256':sha256(payload).hexdigest(),
            'inverse_recipe_hash_scope':'exact decompressed canonical JSON bytes; gzip container metadata is not semantic evidence',
            'remaining':['No claim that approximate paid children preserve native Gaussian/frame relations or D U(q) factorization.',
                         'Inverse of whole native word changes its productive D orientation; it is not automatically a fresh-D opposite shear.',
                         'Scalar additions and dyadic scales were exact rationals; bounded-grid rounding, overflow and total precision remain separately costed.',
                         'Each child must restore its private workspace; projected productive endpoints alone do not establish this.',
                         'Nonlinear rounded bijectivity does not supply the linear operator identities used by the border controller.',
                         'Coherent frame potentials and free-warp intertwining remain unproved for the approximate paid realization.',
                         'IR is a typed inverse recipe, not an accepted native compiler artifact.']}
    return result,payload


if __name__=='__main__':
    ap=argparse.ArgumentParser()
    here=Path(__file__).resolve().parent
    ap.add_argument('--source-word',type=Path,default=here.parents[2]/'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz')
    ap.add_argument('--out-dir',type=Path,default=here)
    ap.add_argument('--regenerate',action='store_true',help='explicitly replace the frozen recipe and receipt')
    args=ap.parse_args()
    result,payload=run(args.source_word)
    result['checker_sha256']=sha256(Path(__file__).read_bytes()).hexdigest()
    result_bytes=(json.dumps(result,indent=2,sort_keys=True)+'\n').encode()
    if args.regenerate:
        args.out_dir.mkdir(parents=True,exist_ok=True)
        (args.out_dir/'INVERSE-RECIPE.json.gz').write_bytes(gzip.compress(payload,mtime=0))
        (args.out_dir/'RESULT.json').write_bytes(result_bytes)
    else:
        need(gzip.decompress((args.out_dir/'INVERSE-RECIPE.json.gz').read_bytes())==payload,'frozen canonical inverse recipe comparison')
        need((args.out_dir/'RESULT.json').read_bytes()==result_bytes,'frozen inverse receipt comparison')
    print(result['status'])
