# SPDX-License-Identifier: Apache-2.0
"""Source-bound finite premises for the mixed cover/fibre norm.
This is an informal mathematics certificate, not a completed admission or Lean proof.
All inherited sources and completed native receipts are read-only.
"""
import argparse,copy,gzip,hashlib,importlib.util,json,os,sys,time
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
sys.dont_write_bytecode=True

def need(p,m):
    if not p:raise AssertionError(m)
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        for b in iter(lambda:f.read(2**20),b''):h.update(b)
    return h.hexdigest()
def read(p):
    p=Path(p);b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def write_new(p,o):
    need(not p.exists(),'refuse overwrite '+str(p));l=p.with_name(p.name+'.lock');fd=os.open(l,os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.close(fd)
    try:p.write_text(json.dumps(o,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
    finally:l.unlink()
def load_module(name,p,expected=None):
    from types import ModuleType
    p=Path(p);body=p.read_bytes()
    if expected is not None:need(hashlib.sha256(body).hexdigest()==expected,'loaded source byte guard '+str(p))
    m=ModuleType(name);m.__file__=str(p);m.__package__=''
    exec(compile(body,str(p),'exec'),m.__dict__)
    return m

def bytecode_control(out):
    import importlib.util,marshal,struct
    d=out/'bytecode-control';d.mkdir();p=d/'fixture.py';body=b"marker='authenticated source'\n";p.write_bytes(body)
    cache=Path(importlib.util.cache_from_source(str(p)));cache.parent.mkdir()
    stat=p.stat();bad=compile("marker='stale bytecode'\n",str(p),'exec')
    cache.write_bytes(importlib.util.MAGIC_NUMBER+struct.pack('<III',0,int(stat.st_mtime),len(body))+marshal.dumps(bad))
    m=load_module('guarded_source_fixture',p,hashlib.sha256(body).hexdigest())
    need(m.marker=='authenticated source','timestamp-valid stale bytecode consumed')
    return 'timestamp_valid_stale_pyc_not_consumed'

def rank2(rows):
    piv={}
    for v in rows:
        while v:
            j=v.bit_length()-1
            if j not in piv:piv[j]=v;break
            v^=piv[j]
    return len(piv)

def monomial(m):
    need(set(m)=={'matrix_rows','offset','phase','linear_Z4','quadratic_rows'},'unknown monomial operator or cover-dependent field')
    A=m['matrix_rows'];need(len(A)==9 and all(type(x)is int and 0<=x<512 for x in A)and rank2(A)==9,'invertible selected-bit address matrix')
    need(type(m['offset'])is int and 0<=m['offset']<512,'selected-bit offset')
    need(type(m['phase'])is int and 0<=m['phase']<8,'unit root phase')
    need(len(m['linear_Z4'])==9 and all(type(x)is int and 0<=x<4 for x in m['linear_Z4']),'selected-bit linear phase')
    need(len(m['quadratic_rows'])==9 and all(type(x)is int and 0<=x<512 for x in m['quadratic_rows']),'selected-bit quadratic phase')

def all_monomials(d):
    n=0
    def rec(z):
        nonlocal n
        if isinstance(z,dict):
            if 'matrix_rows'in z:monomial(z);n+=1
            else:
                for v in z.values():rec(v)
        elif isinstance(z,list):
            for v in z:rec(v)
    rec(d);return n

MARKERS={'entry_adapters','cleanup_tail','full_frame_cleanup','B','done','zero_frame_precondition','final','exit_adapters','A','centers'}
TAGS={'phase':{2},'scalar':{3},'warp':{5},'adapter':{4},'residual_adapter':{4,5},'climb':{6},'center':{5},'zero_buffer':{3}}

def program_norm(events,canon):
    n=2*canon['v']+canon['R'];env={('L',i):Q(1)for i in range(n)};peak=Q(1);zlive=set();cnt=Counter();paid=Counter()
    for e in events:
        need(isinstance(e,list)and e and e[0]in TAGS and len(e)in TAGS[e[0]],'unknown event opcode/shape')
        tag=e[0];cnt[tag]+=1
        need(not zlive or tag in('scalar','warp','zero_buffer'),'private zero buffer exposed to a child')
        if tag=='phase':need(e[1]in MARKERS,'unknown numerical phase or cover-mixing event')
        elif tag=='zero_buffer':
            _,op,z=e;need(z in canon['zero_buffers'],'private buffer label')
            if op=='alloc':need(z not in zlive and('Z',z)not in env,'duplicate private alloc');zlive.add(z);env['Z',z]=Q(0)
            else:need(op=='free'and z in zlive,'private buffer released without allocation');zlive.remove(z);del env['Z',z]
        elif tag=='warp':need(tuple(e[1])in env and type(e[2])is int and e[2]!=0,'rank-zero warp register')
        elif tag=='climb':need(type(e[5])is int and 0<=e[5]<=9,'child selected-bit rank');paid[e[5]]+=1
        elif tag=='center':need(0<=e[1]<8 and e[4]==8,'eight-axis selected-bit centre child');paid[e[4]]+=1
        elif tag=='scalar':
            sc=e[1];op=sc[0];need(op in('add','copy','scale','clear'),'unknown scalar primitive');t=tuple(sc[1]);need(t[0]in('L','C','Z'),'unknown scalar register')
            if op=='clear':need(len(sc)==2,'clear shape');env[t]=Q(0)
            elif op=='copy':need(len(sc)==3 and t in env and tuple(sc[2])in env,'private copy initialization');env[t]=env[tuple(sc[2])]
            elif op=='scale':
                need(len(sc)==4 and t in env,'scale initialization');q=Q(sc[2],sc[3]);a,b=abs(q.numerator),q.denominator
                need(a>0 and a&(a-1)==0 and b&(b-1)==0,'dyadic power scale');env[t]*=abs(q)
            else:
                need(len(sc)==5 and t in env and tuple(sc[2])in env and t!=tuple(sc[2]),'add initialization/alias');s=tuple(sc[2]);q=Q(sc[3],sc[4]);a,b=abs(q.numerator),q.denominator
                need(a>0 and b&(b-1)==0,'dyadic add');acc=0
                for i,bit in enumerate(bin(a)[2:]):
                    if i:acc*=2;peak=max(peak,acc*env[s])
                    if bit=='1':acc+=1;peak=max(peak,acc*env[s])
                val=Q(acc)
                for _ in range(b.bit_length()-1):val/=2;peak=max(peak,val*env[s])
                need(val==abs(q),'exact Horner value');env[t]+=abs(q)*env[s]
            peak=max(peak,env[t])
    need(not zlive and all(v==0 for r,v in env.items()if r[0]=='C'),'private work boundary clear')
    bits=peak.numerator.bit_length()-peak.denominator.bit_length()+1
    return dict(prefix_bits=bits,prefix_upper=str(peak),event_counts=dict(cnt),paid_profile=dict(sorted(paid.items())))

def provider(base,legacy):
    canon=read(base/'CANONICAL-WORD.json.gz');programs=read(base/'LOCAL-PROGRAMS.json.gz');checks=read(base/'LOCAL-CHECKS.json');replay=read(base/'INDEPENDENT-LOCAL-REPLAY.json')
    need((canon['v'],canon['h'],canon['R'])==(112,9,408),'current native dimensions')
    need(replay['status']=='PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY','native replay status')
    need(replay['canonical_word_sha256']==sha(base/'CANONICAL-WORD.json.gz')and replay['local_programs_sha256']==sha(base/'LOCAL-PROGRAMS.json.gz'),'native source binding')
    steps=read(base.parent/'STEPS.json');need([x['step']for x in steps]==['native','ledgers','local-replay','wrappers','phases']and all(x['exit_code']==0 for x in steps),'fresh complete five-stage chain')
    phases=read(base/'CLIFFORD-REVIEW.json');need(phases['status']=='PASS_NEW_WORD_EXACT_LOCAL_PHASE_RECIPES','native phase status')
    need(phases['warp_recipes_rank_zero']and phases['warp_recipes_equal_exact_512_column_product']and phases['all_child_equalities_include_global_phase'],'unitary recipes include exact phases')
    cliff=read(base/'CLIFFORD-RECIPES.json');resid=read(base/'RESIDUAL-ADAPTERS.json')
    need(set(cliff)=={'children','endpoint_adapters','warps'},'closed Clifford recipe inventory')
    counts=[all_monomials(cliff),all_monomials(resid)];need(counts==[6278,150],'current full monomial recipe inventory')
    local={};endpoints={}
    for orient,ev in programs.items():
        need(orient in('forward','backward'),'unknown orientation');local[orient]=program_norm(ev,canon)
        need(local[orient]['prefix_bits']==replay['local'][orient]['prefix_bits_upper'],'exact local prefix binding')
        need(Q(local[orient]['prefix_upper'])==Q(replay['local'][orient]['prefix_l1_upper']),'exact Horner envelope binding')
        need(checks[orient]['private_centers_cleared']and checks[orient]['private_coefficient_stream_cleared_after_each_macro']and checks[orient]['zero_buffers_returned_to_zero']==72,'private macro receipt')
        endpoints[orient]=legacy.replay_endpoint(ev,112,408,orient=='backward')
    widths=[len(canon['frames'][canon['final'][224+i]])-len(canon['frames'][canon['start'][224+i]])for i in range(408)]
    need(Counter(widths)=={4:26,5:2,7:62,8:80,9:238},'complete paid width inventory')
    return canon,dict(widths=widths,local=local,endpoints=endpoints,monomial_counts=counts,canonical_word_sha256=sha(base/'CANONICAL-WORD.json.gz'),phase_recipe_sha256=phases['recipe_sha256'])

def array_stream(path):
    dec=json.JSONDecoder();buf='';start=True;end=False
    with gzip.open(path,'rt',encoding='utf8')as f:
        while True:
            chunk=f.read(2**20)
            if not chunk:break
            buf+=chunk;p=0
            while True:
                while p<len(buf)and buf[p].isspace():p+=1
                if start:
                    if p==len(buf):break
                    need(buf[p]=='[','top-level owners array');p+=1;start=False;continue
                if p<len(buf)and buf[p]==',':p+=1;continue
                if p<len(buf)and buf[p]==']':end=True;p+=1;break
                try:z,q=dec.raw_decode(buf,p)
                except json.JSONDecodeError:break
                yield z;p=q
            buf=buf[p:]
            if end:need(not buf.strip()and not f.read().strip(),'trailing owners input');break
    need(end and not start,'truncated owner array')

def orthobasis(q):
    z=next(i for i in range(9)if not(q>>i&1));a=q^(1<<z);o=list(range(9));o[z],o[0]=o[0],o[z]
    B=[(1<<i)^(a if a>>i&1 else 0)for i in o]+[1<<i for i in range(9,73)]
    need(all((x&y).bit_count()%2==int(i==j)for i,x in enumerate(B)for j,y in enumerate(B)),'port orthogonal basis')
    return B

def norm_role(z,plan,parent,providers,bases,ph,cache,at,call,rank,pair,side):
    need(set(z)=={'child','copy','family','helper','offset','owner_replica','port','replica','stage','time','width'},'unknown address-dependent owner descriptor')
    s,r,h=z['stage'],z['replica'],z['helper'];i,orp,p,off,w=z['child'],z['owner_replica'],z['port'],z['offset'],z['width'];key=s,r
    need(key in call and all(type(z[k])is int for k in z),'integer static chart data')
    need(0<=h<408 and w==providers[call[key]['provider']]['widths'][h],'exact current helper width')
    need(0<=orp<plan['T']and 0<=p<112 and z['copy']==112*orp+p,'fixed owner copy')
    need(z['family']==896*orp+(2*pair[i]+side[i])*112+p,'fixed physical family')
    stagepair=next(e['pair']for e in parent['recipe']if e['kind']=='local'and e['stage']==s)
    need(not(orp==r and 2*stagepair*112<=z['family']-896*r<(2*stagepair+2)*112),'helper aliases active data')
    need(z['time']==at[key]and 0<=off and off+w<=rank[i],'static chart slice/time')
    ck=p,i,off,w
    if ck not in cache:
        B=bases[p];pending=list(map(int,ph['recipes'][p]['idle_children'][i]['orthogonal_axes']));need(len(pending)==rank[i],'source idle rank')
        occ=[B.index(v)for v in pending[off:off+w]];sp=[j for j in range(73)if j not in occ][:9-w]
        order=occ+sp+[j for j in range(73)if j not in occ and j not in sp]
        need(len(order)==len(set(order))==73,'static orthogonal coordinate permutation')
        cache[ck]=hashlib.sha256(json.dumps([B[j]for j in order],separators=(',',':')).encode()).hexdigest()
    return key,h,z['family'],cache[ck]

def owners(path,plan,parent,providers,canon,ph):
    order=list(map(tuple,plan['order']));T=plan['T'];need(T==372 and len(order)==9*T and len(set(order))==9*T,'actual current order')
    need(all([s for s,r0 in order if r0==r]==list(range(9))for r in range(T)),'owner-local source stage order')
    at={k:i for i,k in enumerate(order)};call={(e['stage'],e['replica']):e for e in plan['provider_calls']};need(set(call)==set(order),'full dispatch')
    for key,c in call.items():
        need(c['time']==at[key]and c['provider']in providers,'literal dispatch time')
        need(plan['provider_registry'][c['provider']]['widths']==providers[c['provider']]['widths'],'registry current word widths')
    rank={e['child']:e['rank']for e in parent['idle_children']};pair={};side={}
    for e in parent['execution_schedule']:
        if e['kind']=='idle_cover_sweep':
            for sd,ch in enumerate(e['child_indices']):pair[ch]=e['pair'];side[ch]=sd
    bases=[orthobasis(q)for q in canon['ports']];cache={};seen=set();last=None;helpers=set();families=set();total=0;hd=hashlib.sha256();first=None
    for z in array_stream(path):
        if first is None:first=copy.deepcopy(z)
        k,h,f,d=norm_role(z,plan,parent,providers,bases,ph,cache,at,call,rank,pair,side)
        if k!=last:
            if last is not None:need(len(helpers)==408,'complete helper set per call');seen.add(last)
            need(k not in seen,'noncontiguous owner call');last=k;helpers=set();families=set()
        need(h not in helpers and f not in families,'two live roles share one family within an invocation');helpers.add(h);families.add(f)
        hd.update(json.dumps([*k,h,f,d],separators=(',',':')).encode()+b'\n');total+=1
    need(len(helpers)==408,'final complete helper set');seen.add(last);need(seen==set(order)and total==408*9*T,'all owner roles')
    return dict(roles=total,calls=9*T,replicas=T,distinct_static_orthogonal_charts=len(cache),chart_projection_sha256=hd.hexdigest(),cover_dependency='static integers only; no selected-bit address is read'),(first,bases,cache,at,call,rank,pair,side)


def source_schedule(parent,metric):
    metric.derive(parent['recipe']);allowed={'local_cover_sweep','idle_cover_sweep','bridge','terminal','terminal_Y_translations','bank_padding_cover_sweep','translate_every_live_family'}
    events=parent['execution_schedule'];need(len(events)==32 and all(e['kind']in allowed for e in events),'closed global opcode inventory')
    need([e['stage']for e in events if e['kind']=='local_cover_sweep']==list(range(9)),'all nine local sweeps')
    bridges=[(e['src'],e['dst'],e['coefficient'])for e in events if e['kind']=='bridge'];need(bridges==metric.EXPECTED_BRIDGES,'all global bridge routes')
    need([e['kind']for e in events[-2:]]==['bank_padding_cover_sweep','translate_every_live_family'],'final global routes')
    need(parent['m']==73 and parent['cover']=='all matrices d in O(73,2), in lexicographic row order','literal cover domain')
    return dict(source_events=len(events),event_counts=dict(Counter(e['kind']for e in events)),bridges=bridges,all_events_classified=True)

def envelope(local=70,coverbits=37,ownerbits=5,boundarybits=4,reserve=128):
    need(local>=70 and coverbits>=37 and ownerbits>=5 and boundarybits>=4,'undercharged mixed norm factor')
    need(896<=2**(2*ownerbits)and 73<=2*coverbits,'selected-bit and physical owner stock')
    actual=local+coverbits+boundarybits+ownerbits+1+4;conservative=reserve+coverbits+boundarybits+ownerbits+1+4
    need(actual==121 and conservative==179 and conservative<256,'mixed magnitude accounting')
    return dict(actual_prefix_bits=actual,retained_local_reserve=reserve,reserve_prefix_bits=conservative,proposed_payload_bits=256,currently_admitted_payload_bits=2048,denominator_mass_C0_guards='unchanged; not inferred from a norm',paid_moment_change=0,full_256_admission=False)

def controls(program,canon,mono,role,role_args,plan,parent,providers,ph,metric):
    rejected=[]
    def fail(name,fn):
        try:fn()
        except (AssertionError,KeyError,ValueError,IndexError,StopIteration):rejected.append(name);return
        raise AssertionError('negative control accepted: '+name)
    x=copy.deepcopy(program);x.append(['cover_average',0,1]);fail('unknown_cover_mixing_opcode',lambda:program_norm(x,canon))
    x=copy.deepcopy(program);x.append(['phase','cover_fourier']);fail('unrecognized_numerical_phase',lambda:program_norm(x,canon))
    x=copy.deepcopy(mono);x['matrix_rows'][1]=x['matrix_rows'][0];fail('singular_selected_bit_monomial',lambda:monomial(x))
    x=copy.deepcopy(mono);x['cover_address_dependency']='x';fail('selected_address_dependent_cover_chart',lambda:monomial(x))
    fail('undercharge_selected_fibre_dimension',lambda:envelope(coverbits=36))
    fail('undercharge_owner_stock',lambda:envelope(ownerbits=4))
    first,bases,cache,at,call,rank,pair,side=role_args
    x=copy.deepcopy(first);x['width']-=1;fail('wrong_actual_helper_width',lambda:norm_role(x,plan,parent,providers,bases,ph,cache,at,call,rank,pair,side))
    x=copy.deepcopy(first);x['family']+=1;fail('wrong_static_owner_family',lambda:norm_role(x,plan,parent,providers,bases,ph,cache,at,call,rank,pair,side))
    x=copy.deepcopy(first);x['address']='x';fail('address_dependent_owner_descriptor',lambda:norm_role(x,plan,parent,providers,bases,ph,cache,at,call,rank,pair,side))
    x=copy.deepcopy(parent);x['execution_schedule'].append({'kind':'cover_fourier'});fail('unknown_global_cover_kernel',lambda:source_schedule(x,metric))
    x=copy.deepcopy(parent);next(e for e in x['recipe']if e['kind']=='bridge')['dst']=4;fail('bridge_crosses_replica_block',lambda:source_schedule(x,metric))
    # The full-group unitary C on two cover labels maps (1,i) to (1+i,0).
    # Its max-cover norm squared grows from 1 to 2, so fibre locality is essential.
    need(abs((1+1j))**2>1,'cover-unitary counterexample')
    return rejected

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--manifest',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();start=time.monotonic();need(not a.out.exists(),'fresh output required');a.out.mkdir()
    manifest=read(a.manifest);inputs=manifest['inputs']
    def guards():
        for k,v in inputs.items():need(sha(v['path'])==v['sha256'],'input source guard: '+k)
        src=Path(inputs['source_manifest']['path']).parent;inventory=read(src/'MANIFEST.json')
        need(len(inventory)==541 and sha(src/'MANIFEST.json')=='c8ec4d1b7be08d2ad30730a07392ad9cb6d0222f2c35bef43c9a80a39b16e41f','pinned current complete source manifest')
        actual={p.relative_to(src).as_posix():sha(p)for p in src.rglob('*')if p.is_file()and p.relative_to(src).as_posix()!='MANIFEST.json'}
        need(actual==inventory,'all 541 immutable source files, no extras')
        receipt=read(inputs['native_receipt']['path']);cache=Path(inputs['native_receipt']['path']).parent/'native-cache'
        for n,h in receipt['cache_files'].items():need(sha(cache/n)==h,'completed native cache guard '+n)
        for pid,key in [('gauge44','base'),('extra','extra')]:
            d=cache/receipt['providers'][key]['word_sha256']/'local'
            need(Path(inputs[pid+'/canonical']['path']).resolve()==(d/'CANONICAL-WORD.json.gz').resolve(),'provider path bound to completed native receipt')
            need(sha(d/'CANONICAL-WORD.json.gz')==receipt['providers'][key]['complete_native_files']['local/CANONICAL-WORD.json.gz'],'provider canonical native receipt binding')
        pins=read(inputs['primary_pins']['path']);primary=Path(inputs['primary_pins']['path']).parent
        for e in pins['files']:need(sha(primary/Path(e['name']).name)==e['sha256'],'primary preprint source pin '+e['name'])
    guards();legacy=load_module('frozen_endpoint',inputs['legacy_checker']['path'],inputs['legacy_checker']['sha256']);metric=load_module('stream_metric',inputs['stream_checker']['path'],inputs['stream_checker']['sha256'])
    providers={};canon=None
    for pid in('extra','gauge44'):
        c,r=provider(Path(inputs[pid+'/canonical']['path']).parent,legacy);providers[pid]=r
        if canon is None:canon=c
        else:need(c['ports']==canon['ports'],'common ordered ports')
        print('Provider '+pid+' classified and exact endpoints replayed.',flush=True)
    plan=read(inputs['plan']['path']);parent=read(inputs['parent']['path']);ph=read(inputs['data_phases']['path']);need(parent['exact_data_phase_recipe_sha256']==sha(inputs['data_phases']['path']),'global selected-bit phase binding')
    schedule=source_schedule(parent,metric);P,_=metric.derive(parent['recipe']);u=[57,95,108,175,91,142,56,85];v=[124,80,121,147,119,133,76,78]
    need(all(x<=10*y for x,y in zip(metric.mv(P,v),u))and all(x<=10*y for x,y in zip(metric.mv(metric.transpose(P),u),v)),'exact weighted Schur boundary factor')
    own,args=owners(inputs['owners']['path'],plan,parent,providers,canon,ph);print('All '+str(own['roles'])+' current owner roles classified.',flush=True)
    base=Path(inputs['extra/canonical']['path']).parent;prog=read(base/'LOCAL-PROGRAMS.json.gz')['forward'];cliff=read(base/'CLIFFORD-RECIPES.json')
    negative=controls(prog,canon,cliff['children'][0]['left'],None,args,plan,parent,providers,ph,metric);negative.append(bytecode_control(a.out))
    # Reject a forged private boundary even when all event tags remain allowed.
    evil=copy.deepcopy(prog);evil.append(['scalar',['add',['L',112],['L',224],1,1],0])
    try:legacy.replay_endpoint(evil,112,408,False)
    except AssertionError:negative.append('forged_dirty_helper_to_data_response')
    else:raise AssertionError('forged endpoint accepted')
    guards();result=dict(status='PASS_CURRENT_T372_MIXED_FIBRE_FINITE_PREMISES',source_manifest_sha256=sha(a.manifest),checker_sha256=sha(__file__),providers=providers,owners=own,global_schedule=schedule,magnitude=envelope(),negative_controls_rejected=negative,seconds=time.monotonic()-start,scope='Sufficient mixed-cover/fibre magnitude envelope for the exact current providers, static T372 ownership and source controller. Fresh five-stage native evidence is authenticated and exact free-warp endpoints are independently replayed. This certificate does not certify a completed payload-256 release, exact denominator bounds, a changed paid moment, or a new kappa. The independent source arithmetic, mass, C0, owner-window and final admission guards remain required.')
    write_new(a.out/'RESULT.json',result);print(json.dumps({k:v for k,v in result.items()if k not in('providers',)},sort_keys=True),flush=True)
if __name__=='__main__':main()
