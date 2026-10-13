"""Fresh call-specific mixed-provider finite invoice.

Prepared with OpenAI Codex assistance, Apache-2.0. The scalar/Horner recount
and finite inequalities are adapted from the retained PR558 -> PR552 ->
PR531 invoice_final.py, whose notices and sources are preserved in the package.
Every call selects a hash-bound provider. Shared compiler reserves use maxima;
primitive work, coefficient work, local children and wrappers are also summed
from actual selected provider/orientation records.
"""
import argparse, gzip, hashlib, json
import sys as _s,pathlib as _p;_s.path.insert(0,str(_p.Path(__file__).resolve().parent))
from witness import *
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
assert __debug__, 'Assertions required'

def read(path):
    data=path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix=='.gz' else data)
def filehash(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def contenthash(path):
    data=path.read_bytes()
    return hashlib.sha256(gzip.decompress(data) if path.suffix=='.gz' else data).hexdigest()
def programhash(events):
    return hashlib.sha256(json.dumps(events,separators=(',',':')).encode()).hexdigest()

def recount_provider(local_dir, registry):
    cp=local_dir/'CANONICAL-WORD.json.gz'; pp=local_dir/'LOCAL-PROGRAMS.json.gz'
    rp=local_dir/'INDEPENDENT-LOCAL-REPLAY.json'
    w,programs,replay=read(cp),read(pp),read(rp)
    checks=read(local_dir/'LOCAL-CHECKS.json')
    assert set(programs)=={'forward','backward'}
    assert replay['status']=='PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY'
    assert replay['canonical_word_sha256']==filehash(cp)==registry['canonical_word_sha256']
    assert replay['local_programs_sha256']==filehash(pp)==registry['local_programs_sha256']
    assert programs==registry['local_programs']
    assert checks==registry['local_program_checks']
    assert filehash(local_dir/'CLIFFORD-RECIPES.json')==registry['exact_local_clifford_recipe_sha256']
    assert filehash(local_dir/'RESIDUAL-ADAPTERS.json')==registry['residual_adapter_sha256']
    v,helpers,h,m=w['v'],w['R'],w['h'],73
    assert (v,helpers,h,len(w['centers']))==(geo.v,geo.helpers,geo.h,geo.centres)
    assert registry['v']==v and registry['R']==helpers and registry['h']==h
    assert registry['ports']==w['ports'] and registry['centers']==w['centers']
    assert replay['v']==v and replay['helpers']==helpers
    n=2*v+helpers
    widths = [h-len(w['frames'][f]) for f in w['start'][2*v:]]
    assert len(widths) == helpers
    entrances = {r: f for r, f in enumerate(w['start']) if r >= 2*v and f != 0}
    entering = len(entrances)
    assert entering == replay['entering_helpers']
    local = {}
    for orientation, events in programs.items():
        # Endpoint equality and native frames were already independently
        # replayed on all n columns in the hash-bound receipt above.
        env = {('L', r): Q(1) for r in range(n)}
        peak = Q(1)
        real = macros = workops = 0
        paid = Counter()
        wrappers = {'pre': set(), 'post': set()}
        for event in events:
            tag = event[0]
            if tag == 'climb':
                paid[event[5]] += 1
            elif tag == 'center':
                paid[event[4]] += 1
            elif tag == 'residual_adapter':
                _, kind, register, frame = event
                assert kind in wrappers and entrances.get(register) == frame
                assert register not in wrappers[kind]
                wrappers[kind].add(register)
            elif tag == 'scalar':
                macros += 1
                scalar = event[1]
                op, target = scalar[0], tuple(scalar[1])
                if op == 'clear':
                    env[target] = Q(0)
                    count = 1
                elif op == 'copy':
                    env[target] = env[tuple(scalar[2])]
                    count = 1
                elif op == 'scale':
                    q = Q(scalar[2], scalar[3])
                    numerator, denominator = abs(q.numerator), q.denominator
                    assert numerator and numerator & (numerator-1) == 0
                    assert denominator & (denominator-1) == 0
                    env[target] *= abs(q)
                    count = abs(numerator.bit_length()-denominator.bit_length()) + int(q < 0)
                elif op == 'add':
                    source = tuple(scalar[2])
                    q = Q(scalar[3], scalar[4])
                    numerator, denominator = abs(q.numerator), q.denominator
                    assert source != target and numerator > 0
                    assert denominator & (denominator-1) == 0
                    acc, count = 0, 1  # clear coefficient work
                    for i, bit in enumerate(bin(numerator)[2:]):
                        if i:
                            acc *= 2
                            count += 1
                            peak = max(peak, acc*env[source])
                        if bit == '1':
                            acc += 1
                            count += 1
                            peak = max(peak, acc*env[source])
                    value = Q(acc)
                    for _ in range(denominator.bit_length()-1):
                        value /= 2
                        count += 1
                        peak = max(peak, value*env[source])
                    assert value == abs(q)
                    count += 2  # signed accumulation and work clear
                    env[target] = env.get(target, Q(0)) + abs(q)*env[source]
                    workops += count
                else:
                    raise AssertionError(op)
                real += 2*count
                peak = max(peak, env[target])
            else:
                assert tag in ('adapter', 'phase')
        assert wrappers['pre'] == wrappers['post'] == set(entrances)
        assert all(value == 0 for register, value in env.items() if register[0] == 'C')
        prior = replay['local'][orientation]
        assert prior['all_exact_columns'] == n and prior['private_work_erased']
        assert peak == Q(prior['prefix_l1_upper']) and peak < 2**prior['charged_payload_bits']
        bits = peak.numerator.bit_length()-peak.denominator.bit_length()+1
        assert bits == prior['prefix_bits_upper']
        assert real == checks[orientation]['real_component_primitive_bound']
        assert macros == checks[orientation]['scalar_macros']
        assert dict(paid) == {int(r): count for r, count in checks[orientation]['paid_profile'].items()}
        assert dict(paid) == {int(r): count for r, count in replay['paid_profiles'][orientation].items()}
        local[orientation] = dict(
            events=len(events), macros=macros, real_component_primitives=real,
            prefix_l1=str(peak), prefix_bits=bits,
            coefficient_work_primitive_count=workops, all_exact_columns=n,
            dirty_helper_columns=helpers, all_dirty_helper_columns_restored=True,
            private_centres_and_coefficient_work_cleared=True,
            pre_wrappers=len(wrappers['pre']), post_wrappers=len(wrappers['post']),
            endpoint_evidence='Hash-bound fresh INDEPENDENT-LOCAL-REPLAY.json')

    centres = len(w['centers'])
    children = sum(checks['forward']['paid_profile'].values())
    assert checks['forward']['paid_profile'] == checks['backward']['paid_profile']
    macro_bound = max(row['macros'] for row in local.values())
    compiler = 64*(m+1)**3
    adapters = 16*(macro_bound+children+n+centres)+64*m
    primitive_bound = max(row['real_component_primitives'] for row in local.values())+adapters*compiler

    assert widths==registry['widths']
    artifacts={f.name:filehash(f) for f in local_dir.iterdir() if f.is_file()}
    phase_review=read(local_dir/'CLIFFORD-REVIEW.json')
    semantic_phase=hashlib.sha256(json.dumps({k:v for k,v in phase_review.items()if k!='seconds'},sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return dict(local=local,helpers=helpers,centres=centres,v=v,h=h,n=n,
                entering_helpers=entering,entrance_rank=sum(h-width for width in widths),
                width_inventory=dict(sorted(Counter(widths).items())),widths=widths,
                local_adapters=adapters,local_primitive_bound=primitive_bound,
                compiler=compiler,children=children,artifacts=artifacts,
                paid_profile=checks['forward']['paid_profile'],
                program_hashes={o:programhash(events) for o,events in programs.items()},semantic_artifact_sha256={'CLIFFORD-REVIEW.json':semantic_phase})


def run(base, hosted, audit, out, retained_invoice=None):
    local_dir=base/'split-centres'
    parent=read(local_dir/'GLOBAL-TEMPLATE.json.gz')
    template_path=hosted/'GLOBAL-TEMPLATE.json.gz'
    template=read(template_path); summary=read(hosted/'HOSTED.json')
    owners=read(audit/'OWNERS-AND-PROFILE.json'); control=read(audit/'ASYNC-AUDIT.json')
    template_hash=contenthash(template_path)
    assert template_hash==control['complex_template_sha256']==owners['template_sha256']==summary['template_sha256']
    assert owners['status']=='PASS_INDEPENDENT_ASYNC_OWNERS_AND_PROFILE'
    assert template['recipe']==parent['recipe']
    assert 'local_programs' not in template
    assert set(template['local_providers'])==set(PIDS)
    providers={pid:recount_provider(base/'providers'/pid,registry)
               for pid,registry in template['local_providers'].items()}
    for pid,p in providers.items():
        assert owners['provider_phase_semantic_sha256'][pid]==control['provider_phase_semantic_sha256'][pid]==p['semantic_artifact_sha256']['CLIFFORD-REVIEW.json']
        # The fresh controller admission must cite precisely these provider bytes.
        for name in ('CANONICAL-WORD.json.gz','LOCAL-PROGRAMS.json.gz','LOCAL-CHECKS.json',
                     'INDEPENDENT-LOCAL-REPLAY.json','CLIFFORD-RECIPES.json',
                     'CLIFFORD-REVIEW.json','RESIDUAL-ADAPTERS.json'):
            path='providers/'+pid+'/'+name
            assert summary['source_artifacts'][path]==p['artifacts'][name]
            assert owners['source_artifacts'][path]==p['artifacts'][name]
    v,helpers,h,m,centres,n=geo.v,geo.helpers,geo.h,73,geo.centres,geo.columns
    stages,replicas,blocks_per_stream=geo.stages,geo.replicas,4
    call_count=len(template['calls'])
    assert call_count==stages*replicas==control['complete_invocations']
    assert control['one_owner_per_complete_invocation']
    assert len({(c['stage'],c['replica']) for c in template['calls']})==call_count
    parent_calls={(c['stage'],c['replica']):c for c in parent['calls']}
    sweeps=[e for e in template['execution_schedule'] if e['kind']=='local_cover_sweep']
    assert len(sweeps)==call_count
    selected=[]; selected_paid=Counter(); provider_counts=Counter(); orientation_counts=Counter()
    scalar=coefficient_work=macros=0; wrapper_factors=0
    factors_per_wrapper=2*(m-1)
    for c in template['calls']:
        pid,orientation=c['provider_id'],c['orientation']; p=providers[pid]
        old=parent_calls[(c['stage'],c['replica'])]
        assert orientation==old['orientation'] and c['owners'][:2*v]==old['owners'][:2*v]
        assert c['local_program_sha256']==p['program_hashes'][orientation]
        r=p['local'][orientation]
        scalar+=r['real_component_primitives']; coefficient_work+=r['coefficient_work_primitive_count']; macros+=r['macros']
        wrapper_factors+=(r['pre_wrappers']+r['post_wrappers'])*factors_per_wrapper
        provider_counts[pid]+=1; orientation_counts[(pid,orientation)]+=1
        selected_paid.update({int(k):v for k,v in p['paid_profile'].items()})
        selected.append(dict(stage=c['stage'],replica=c['replica'],provider_id=pid,orientation=orientation,
                             program_sha256=c['local_program_sha256'],events=r['events'],macros=r['macros'],
                             real_component_primitives=r['real_component_primitives'],
                             coefficient_work_primitive_count=r['coefficient_work_primitive_count'],
                             entering_helpers=p['entering_helpers'],entrance_rank=p['entrance_rank'],
                             pre_wrappers=r['pre_wrappers'],post_wrappers=r['post_wrappers']))
    assert provider_counts==COUNTS
    # The sweep registry is executable: no hidden use of the historical supplier.
    by_call={(c['stage'],c['replica']):c for c in template['calls']}
    for e in sweeps:
        c=by_call[(e['stage'],e['replica'])]
        assert e['provider_id']==c['provider_id']
    assert set(p['compiler'] for p in providers.values())=={64*(m+1)**3}
    compiler=64*(m+1)**3
    adapters=max(p['local_adapters'] for p in providers.values())
    primitive_bound=max(p['local_primitive_bound'] for p in providers.values())
    bridge_steps=sum(event['kind']=='bridge' for event in parent['recipe'])
    bridge_sweeps=sum(event['kind']=='bridge' for event in template['execution_schedule'])
    assert bridge_sweeps==replicas*bridge_steps
    bridge_additions=2*v*bridge_sweeps
    shifts=blocks_per_stream*v*replicas; moves=2*shifts
    parent_live,parent_physical=parent['live'],parent['physical']
    data_stock=2*v*blocks_per_stream*replicas
    assert (parent_live-data_stock)%stages==0
    parent_banks=(parent_live-data_stock)//stages
    assert parent_banks>=0 and parent_physical==parent_live+helpers+centres+2
    nonlocal_items=(4*v*replicas*stages+2*v*replicas*stages+2*call_count*helpers
        +sum(child['replicas'] for child in parent['idle_children'])+stages*parent_banks
        +bridge_additions+shifts+moves+parent_live+parent_physical+wrapper_factors)
    outside=8*nonlocal_items+64*m
    parent_pervertex=(scalar+bridge_additions+shifts+moves+parent_live
        +(call_count*adapters+outside)*compiler+64*parent_physical)
    live,physical=template['live'],template['physical']
    mass,profile=owners['rank_mass'],owners['paid_profile']
    assert m*live-mass==owners['deficit']==pin('global.deficit',m*live-mass)
    assert mass==sum(int(r)*count for r,count in profile.items())
    assert physical==live+helpers+centres+2
    assert live==owners['live'] and physical==owners['physical']
    assert live<=parent_live and physical<=parent_physical
    assert not template['bank_padding']['families']
    assert owners['explicit_idle_remainder_children']<=owners['source_idle_children_charged']
    # The old dedicated-bank geometry is only a conservative reserve envelope.
    # Its singular program is never used as evidence for a mixed invocation.
    rebased=parent_pervertex+65*(physical-parent_physical)+(live-parent_live)
    used=max(rebased,parent_pervertex); retained=None; payload=512
    if retained_invoice is not None:
        previous=read(retained_invoice)
        assert previous['compiler']==compiler and previous['charged_prefix_bits']==payload
        previous_bound=previous['conservative_pervertex_used']
        used=max(used,previous_bound+parent_pervertex)
        retained=dict(sha256=filehash(retained_invoice),previous_pervertex_allowance=previous_bound,
            added_complete_new_pervertex=parent_pervertex,policy='Retain old allowance and add entire fresh mixed recount.')
    half=m//2; group=2**(half*half)
    for i in range(1,half+1): group*=2**(2*i)-1
    stock,streamed_mass=group*physical,group*mass
    logical=group*used+64; router=compiler*(logical+1)*(stock+1)**2
    g_bound,e_bound,c0=2**30000,2**100000,2**210000
    total_mass=streamed_mass+e_bound
    literal=2*g_bound*stock**2+8*streamed_mass+4*stock+4+32*m
    row=2*stock.bit_length()+9909+252+2*payload
    maxchild=max(map(int,profile))
    inequalities=dict(local_primitive_bound=primitive_bound<2**48,
        logical=logical<2**6050,router=router<g_bound,literal=literal<e_bound,
        mass=total_mass<2**100001,precision=32*m*total_mass*total_mass<c0,
        tape=2*total_mass+18<c0,row=row<20161,halving=m*m>2*maxchild*maxchild)
    assert all(inequalities.values())
    localbits=max(r['prefix_bits'] for p in providers.values() for r in p['local'].values())
    input_l2_bits=(m+1)//2
    required_prefix=localbits+input_l2_bits+call_count+bridge_sweeps+4
    assert required_prefix<payload
    receipt=dict(status='PASS_INDEPENDENT_MIXED_ASYNC_SCALAR_PREFIX_AND_FINITE_INVOICE',
        template_sha256=template_hash,parent_template_sha256=contenthash(local_dir/'GLOBAL-TEMPLATE.json.gz'),
        owner_audit_sha256=filehash(audit/'OWNERS-AND-PROFILE.json'),
        controller_audit_sha256=filehash(audit/'ASYNC-AUDIT.json'),
        providers=providers,provider_phase_semantic_sha256={pid:p['semantic_artifact_sha256']['CLIFFORD-REVIEW.json']for pid,p in providers.items()},provider_counts=dict(provider_counts),selected_calls=selected,
        selected_local_paid_profile=dict(sorted(selected_paid.items())),
        selected_real_component_primitives=scalar,selected_coefficient_work_primitive_count=coefficient_work,
        selected_scalar_macros=macros,global_prefix_bits=required_prefix,charged_prefix_bits=payload,
        complete_invocation_sweeps=call_count,bridge_sweeps=bridge_sweeps,row_prefix_extra=2*payload,
        helpers=helpers,centres=centres,live=live,physical=physical,
        physical_stock_identity=dict(data_and_owner_families=live,local_helpers=helpers,
                                     private_centres=centres,coefficient_work=2),
        local_adapters=adapters,local_primitive_bound=primitive_bound,
        wrapper_elementary_factors_charged=wrapper_factors,factors_per_wrapper=factors_per_wrapper,
        compiler=compiler,unhosted_pervertex=parent_pervertex,hosted_rebased_pervertex=rebased,
        conservative_pervertex_used=used,retained_prior_overcharge=retained,
        finite=dict(physical_stock_bits=stock.bit_length(),router_bits=router.bit_length(),
                    literal_bits=literal.bit_length(),physical_row_coefficient=row,
                    retained_row_coefficient=20161,required_C0_bits=(32*m*total_mass*total_mass).bit_length(),
                    halving_integer_inequality=[m*m,2*maxchild*maxchild],G_exponent=30000,
                    E_exponent=100000,C0_exponent=210000),strict_checks=inequalities,
        scope='Actual call-specific mixed scalar, Horner, wrappers and paid children recounted. All three providers use fresh hash-bound independent all-column/frame/phase/normalization admission. Shared compiler uses conservative maxima; parent is geometry/overcharge only. All-size compiler, hosting, precision/tape and analytic transfer remain conditional.')
    prefix=dict(status='PASS_MIXED_ASYNC_GLOBAL_PREFIX',template_sha256=template_hash,
        global_prefix_bits=required_prefix,retained_payload_bits=payload,
        complete_invocation_cover_sweeps=call_count,bridge_factor_two_sweeps=bridge_sweeps,
        local_scalar_coefficient_work_prefix_bits=localbits,stream_input_sup_to_l2_bits=input_l2_bits,
        primitive_arithmetic_margin_bits=4,controller_audit_sha256=filehash(audit/'ASYNC-AUDIT.json'),
        proof='Each selected normalized provider restores all arbitrary dirty helper columns and gives the same data shear endpoints. Actual whole-owner charts are right-translation bijections. Sum all invocation and bridge sweeps and take maximum local scalar/Horner prefix over all providers and orientations. Idle children, phases, spectator endpoints and terminal translations are unitary. Retained all-size interfaces are conditional.')
    out.mkdir(parents=True,exist_ok=True)
    (out/'PREFIX-AND-INVOICE.json').write_text(json.dumps(receipt,indent=2)+'\n')
    (out/'GLOBAL-PREFIX.json').write_text(json.dumps(prefix,indent=2)+'\n')
    print(json.dumps({k:receipt[k] for k in ['status','provider_counts','selected_real_component_primitives',
          'selected_coefficient_work_primitive_count','global_prefix_bits','finite','strict_checks']},indent=2))
    return receipt

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('base','hosted','audit','out'):parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--retained-invoice',type=Path)
    args=parser.parse_args()
    run(args.base,args.hosted,args.audit,args.out,args.retained_invoice)
