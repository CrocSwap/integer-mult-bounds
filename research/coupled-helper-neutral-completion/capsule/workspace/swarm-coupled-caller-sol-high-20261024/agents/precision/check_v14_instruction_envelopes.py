#!/usr/bin/env python3
"""Fresh data-only v14 literal instruction envelopes and ordinary inventories.

Root executes. No author/scientific module is imported. Source phase/endpoint
admission is reused by exact bindings, not reconstructed from norm checks.
Apache-2.0, Chris R/Clear1nsight; substantial OpenAI Codex assistance.
"""
import argparse,copy,gzip,json,resource,time
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
HERE=Path(__file__).resolve().parent


def need(ok,s):
    if not ok: raise ValueError(s)


def ceil_log2(q):
    q=max(Q(1),Q(q));k=max(0,q.numerator.bit_length()-q.denominator.bit_length())
    return k+int(q>2**k)


def binary_rank(rows):
    piv={}
    for x in rows:
        need(type(x) is int and 0<=x<512,'nine-axis binary row')
        while x:
            j=x.bit_length()-1
            if j in piv:x^=piv[j]
            else:piv[j]=x;break
    return len(piv)


def mono(word):
    c=Counter();need(isinstance(word,list) and 0<len(word)<=128,'bounded literal monomial')
    for g in word:
        c[g[0]]+=1
        if g[0]=='P':need(len(g)==2 and len(g[1])==9 and binary_rank(g[1])==9,'invertible literal permutation')
        elif g[0]=='D':
            need(len(g)==3 and len(g[1])==len(g[2])==9,'diagonal phase arity');binary_rank(g[1])
            need(all(type(x) is int and 0<=x<4 for x in g[2]),'Z4 phase coefficients')
        elif g[0]=='X':need(len(g)==2 and type(g[1]) is int and 0<=g[1]<512,'nine-axis translation')
        elif g[0]=='phase':need(len(g)==2 and type(g[1]) is int and 0<=g[1]<4,'unit absolute phase')
        else:raise ValueError('nonmonomial '+str(g[0]))
    return c


def scalar_tariff(op,q=None):
    if op in ('COPY','CLEAR'):return 2
    if op=='SWAP':return 26
    q=Q(q);a,b=abs(q.numerator),q.denominator
    need(a>0 and b&(b-1)==0,'nonzero dyadic scalar tariff')
    if op=='SCALE':
        need(a&(a-1)==0,'dyadic-unit SCALE')
        return 2*(abs(a.bit_length()-b.bit_length())+int(q<0))
    need(op=='ADD','scalar opcode')
    return 2*(2+a.bit_length()+a.bit_count()+b.bit_length()-1)


class Inventory:
    def __init__(self):
        self.ops=Counter();self.primitives=Counter();self.coefficients=Counter()
        self.Lmax=self.Ljoint=self.height=self.tariff=0
    def add(self,op,q=None,word=None):
        self.ops[op]+=1
        if op in ('ADD','SCALE'):
            q=Q(q);l=ceil_log2(1+abs(q) if op=='ADD' else abs(q))
            self.Lmax+=l;self.Ljoint+=l
            need(q.denominator&(q.denominator-1)==0,'dyadic coefficient height')
            self.height+=l+q.denominator.bit_length()-1
            self.coefficients[op+':'+str(q)]+=1;self.tariff+=scalar_tariff(op,q)
        elif op in ('COPY','CLEAR','SWAP'):
            self.tariff+=scalar_tariff(op)
            self.Ljoint+=int(op=='COPY')
        elif op=='MONOMIAL':self.primitives.update(mono(word))
        else:need(op in ('UNITARY_NATIVE','GAUSSIAN','ZERO_RETAG','ANNOTATION','CHECK_OWNED_ZERO'),'known exact instruction')
    def basis(self,program):
        for e in program:
            need(e[0] in ('add','scale'),'literal basis opcode')
            self.add(e[0].upper(),e[-1])
    def record(self):
        swaps=self.ops['SWAP']
        micro=Counter(self.ops);micro['ADD']+=3*swaps;micro['SCALE']+=swaps;micro.pop('SWAP',None)
        return dict(operations=dict(self.ops),monomial_primitive_occurrences=dict(self.primitives),
                    scalar_coefficients=dict(self.coefficients),scalar_tariff=self.tariff,
                    dyadic_coefficient_height=self.height,
                    field_instruction_interval_exponents=dict(max_field_l2=self.Lmax,joint_field_l2=self.Ljoint),
                    explicit_26_unit_SWAP_microcode=dict(operations=dict(micro),
                        max_field_l2_exponent=self.Lmax+3*swaps,
                        joint_field_l2_exponent=self.Ljoint+3*swaps,
                        additional_height=3*swaps,
                        chart_binding_required=True,
                        word='a+=b; b-=a; a+=b; b*=(-1)',
                        scope='Concrete conservative physical scalar microcode extension; each ADD must have common physical address/chart interface. Bind exact-zero retags where needed. Not silently inherited from completed-SWAP norm one.'),
                    field_residual_sites=sum(self.ops.values()))


