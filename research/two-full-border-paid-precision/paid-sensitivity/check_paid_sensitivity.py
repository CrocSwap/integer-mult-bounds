#!/usr/bin/env python3
"""Exact actual-paid-site scalar-relative fault witnesses for the Laurent word.

SPDX-License-Identifier: Apache-2.0
Yiyang (@Lyy-iiis), with substantial OpenAI Codex assistance.
This is a sufficient witness census in the independent operator-error model.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
import gzip
import json
from pathlib import Path
import sys
sys.dont_write_bytecode=True

SOURCE_PIN='7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05'
PROFILE={1:2201,2:412,3:510,4:127,5:40,8:8}
SPLIT={1:[1],2:[2],3:[3],4:[3,1],5:[3,2],8:[3,3,2]}


def require(ok,message):
    if not ok:
        raise ValueError(message)


def canonical_json(value):
    normalized=json.loads(json.dumps(value,allow_nan=False))
    return json.dumps(normalized,sort_keys=True,separators=(',',':'),allow_nan=False)


def compare_json(expected,actual):
    require(canonical_json(expected)==canonical_json(actual),
            'complete typed decoded reference receipt equality')


def add(a,b,c=F(1)):
    for k,v in b.items():
        z=a.get(k,F())+c*v
        if z:
            a[k]=z
        else:
            a.pop(k,None)


def scale(a,c):
    return {k:c*v for k,v in a.items() if c*v}


def owner(ref):
    require(ref[0] in ('L','C'),'known owner type')
    return ref[1] if ref[0]=='L' else 632


def paid_event(e):
    if e[0]=='climb':
        return e[2],e[-1]
    if e[0]=='center':
        return 632,e[-1]
    return None


def first(row):
    if not row:
        return None
    k=min(row)
    return [k,str(row[k])]


def delta_zero_certificate(canonical,programs):
    """The inherited warp K_G is a homogeneous quadratic-phase monomial.

    K_G|x>=i^q_M(Gx)|Gx>, where q_M has no constant term. Its inverse,
    transpose and inverse transpose all fix address zero with phase one. Check
    every actual matrix is invertible and every used signed symbol is bound.
    This is the only address specialization used by the scalar replay.
    """
    matrices={}
    for warp in canonical['warps']:
        op=warp['op'];columns=warp['G_columns']
        require(op>0 and op not in matrices,'unique positive warp identifier')
        require(len(columns)==9 and all(0<x<512 for x in columns),'nine binary warp columns')
        span={0}
        for x in columns:
            span |= {y^x for y in tuple(span)}
        require(len(span)==512,'invertible homogeneous warp fixes delta zero')
        matrices[op]=columns
    uses=Counter()
    for direction,program in programs.items():
        for e in program:
            if e[0]=='warp':
                require(abs(e[2]) in matrices,'actual warp bound to its homogeneous matrix')
                uses[direction]+=1
    return {'distinct_invertible_matrices':len(matrices),
            'actual_warp_uses':dict(uses),
            'semantics':'Inherited K_G|x>=i^q_M(Gx)|Gx>, M=I+G^-T G^-1 and q_M(y)=sum M_ii*y_i+2*sum_(i<j)M_ij*y_i*y_j mod4. G0=0 and q_M(0)=0, so K_G, its inverse, transpose and inverse transpose fix delta_0 with phase exactly1. No affine offset or independent global phase is introduced.'}


def forward(program,which):
    rows=[{} for _ in range(633)]
    for i in range(112):
        rows[i]={i:F(1)}
        if which=='upper':
            rows[112+i]={i:F(1)}
    prefixes={}
    profile=Counter()
    for ix,e in enumerate(program):
        p=paid_event(e)
        if p is not None:
            a,r=p
            profile[r]+=1
            prefixes[ix]={'owner':a,'rank':r,'kind':e[0],
                          'source_event':e,
                          'nonzero_inputs':len(rows[a]),'prefix_witness':first(rows[a])}
        if e[0]=='scalar':
            g=e[1];op=g[0];a=owner(g[1])
            if op=='clear':
                rows[a]={}
            elif op=='copy':
                rows[a]=dict(rows[owner(g[2])])
            elif op=='add':
                add(rows[a],rows[owner(g[2])],F(g[3],g[4]))
            elif op=='scale':
                rows[a]=scale(rows[a],F(g[2],g[3]))
            else:
                raise ValueError('unknown scalar instruction')
        else:
            require(e[0] in ('climb','center','warp','phase','adapter','residual_adapter'),
                    'known source event')
    require(dict(profile)==PROFILE,'complete actual paid profile')
    for i in range(112):
        require(rows[i]==({i:F(1)} if which=='lower' else {}),
                'exact scalar source main X endpoint')
        require(rows[112+i]=={i:F(1)},'exact scalar source main Y endpoint')
    require(all(not x for x in rows[224:]),'all helper/owned outputs restore on these inputs')
    return prefixes


def backward(program,which):
    # Entries are coefficients of independent final observations, not state.
    columns=[{} for _ in range(633)]
    for i in range(112):
        columns[i]={i:F(1)}
        if which=='lower':
            columns[112+i]={i:F(-1)}
    for h in range(224,632):
        columns[h]={112+h-224:F(1)}
    suffixes={}
    clear_controls=[]
    for ix in reversed(range(len(program))):
        e=program[ix]
        p=paid_event(e)
        if p is not None:
            a,r=p
            suffixes[ix]={'nonzero_observations':len(columns[a]),
                          'suffix_witness':first(columns[a]),
                          'main_visible':any(k<112 for k in columns[a]),
                          'helper_visible':any(k>=112 for k in columns[a])}
        if e[0]=='scalar':
            g=e[1];op=g[0];a=owner(g[1])
            if op=='clear':
                # A fault immediately BEFORE an owned clear has no output.
                columns[a]={}
                clear_controls.append({'event':ix,'owner':a,'before_clear_column_zero':True})
            elif op=='copy':
                b=owner(g[2]);require(a!=b,'source copy has distinct owners')
                add(columns[b],columns[a])
                columns[a]={}
            elif op=='add':
                b=owner(g[2]);require(a!=b,'source add has distinct owners')
                add(columns[b],columns[a],F(g[3],g[4]))
            elif op=='scale':
                columns[a]=scale(columns[a],F(g[2],g[3]))
    for i in range(112):
        if which=='lower':
            require(not columns[i],'baseline lower X input has zero unscaled observation')
        else:
            z=dict(columns[i]);add(z,columns[112+i])
            require(not z,'baseline diagonal upper input has zero unscaled observation')
    require(len(clear_controls)==16,'all sixteen actual owned clears handled')
    return suffixes,clear_controls


def decode_source(raw):
    require(sha256(raw).hexdigest()==SOURCE_PIN,'pinned actual round-three source')
    return json.loads(gzip.decompress(raw))


def direct_fault(program,which,input_port,event,eta):
    """Separate one-column finite execution, without prefix/suffix tables."""
    values=[F() for _ in range(633)]
    values[input_port]=F(1)
    if which=='upper':
        values[112+input_port]=F(1)
    for ix,e in enumerate(program):
        if ix==event:
            p=paid_event(e)
            require(p is not None,'direct fault attached to an actual paid owner')
            values[p[0]]*=1+eta
        if e[0]!='scalar':
            continue
        g=e[1];a=owner(g[1])
        if g[0]=='clear':
            values[a]=F()
        elif g[0]=='copy':
            values[a]=values[owner(g[2])]
        elif g[0]=='add':
            values[a]+=F(g[3],g[4])*values[owner(g[2])]
        elif g[0]=='scale':
            values[a]*=F(g[2],g[3])
        else:
            raise ValueError('direct replay unknown scalar')
    return [values[i]-(values[112+i] if which=='lower' else 0)
            for i in range(112)]+values[224:632]


def targeted_controls(raw,data,calls):
    def rejects(fn,label):
        try:
            fn()
        except ValueError:
            return {'name':label,'rejected':True}
        raise ValueError('negative control was accepted: '+label)
    bad_warps=deepcopy(data['canonical'])
    bad_warps['warps'][0]['G_columns'][0]=0
    no_final_clear=deepcopy(data['programs']['forward'])
    last_clear=max(i for i,e in enumerate(no_final_clear)
                   if e[0]=='scalar' and e[1][0]=='clear')
    del no_final_clear[last_clear]
    controls=[rejects(lambda:decode_source(raw+b'\n'),'changed source bytes'),
        rejects(lambda:delta_zero_certificate(bad_warps,data['programs']),
                'noninvertible homogeneous warp'),
        rejects(lambda:forward(no_final_clear,'lower'),'omit final owned clear')]
    boolean_rank=deepcopy(calls)
    changed=next(s for s in boolean_rank[0]['sites'] if s['rank']==1)
    changed['rank']=True
    controls.append(rejects(lambda:compare_json({'calls':boolean_rank},{'calls':calls}),
                            'Boolean substituted for an actual paid rank integer'))
    samples=[]
    for call in calls:
        rows=call['sites'];which=call['call'];program=data['programs'][call['source_orientation']]
        predicates=[('center',lambda s:s['kind']=='center' and s['epsilon_minus_one_witness']),
            ('main_rank1',lambda s:s['rank']==1 and s['epsilon_minus_one_witness'] and s['main_visible']),
            ('helper_only',lambda s:s['epsilon_minus_one_witness'] and not s['main_visible']),
            ('zero_prefix',lambda s:s['prefix_witness'] is None),
            ('zero_suffix',lambda s:s['suffix_witness'] is None)]
        for name,predicate in predicates:
            selected=next((s for s in rows if predicate(s)),None)
            if selected is None:
                continue
            p=selected['prefix_witness'];s=selected['suffix_witness']
            input_port=p[0] if p else 0
            for eta in (F(1,8),F(-1,4)):
                actual=direct_fault(program,which,input_port,selected['event'],eta)
                if selected['epsilon_minus_one_witness']:
                    expected=eta*F(p[1])*F(s[1])
                    require(actual[s[0]]==expected and expected!=0,
                            'direct finite fault agrees with source prefix/suffix coefficient')
                else:
                    require(not any(actual),'direct finite fault confirms silent specialized site')
            samples.append({'call':which,'sample':name,'event':selected['event'],
                            'eta_values':['1/8','-1/4'],'passed':True})
    return {'rejecting_controls':controls,'independent_finite_fault_samples':samples}


def conditional_budget(canonical,main_profile):
    helpers=Counter()
    for i in range(224,632):
        helpers[len(canonical['frames'][canonical['final'][i]])-
                len(canonical['frames'][canonical['start'][i]])]+=1
    require(dict(helpers)=={4:28,7:7,8:47,9:326},'source productive helper widths')
    target=Counter({r:2*n for r,n in helpers.items()});target[17]+=224
    baseline=Counter()
    for r,n in PROFILE.items():
        for part in SPLIT[r]:
            baseline[part]+=2*n
    surcharge=main_profile[1]
    require(surcharge==3608,'main-output-only rank-one pole witness count')
    funded=baseline.copy();funded[1]+=surcharge
    mass=lambda profile:sum(r*n for r,n in profile.items())
    require(min(target)==4 and max(funded)==3,'retained strict target/paid rank separation')
    require(mass(target)==10750 and mass(baseline)==10654 and mass(funded)==14262,
            'complete original and funded rank masses')
    require(mass(funded)>mass(target),'funded invoice fails rank-mass test')
    return {'target_profile':dict(sorted(target.items())),
        'baseline_split_profile':dict(sorted(baseline.items())),
        'charged_extra_rank_one_jobs':surcharge,
        'funded_profile_using_only_rank_one_witnesses':dict(sorted(funded.items())),
        'target_rank_mass':mass(target),'baseline_paid_rank_mass':mass(baseline),
        'funded_paid_rank_mass':mass(funded),
        'conditional_precision_cost_policy':'Each independently variable relative paid-operator error is bounded by 2^-w on unit input. The raw tariff uses w=k+o(k), and leading cost is linear in w. Requiring output error O(2^-k), with epsilon=O(2^-k), forces each witnessed site to w>=2k-O(1); we charge only one additional H1 at each of the3608 main-visible rank-one split jobs.',
        'exact_all_concave_moments_certificate':{
            'range':'0 <= t <= 1; H_r=r^t',
            'target_upper':'T_t <= 4^(t-1) * 10750',
            'funded_paid_lower':'P_t >= 3^(t-1) * 14262',
            'ratio_upper':'T_t/P_t <= (4/3)^(t-1) * 5375/7131 <= 5375/7131 < 1',
            'constant_ratio':str(F(mass(target),mass(funded)))},
        'scope':'Rejection of this independent-error, linear-precision raw invoice policy; not a multiplication lower bound, correlated-error impossibility, or a claim that every existing compiler has this baseline cost law.'}


def run(source):
    raw=source.read_bytes()
    data=decode_source(raw)
    require({int(k):v for k,v in data['canonical']['local_profile'].items()}==PROFILE,
            'literal canonical paid profile')
    delta_zero=delta_zero_certificate(data['canonical'],data['programs'])
    results=[]
    for which,direction in [('lower','forward'),('upper','backward')]:
        program=data['programs'][direction]
        prefix=forward(program,which)
        suffix,clears=backward(program,which)
        flagged=Counter();flagged_split=Counter();silent=Counter();kinds=Counter()
        main_split=Counter();helper_only_split=Counter()
        rows=[]
        for ix,p in sorted(prefix.items()):
            s=suffix[ix]
            active=p['prefix_witness'] is not None and s['suffix_witness'] is not None
            row={'event':ix,**p,**s,'epsilon_minus_one_witness':active}
            if active:
                a,c=p['prefix_witness'];b,d=s['suffix_witness']
                row['pole_coefficient_ignoring_common_sign']=str(F(c)*F(d))
                row['input_original_Y_port']=a
                row['output_observation']=('main_X',b) if b<112 else ('helper',b-112+224)
                flagged[p['rank']]+=1
                kinds[p['kind']]+=1
                for part in SPLIT[p['rank']]:
                    flagged_split[part]+=1
                    (main_split if s['main_visible'] else helper_only_split)[part]+=1
            else:
                silent[p['rank']]+=1
            rows.append(row)
        results.append({'call':which,'source_orientation':direction,
                        'actual_event_count':len(program),'paid_site_count':len(rows),
                        'flagged_profile':dict(sorted(flagged.items())),
                        'flagged_split_profile':dict(sorted(flagged_split.items())),
                        'main_output_flagged_split_profile':dict(sorted(main_split.items())),
                        'helper_only_flagged_split_profile':dict(sorted(helper_only_split.items())),
                        'not_witnessed_profile':dict(sorted(silent.items())),
                        'flagged_kinds':dict(kinds),
                        'owned_clear_controls':clears,'sites':rows})
    total=Counter();main_total=Counter();helper_only_total=Counter()
    for r in results:
        total.update(r['flagged_split_profile'])
        main_total.update(r['main_output_flagged_split_profile'])
        helper_only_total.update(r['helper_only_flagged_split_profile'])
    require(sum(total.values())>28,'nontrivial source-bound precision tariff witness')
    min_coefficient=min(abs(F(s['pole_coefficient_ignoring_common_sign']))
        for call in results for s in call['sites'] if s['epsilon_minus_one_witness'])
    require(min_coefficient>=F(1,8),'uniform recorded pole coefficient lower bound')
    return {'status':'PASS_EXACT_ACTUAL_PAID_SITE_POLE_WITNESSES',
            'source_sha256':SOURCE_PIN,'source_profile_head':'0ce1b5c9fb7163d0b2f0ac3db95fc418dbbcec62',
            'actual_word_source':{'head':'1eb8da6cfb35512c0cc2533413e5ca42f48e13c6',
                'path':'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz',
                'git_blob':'46d929df83817b85a5387bcdb9745e0627d6366e',
                'retrieved_unchanged_via':'PR4694 head2add42d1edf14a263abe90a3bcde67fc1ba30768 research/retained-center-extension/inputs/round3-native.json.gz'},
            'actual_single_call_profile':PROFILE,
            'delta_zero_certificate':delta_zero,
            'relative_fault_model':'At one paid normalized Gaussian operator G, substitute (1+eta)G; all other paid operators exact. Retained monomial normalizers remain unchanged.',
            'address_witness':'Logical address delta_0, fixed by every source linear/quadratic K_G warp. Lower inputs use arbitrary original Y on Q delta_0; upper inputs use Q D_lower^-1 delta_0. Extend to every fiber count by tensoring the address vectors.',
            'observations':{'lower':'logical final X_i-Y_i and every helper output before source output normalizers',
                            'upper':'logical final X_i and every helper output before source output normalizers'},
            'total_flagged_split_profile':dict(sorted(total.items())),
            'main_output_flagged_split_profile':dict(sorted(main_total.items())),
            'helper_only_flagged_split_profile':dict(sorted(helper_only_total.items())),
            'total_flagged_split_calls':sum(total.values()),
            'minimum_recorded_absolute_pole_coefficient':str(min_coefficient),
            'uniform_precision_implication':'For fixed epsilon<=2^(-k-1), independent unit-input operator tolerance2^-w_j and uniform output error<=2^-k require w_j>=2*k-2 at every witnessed site. This is a worst-case per-site tolerance contract, not a statement about correlated or input-adaptive errors.',
            'conditional_precision_budget':conditional_budget(data['canonical'],main_total),
            'controls':targeted_controls(raw,data,results),
            'scope':'Sufficient exact pole witnesses for individual independent paid-site scalar-relative errors, not all error directions and not a correlated-circuit impossibility theorem. Unflagged sites are not certified safe. Scalar/route rounding and helpers arbitrary baseline inputs are not priced by this witness census.',
            'calls':results}


if __name__=='__main__':
    ap=argparse.ArgumentParser()
    source_relative=Path('research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz')
    default_source=next((p/source_relative for p in Path(__file__).resolve().parents
                         if (p/source_relative).is_file()),None)
    ap.add_argument('--source',type=Path,default=default_source)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--expected',type=Path,help='Compare decoded JSON payload, independent of gzip container bytes')
    args=ap.parse_args()
    require(args.source is not None,'provide --source when outside the repository input layout')
    require(not args.out.exists(),'fresh output receipt')
    result=run(args.source)
    result['checker_sha256']=sha256(Path(__file__).read_bytes()).hexdigest()
    if args.expected:
        expected=args.expected.read_bytes()
        if args.expected.suffix=='.gz':
            expected=gzip.decompress(expected)
        compare_json(json.loads(expected),result)
    payload=(json.dumps(result,sort_keys=True,indent=2)+'\n').encode()
    args.out.write_bytes(gzip.compress(payload,mtime=0) if args.out.suffix=='.gz' else payload)
    print(json.dumps({'status':result['status'],'flagged_split':result['total_flagged_split_profile'],
        'calls':[{k:r[k] for k in ('call','paid_site_count','flagged_profile','not_witnessed_profile','flagged_kinds')} for r in result['calls']]}))
