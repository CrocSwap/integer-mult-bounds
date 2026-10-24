#!/usr/bin/env python3
"""Actual routed-neutral/full-old-controller invoice and fresh neutral endpoint arithmetic.

No submitted evaluator is imported. The signed recursive profile is exactly
unchanged: this is not a construction/economic gain or a new raw ceiling.
Ordinary/precision/global admission stays separate from numerical funding.
"""
from pathlib import Path
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
import argparse,gzip,json
from exact_moments import encode,need
from fund_uniform_endpoint import evaluate_profiles

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
BUDGET=ROOT/'swarm-provider-audit-sol-high-20261024/agents/budget'
ACTUAL=None
FORWARD=None
ALIASES=HERE.parent/'challenge/CURRENT-HELPER-ALIASES-v2.json'
CTL=ROOT/'swarm-next-gain-sol-high-20261024/repository/research/kappa-backward-controller-20261023/CONTROLLER.json'
REF=ROOT/'swarm-next-gain-sol-high-20261024/agents/numeric/INVOICE-v2.json'


def read(path):
    b=path.read_bytes()
    return json.loads(gzip.decompress(b)if path.suffix=='.gz'else b)


def hist(c):
    return {int(k):v for k,v in c.items()if v}


def tariff(op,q=None):
    if op in ('COPY','CLEAR'):return 2
    if op=='SWAP':return 26
    q=F(q);n,d=abs(q.numerator),q.denominator
    need(n>0 and d&(d-1)==0,'nonzero dyadic scalar')
    if op=='SCALE':
        need(n&(n-1)==0,'dyadic unit SCALE')
        return 2*(abs(n.bit_length()-d.bit_length())+int(q<0))
    need(op=='ADD','scalar tariff alphabet')
    return 2*(3+n.bit_length()-1+n.bit_count()+d.bit_length()-1)


def signed(P,T):
    return {r:T.get(r,0)-P.get(r,0)for r in set(P)|set(T)if T.get(r,0)!=P.get(r,0)}