def boundary_maps(p,n):
    words=[r['compiled_wrappers'][key]['word'] for r in n['ports'] for key in
           ('backward_input_X','backward_input_Y','backward_output_X','backward_output_Y')]
    words += [r[key]['literal_word'] for r in p['mode_boundaries'] for key in ('input_K','output_N')]
    need(len(words)==464,'complete source boundary map inventory')
    return words


def forward_provider(p,n,w):
    inv=Inventory();groups=[]
    def group(name,fn):
        before=(inv.Lmax,inv.Ljoint,inv.tariff);fn()
        groups.append(dict(stage=name,Lmax=inv.Lmax-before[0],Ljoint=inv.Ljoint-before[1],scalar_tariff=inv.tariff-before[2]))
    group('eight_mode_input_scales',lambda:[inv.add('SCALE',2) for _ in p['mode_boundaries']])
    group('input_basis',lambda:inv.basis(p['input_basis_program']))
    def body():
        for e in w:
            if e[0]=='scalar':
                g=e[1];op=g[0].upper()
                inv.add(op,Q(*g[-2:]) if op in ('ADD','SCALE') else None)
            elif e[0] in ('warp','climb','center'):inv.add('UNITARY_NATIVE' if e[0]=='warp' else 'GAUSSIAN')
            elif e[0]=='zero_retag':inv.add('ZERO_RETAG')
            else:need(e[0] in ('phase','adapter','residual_adapter'),'retained native annotation');inv.add('ANNOTATION')
    group('source_native_word',body)
    group('output_basis',lambda:inv.basis(p['output_basis_program']))
    def cache():
        for r in p['mode_boundaries']:
            inv.add('SCALE',r['cache_scalar']);inv.add('SWAP');inv.add('CLEAR')
    group('eight_cache_output_scales_swaps_clears',cache)
    for word in boundary_maps(p,n):inv.add('MONOMIAL',word=word)
    need(inv.Lmax==18996 and inv.Ljoint==19012,'fresh original provider agrees with accepted two-geometry receipt')
    need(inv.tariff==175022,'fresh original provider scalar tariff')
    return inv,groups


def inverse_provider(p,n,plan):
    inv=Inventory();groups=[]
    need(plan['source_head']=='123ffa6aa7c1866ac60c67739841f71d95b3edf7','exact5411 inverse plan')
    need(plan['inverse_output_basis']==p['input_basis_program'] and
         plan['inverse_input_basis']==p['output_basis_program'],'actual inverse basis recipes')
    def group(name,fn):
        before=(inv.Lmax,inv.Ljoint,inv.tariff);fn()
        groups.append(dict(stage=name,Lmax=inv.Lmax-before[0],Ljoint=inv.Ljoint-before[1],scalar_tariff=inv.tariff-before[2]))
    need(plan['owned_entry_CLEAR']==list(range(632,641)),'nine arbitrary-owned entry clears')
    group('owned_entry_clear9',lambda:[inv.add('CLEAR') for _ in plan['owned_entry_CLEAR']])
    def output():
        for r in p['mode_boundaries']:
            inv.add('SWAP');inv.add('SCALE',1/Q(r['cache_scalar']))
    group('inverse_output_swap_and_cache_scale',output)
    group('inverse_output_basis',lambda:inv.basis(plan['inverse_output_basis']))
    def reverse_body():
        for e in plan['native_reverse_records']:
            op=e['op']
            if op in ('ADD','SCALE'):inv.add(op,e['coefficient'])
            elif op=='ZERO_RETAG':inv.add('ZERO_RETAG')
            elif op=='CHECK_OWNED_ZERO':inv.add(op)
            elif op=='NATIVE_INVERSE_SOURCE':inv.add('UNITARY_NATIVE')
            elif op=='GAUSSIAN_INVERSE_SOURCE':
                need(1<=e['rank']<=9,'positive inverse-child rank')
                inv.add('GAUSSIAN')
            else:need(op=='INVERSE_SOURCE_ANNOTATION','known reverse record');inv.add('ANNOTATION')
    group('literal_inverse_native_plan',reverse_body)
    group('inverse_input_basis',lambda:inv.basis(plan['inverse_input_basis']))
    group('inverse_mode_input_scales',lambda:[inv.add('SCALE',Q(1,2)) for _ in p['mode_boundaries']])
    need(plan['terminal_owned_zero_check_and_CLEAR']==list(range(633,641)),'eight terminal owned returns')
    group('terminal_owned_clear8',lambda:[inv.add('CLEAR') for _ in plan['terminal_owned_zero_check_and_CLEAR']])
    # Exact physical adjoints preserve primitive counts and unit norms. Accepted
    # inverse phase audit binds their actual adjoints; no author evaluator runs.
    for word in boundary_maps(p,n):inv.add('MONOMIAL',word=word)
    need(inv.ops['COPY']==0,'reverse COPY is actual ADD, never a free joint COPY')
    return inv,groups


def outside(d):
    inv=Inventory();ops=d['operations'];pos=[i for i,e in enumerate(ops) if e['op'].startswith('PROVIDER_')]
    need(len(pos)==1,'one actual provider occurrence');pos=pos[0]
    aliasops=ops[pos-400:pos]+ops[pos+1:pos+401]
    need(len(aliasops)==800 and all(e['op']=='MONOMIAL' for e in aliasops),'800 actual alias maps already in outer inventory')
    alias=Counter()
    for e in aliasops:alias.update(mono(e['word']))
    for e in ops:
        op=e['op']
        if op.startswith('PROVIDER_'):continue
        if op in ('ADD','SCALE'):inv.add(op,e['coefficient'])
        elif op=='MONOMIAL':inv.add(op,word=e['word'])
        elif op in ('CLEAR','COPY','ZERO_RETAG'):
            target=e.get('field',e.get('dst',''))
            need(target in {f'c{i}' for i in range(1,9)},'only reused owned observation banks')
            inv.add(op)
        elif op=='GAUSSIAN':need(e['paid'] is True and e['rank']==1,'eight paid observations');inv.add(op)
        elif op=='SWAP':need(e['includes_chart'] is True,'whole-field/chart SWAP');inv.add(op)
        else:raise ValueError('unsupported actual v14 opcode '+op)
    return inv,dict(alias),ops[pos]


def combine(a,b):
    c=Inventory();c.ops=a.ops+b.ops;c.primitives=a.primitives+b.primitives
    c.coefficients=a.coefficients+b.coefficients
    for key in ('Lmax','Ljoint','height','tariff'):setattr(c,key,getattr(a,key)+getattr(b,key))
    return c