def invoice():
    pinpath=BUDGET/'inputs/ALL-PINS.json'
    need(sha256(pinpath.read_bytes()).hexdigest()==
         'a37fa9735bbb2697811de72a706b243842d1303243f6e6a0300bd5046d4f3d66',
         'frozen independent provider source manifest changed')
    for row in read(pinpath):
        need(sha256((BUDGET/row['local']).read_bytes()).hexdigest()==row['sha256'],
             'changed frozen provider input '+row['local'])
    packet,aliases,ctl,ref=map(read,[ACTUAL,ALIASES,CTL,REF])
    forward=read(FORWARD)
    need(forward['backward_candidate_sha256']==sha256(ACTUAL.read_bytes()).hexdigest(),
         'forward packet does not bind the exact backward bytes')
    need(forward['aliases_sha256']==packet['aliases_sha256'],'paired aliases changed')
    need(packet['aliases_sha256']==sha256(ALIASES.read_bytes()).hexdigest(),
         'v16 helper aliases changed')
    need(aliases['status']=='INDEPENDENT_SIGNED_PHASE_AND_FULL_ANCHOR_VERIFIED',
         'source alias application not independently accepted')
    word=read(BUDGET/'inputs/WORD.json.gz')['word']
    source=read(BUDGET/'inputs/SOURCE-WORD.json.gz')['canonical']
    provider=read(BUDGET/'inputs/PROVIDER.json')
    native=Counter()
    for e in word:
        if e[0]in ('climb','center'):
            a,b=e[-3:-1];r=e[-1]
            need(abs(len(source['frames'][a])-len(source['frames'][b]))==r,
                 'literal provider paid rank/frame delta')
            native[r]+=1
    modes=set(provider['mode_owners']);need(len(modes)==8,'eight native mode owners')
    oldhelpers=Counter(len(source['frames'][source['final'][r]])-
                       len(source['frames'][source['start'][r]])
                       for r in range(224,632)if r not in modes)
    need(native==Counter({1:2193,2:412,3:510,4:127,5:40})
         and oldhelpers==Counter({4:28,7:7,8:47,9:318}),
         'literal complete comparison source profile')
    ops=packet['operations'];localextra=Counter();fields=set()
    route_word=[['P',[256,2,4,8,16,32,64,128,1]]]
    route_maps=Counter()
    for index,op in enumerate(ops):
        if op['op']=='GAUSSIAN':
            need(op['paid']is True and op['rank']==8
                 and op['operator']=='C_rank8_bits0to7_positive'
                 and op['actual_axes']==list(range(8)),'actual standard paid C8')
            need(0<index<len(ops)-1,'paid C8 route adjacency')
            for adjacent,purpose in [(ops[index-1],'D8paidjobinputaxisroute'),
                                     (ops[index+1],'D8paidjoboutputaxisroute')]:
                need(adjacent['op']=='MONOMIAL' and adjacent['field']==op['field']
                     and adjacent['word']==route_word and adjacent.get('purpose')==purpose,
                     'actual C8 input/output axis0/8 route missing')
                route_maps[purpose]+=1
            need(op['field']not in fields,'distinct paid neutral D8 owner')
            fields.add(op['field']);localextra[8]+=1
    need(len(fields)==len(modes)==8,'all eight original modes explicitly repaired')
    need(route_maps==Counter(D8paidjobinputaxisroute=8,D8paidjoboutputaxisroute=8),
         'all16 paid-child routing maps counted')
    for purpose in ['originalmodecanonicalC8inputalias','restoredmodecanonicalC8outputalias']:
        rows=[o for o in ops if o['op']=='MONOMIAL'and o.get('purpose')==purpose]
        need(len(rows)==8 and {o['field']for o in rows}=={f'h{i}'for i in range(8)}
             and all(o['word']==route_word for o in rows),
             'all16 original-mode canonical C8 aliases required')
    permutation=[256,2,4,8,16,32,64,128,1]
    need({permutation[i]for i in range(8)}=={1<<i for i in range(1,9)}
         and {permutation[i]for i in range(1,9)}=={1<<i for i in range(8)},
         'signed-phase-free bit permutation route proof')
    localpaid=native+localextra;helpers=oldhelpers+localextra
    need(hist(packet['helper_jobs'])==dict(helpers)
         and packet['helper_count']==408,'routed-neutral claimed helper inventory mismatch')
    need(packet['persistent_original_count']==632 and
         packet['owned_entry_count']==packet['owned_exit_zero_count']==17,
         'actual neutral interface domain')
    # Check that exactly the accepted400 native helper aliases were emitted,
    # rather than crediting a count without both physical normalization sides.
    normalizers=[]
    for group in aliases['groups']:
        for owner in group['owners']:
            normalizers.append((f'owner{owner}',group['forward_pre_input_monomial_word'],
                                 group['forward_post_output_monomial_word']))
    need(len(normalizers)==400 and len({r[0]for r in normalizers})==400,
         'all400 distinct accepted native helper roles')
    explicit=Counter((o['field'],json.dumps(o['word'],sort_keys=True),
                      o.get('whole_job_boundary'))
                     for o in ops if o['op']=='MONOMIAL'and'whole_job_boundary'in o)
    expected=Counter()
    for owner,pre,post in normalizers:
        expected[(owner,json.dumps(pre,sort_keys=True),'before provider')]+=1
        expected[(owner,json.dumps(post,sort_keys=True),'after provider')]+=1
    need(explicit==expected,'literal routed-neutral positive helper normalizer rows differ')
    P,T,chron=Counter(),Counter(),[]
    events=Counter();main,idles=Counter(),Counter()
    for index,e in enumerate(ctl['physical_events']):
        events[e[0]]+=1;p,t=Counter(),Counter()
        if e[0]=='LOCAL':
            need(e[3]is True,'all18 standard backward providers')
            p.update(localpaid);t.update(helpers)
        elif e[0]=='QUERY_SHEAR':p[1]+=112
        elif e[0]=='IDLE':
            need(len(e[2])==len(set(e[2])),'whole idle stage set')
            p[8*len(e[2])]+=224;idles.update(p)
        else:need(e[0]in ('ADD','SIGNED_SWAP','Q_POWER'),'old caller ordinary opcode')
        P.update(p);T.update(t)
        chron.append({'index':index,'event':e,'paid':p,'productive':t,
                      'ordinary_record_funded':False})
    for term in ctl['diagonal']:
        need(abs(term[0])==1 and all(v in(0,1)for v in term[1:]),'main diagonal')
        main[1+8*sum(term[1:])]+=112
    T.update(main)
    oldP=Counter({int(k):v for k,v in ref['histograms']['paid'].items()})
    oldT=Counter({int(k):v for k,v in ref['histograms']['productive'].items()})
    expectedP,expectedT=oldP.copy(),oldT.copy()
    expectedP[8]+=144;expectedT[8]+=144
    need(events['LOCAL']==18 and P==expectedP and T==expectedT,
         'full actual neutral/controller census differs')
    need(signed(P,T)==signed(oldP,oldT),'neutral signed profile must be identical')
    need(sum(P.values())==64260 and sum(T.values())==10928,'neutral full counts')
    # Full ordinary subtotals are explicit; no old whole-caller allowance is
    # transferred. Machine/map/native/precision costs remain separate.
    kinds=Counter(o['op']for o in ops)
    coefficients=Counter(o['coefficient']for o in ops if o['op']=='ADD')
    extension=sum(tariff('ADD',q)*n for q,n in coefficients.items())
    extension+=sum(kinds[k]*tariff(k)for k in ('COPY','CLEAR','SWAP'))
    return {'schema':'actual-routed-neutral-standard-p16-invoice/1',
            'status':'INDEPENDENT_LITERAL_INVOICE_WITH_EXTERNAL_PHYSICAL_GATES',
            'source_bindings':[{'path':str(p.relative_to(ROOT)),
                                'sha256':sha256(p.read_bytes()).hexdigest()}
                               for p in [ACTUAL,FORWARD,ALIASES,CTL,REF,pinpath]],
            'local_paid':localpaid,'local_productive_helpers':helpers,
            'helper_normalizer_records':400,'helper_normalizer_maps':800,
            'local_extra_paid':localextra,'local_extra_productive':localextra,
            'paid_child_standard_axes':list(range(8)),
            'paid_child_realized_active_axes':list(range(1,9)),
            'new_helper_canonical_axes':list(range(8)),
            'explicit_paid_child_axis_route_maps':16,
            'explicit_new_helper_axis_alias_maps':16,
            'route_proof':'Plain involutive axis0/8 permutation fixes phases, sendsC8 toD8 andD8 toC8, extends by identity on all other/fibre axes',
            'forward_packet_bound':True,'forward_used_in_old_controller':False,
            'accepted_local_route_receipt_comparison':'PENDING_SEPARATE_SOURCE_BOUND_BINDING',
            'histograms':{'paid':P,'productive':T},'chronology':chron,
            'main':main,'whole_idles':idles,'caller_events':events,
            'paid_count':sum(P.values()),'productive_count':sum(T.values()),
            'paid_rank_mass':sum(r*n for r,n in P.items()),
            'productive_rank_mass':sum(r*n for r,n in T.items()),
            'signed_profile_identical_to_5398':True,
            'economic_profile_gain':0,'raw_moment_delta_all_exponents':0,
            'raw_ceiling_changed':False,
            'local_persistent_arbitrary_inputs':632,'local_owned_arbitrary_inputs':17,
            'local_operation_census':kinds,'local_ADD_coefficients':coefficients,
            'known_local_extension_scalar_tariff':extension,
            'known_provider_scalar_tariff':175022,
            'known_complete_local_scalar_tariff':175022+extension,
            'known_complete_local_monomial_maps':464+kinds['MONOMIAL'],
            'full_ordinary_budget':None,'native_physical_tariff':None,
            'fresh_complete_precision':None,'global_scientific_admission':False,
            'scope':'Every LOCAL/query/wholeidle/main counted. Native and local all-input phase/ownership, '
                    'full ordinary machine work and fresh precision are external root gates. '
                    'This neutral construction supplies no economic saving or new raw root.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--backward',type=Path,required=True)
    parser.add_argument('--forward',type=Path,required=True)
    args=parser.parse_args();args.output_dir.mkdir(parents=True,exist_ok=True)
    ACTUAL=args.backward.resolve();FORWARD=args.forward.resolve()
    inv=invoice();ip=args.output_dir/'INVOICE-NEUTRAL-LITERAL.json'
    need(not ip.exists(),'immutable invoice exists')
    ip.write_text(json.dumps(encode(inv),indent=2,sort_keys=True)+'\n')
    P,T=inv['histograms']['paid'],inv['histograms']['productive']
    result=evaluate_profiles(P,T,F('.003027288235'),F('.003027288245'),1000,
             {'model':'actual-routed-neutral-standard-p16','p':16,'a':7,
              'economic_profile_gain':0,'raw_ceiling_changed':False,
              'possible_gain_type':'tiny compiler/outer headroom only',
              'ordinary_funded':False,'fresh_precision_source_applicable':False,
              'invoice_sha256':sha256(ip.read_bytes()).hexdigest()})
    result['neutral_signed_identity']=True
    fp=args.output_dir/'FUNDING-NEUTRAL-LITERAL.json';need(not fp.exists(),'immutable funding exists')
    fp.write_text(json.dumps(encode(result),indent=2,sort_keys=True)+'\n')
    print(json.dumps(encode({k:result[k]for k in ('status','kappa','tested','alpha_upper',
                    'gamma_upper','delta_upper','j','H','economic_profile_gain',
                    'whole_scientific_admission')})))