def main():
    start=time.monotonic();resource.setrlimit(resource.RLIMIT_CPU,(15,15))
    resource.setrlimit(resource.RLIMIT_AS,(256*1024**2,256*1024**2))
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=HERE.parents[2]);ap.add_argument('--output',type=Path,default=HERE/'V14-INSTRUCTION-ENVELOPES-v1.json');a=ap.parse_args()
    manifest=json.loads((HERE/'V14-SOURCES.json').read_bytes());data={}
    for r in manifest['rows']:
        b=(a.root/r['path']).read_bytes();need(sha256(b).hexdigest()==r['sha256'],'changed input '+r['path'])
        data[r['id']]=json.loads(gzip.decompress(b) if r['path'].endswith('.gz') else b)
    p,n,w=data['provider'],data['normalizers'],data['word']['word'];plan=data['inverse_plan']
    need(data['inverse_acceptance']['inverse_plan_sha256']==sha256((a.root/manifest['by_id']['inverse_plan']).read_bytes()).hexdigest(),'executed independent inverse plan binding')
    need(data['alias_acceptance']['aliases_sha256']==sha256((a.root/manifest['by_id']['aliases']).read_bytes()).hexdigest(),'executed alias proof binding')
    fp,fg=forward_provider(p,n,w);ip,ig=inverse_provider(p,n,plan)
    out=dict(status='PASS_SCOPED_V14_LITERAL_INTERVAL_AND_ORDINARY_INVENTORY',
             provider_forward=fp.record(),provider_forward_stages=fg,
             provider_inverse_fresh=ip.record(),provider_inverse_stages=ig,packets={},
             accepted_inverse_plan='632original+9arbitraryowned phase/source binding retained separately',
             accepted_aliases='17inverse classes+2promotedD8classes; no fullphase replay in this checker')
    for label in ('B','inverse','F'):
        d=data[label];extra,aliases,macro=outside(d)
        need(d['owned_count']==9 and d['persistent_original_count']==632 and d['helper_count']==392,'fresh raw owned/productive directions')
        need(d['aliases_sha256']==data['alias_acceptance']['aliases_sha256'],'same executed alias packet')
        base=fp if label=='B' else ip
        need(macro['op']==('PROVIDER_5402' if label=='B' else 'PROVIDER_5411_INVERSE'),'correct source direction')
        total=combine(base,extra);rec=total.record()
        inverse_translations=0 if label=='B' else ip.ops['GAUSSIAN']
        rec.update(outside=extra.record(),alias_maps_included=800,
                   exact_800_alias_primitive_occurrences=aliases,
                   inverse_child_translation_field_maps=inverse_translations,
                   inverse_child_translation_primitive_X=inverse_translations,
                   new_owned_fields=0,owned_fields_per_occurrence=9,
                   paid_local_profile={'1':2201,'2':412,'3':510,'4':127,'5':40},
                   paid_calls_per_occurrence=3290,autonomous_helper_profile=d['helper_profile'],
                   main240_coupled=True,
                   scalar_tariff_excludes_physical_map_tariff=True)
        # These are fresh computable value bounds, never an admitted new W/P.
        routegroups=(total.ops['MONOMIAL']+total.ops['UNITARY_NATIVE']+
                     total.ops['GAUSSIAN']+inverse_translations+total.ops['ZERO_RETAG']+
                     total.ops['ANNOTATION'])
        rec['raw_staging']=dict(W='UNKNOWN: actual complete global productive outputs',
            P='3290 paid mixed-rank local calls; expanded rank-one P UNKNOWN',
            O='9 per physical local occurrence plus all separately tagged caller/parked banks',
            R_known_field_schema_count=sum(total.ops.values())+inverse_translations,
            G_scalar_plus_unit_overestimate=total.tariff+8*routegroups,
            N='UNKNOWN until complete compiler instance',
            common_1000_record_route_upper=1000*routegroups,
            route_upper_condition='Retained9axis normal-form/coordinate/restoration tariff. Counts are finite primitive schemas, not literal f-dependent tape instructions. Source native child factors/warps are class-bound groups, not new emitted phase recipes.',
            complete_funded=False)
        out['packets'][label]=rec
    need(ip.Lmax==ip.Ljoint,'fresh inverse no COPY geometry difference')
    # Fresh scalar function controls; no candidate semantic evaluator is invoked.
    need(ceil_log2(Q(3,2))==1 and ceil_log2(Q(1,2))==0,'exact upward rational ceiling')
    tmp=Inventory();tmp.add('COPY');need(tmp.Lmax==0 and tmp.Ljoint==1,'COPY geometry')
    tmp=Inventory();tmp.add('ADD',-1);need(tmp.Lmax==tmp.Ljoint==1,'inverse COPY actual ADD')
    need(3*scalar_tariff('ADD',1)+scalar_tariff('SCALE',-1)==scalar_tariff('SWAP'),'actual26unit swap realization')
    out.update(controls=['exact rational ceiling','COPY geometry','inverseCOPYADD','26unitSWAPmicrocode'],
        checker_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),source_manifest_sha256=sha256((HERE/'V14-SOURCES.json').read_bytes()).hexdigest(),
        seconds=time.monotonic()-start,complete_caller=False,new_kappa=None,
        scope='Literal v14 local instruction products under audited unitary native/alias realization. Full native phase, H/Hinv sharp completed map theorem and globalcaller not replayed. Scalar SWAP microcode requires explicit same-chart realization; neither endpoint SWAP norm nor old source bound silently proves machine instruction stability.')
    need(not a.output.exists(),'new immutable output');a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':out['status'],'inverseL':[ip.Lmax,ip.Ljoint],
        'packets':{k:{'field_L':[v['field_instruction_interval_exponents']['max_field_l2'],v['field_instruction_interval_exponents']['joint_field_l2']], 'scalar_tariff':v['scalar_tariff'],'micro_L':[v['explicit_26_unit_SWAP_microcode']['max_field_l2_exponent'],v['explicit_26_unit_SWAP_microcode']['joint_field_l2_exponent']]} for k,v in out['packets'].items()},'seconds':out['seconds']}))


if __name__=='__main__':main()
