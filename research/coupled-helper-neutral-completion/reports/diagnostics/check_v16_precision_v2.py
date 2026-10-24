#!/usr/bin/env python3
"""Frozen v16c neutral completion: fresh data-only precision/ordinary closure.

Root alone executes. No author evaluator or earlier scientific suite runs.
The full source/native/phase and new649-column endpoint gates remain separate.
Apache-2.0, Chris R/Clear1nsight; substantial OpenAI Codex assistance.
"""
import argparse,copy,gzip,importlib.util,json,resource,time
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
HERE=Path(__file__).resolve().parent


def need(ok,s):
    if not ok:raise ValueError(s)


def multiple(h,a,n):
    b=h.Inventory();b.ops=Counter({k:v*n for k,v in a.ops.items()})
    b.primitives=Counter({k:v*n for k,v in a.primitives.items()})
    b.coefficients=Counter({k:v*n for k,v in a.coefficients.items()})
    for key in ('Lmax','Ljoint','height','tariff'):setattr(b,key,getattr(a,key)*n)
    return b


def local(h,d,p,aliases):
    inv=h.Inventory();ops=d['operations']
    positions=[i for i,e in enumerate(ops) if e['op']=='PROVIDER_5402']
    need(len(positions)==1,'one forward5402 provider');pos=positions[0]
    block=ops[pos-400:pos]+ops[pos+1:pos+401]
    need(len(block)==800 and all(e['op']=='MONOMIAL' for e in block),'actual800aliases included once')
    expected={}
    for g in aliases['groups']:
        for owner in g['owners']:
            expected['owner'+str(owner)]=(g['forward_pre_input_monomial_word'],g['forward_post_output_monomial_word'])
    need(len(expected)==400,'all400 alias owners')
    for side,es in enumerate((block[:400],block[400:])):
        need({e['field'] for e in es}==set(expected),'each400 actual helper owners exactly once')
        for e in es:need(e['word']==expected[e['field']][side],'literal forward positive alias binding')
    alias_counts=Counter()
    for e in block:alias_counts.update(h.mono(e['word']))
    binding=d['physical_field_bindings']
    need(len(binding)==649 and len(set(binding.values()))==649 and set(binding.values())==set(range(649)),
         'all632original+17arbitraryowned separate physical IDs')
    need(d['arbitrary_original_columns']==632 and d['arbitrary_owned_columns']==d['all_owned_zero_returns']==17,
         'frozen649column type')
    need(d['helper_jobs']=={'4':28,'7':7,'8':55,'9':318},'408helper jobs, including8new canonicalH8')
    need(d['complete_paid_local_profile']=={'1':2193,'2':412,'3':510,'4':127,'5':40,'8':8},'actual local paid profile')
    for i,e in enumerate(ops):
        op=e['op']
        if op=='PROVIDER_5402':
            need(e['owned_fields']==[f'c{k}' for k in range(9)],'source nine-owned ABI')
            need(e['source_head']=='3348fccea855082786d5f0fc5558b73d4974e745','exact forward provider head')
            continue
        if op in ('ADD','SCALE'):inv.add(op,e['coefficient'])
        elif op=='MONOMIAL':inv.add(op,word=e['word'])
        elif op=='CLEAR':need(e.get('owned') is True and e['field'] in {f't{k}' for k in range(8)},'only addedT-owned clears');inv.add(op)
        elif op=='ZERO_RETAG':
            need(i>0 and ops[i-1]['op']=='CLEAR' and ops[i-1]['field']==e['field'] and e['new_chart']=='ground','zero retag after actual owned CLEAR')
            inv.add(op)
        elif op=='SWAP':need(e['includes_chart'] is True,'SWAP carries full field/chart');inv.add(op)
        elif op=='GAUSSIAN':
            need(e['paid'] is True and e['rank']==8 and e['operator']=='C_rank8_bits0to7_positive','actual positive C8')
            need(e['actual_axes']==list(range(8)),'explicit paid C8 axes')
            need(ops[i-1]['op']==ops[i+1]['op']=='MONOMIAL' and
                 ops[i-1]['field']==ops[i+1]['field']==e['field'] and
                 ops[i-1]['word']==ops[i+1]['word']==[['P',[256,2,4,8,16,32,64,128,1]]],
                 'paidD8 realized by two full axis0/8 swaps')
            inv.add(op)
        else:raise ValueError('unsupported neutral literal '+op)
        for key in ('field','dst','src'):
            if key in e:need(e[key] in binding,'actual named physical field')
        if op in ('ADD','SCALE'):
            need(e.get('dst',e.get('field')) != e.get('src'), 'ADD has distinct physical owners')
    need(inv.ops['COPY']==0,'neutral extension uses SWAP, not hidden COPY')
    return inv,dict(alias_counts)


def controller(h,ctl):
    """Explicit retained full-bank program and query stream realization."""
    inv=h.Inventory();counter=Counter();query_slots=[];paid=Counter();main=Counter()
    width=112
    def scalar_record(e):
        op=e[0]
        for _ in range(width):
            if op=='ADD':inv.add('ADD',e[3])
            elif op=='SCALE':inv.add('SCALE',e[2])
            else:need(op=='SWAP','bank boundary alphabet');inv.add('SWAP')
    for e in ctl['boundaries']['right_program']:scalar_record(e)
    for idx,e in enumerate(ctl['physical_events']):
        op=e[0];counter[op]+=1
        if op=='LOCAL':need(e[3] is True,'all18 backends are neutralB');continue
        if op=='ADD':scalar_record(e)
        elif op=='SIGNED_SWAP':
            for _ in range(width):
                inv.add('ADD',1);inv.add('ADD',-1);inv.add('ADD',1)
        elif op=='Q_POWER':
            need(e[2] in (2,-2),'explicit even-Q native translation')
            for _ in range(width):inv.add('MONOMIAL',word=[['X',1]])
        elif op=='QUERY_SHEAR':
            # One private complete slot per port per physical occurrence,
            # cleared on arbitrary entry, copied, child-completed, added, cleared.
            for j in range(width):
                query_slots.append(f'query{idx}:port{j}:Z')
                inv.add('CLEAR');inv.add('COPY');inv.add('GAUSSIAN');paid[1]+=1
                if e[3] is False:inv.add('MONOMIAL',word=[['X',1]])
                inv.add('ADD',-1 if e[3] else 1);inv.add('CLEAR')
        elif op=='IDLE':
            rank=8*len(e[2]);need(rank>0,'positive whole-IDLE job')
            for _ in range(2*width):inv.add('GAUSSIAN');paid[rank]+=1
        else:raise ValueError('unsupported direct controller '+op)
    for e in ctl['boundaries']['left_program']:scalar_record(e)
    for row in ctl['diagonal']:
        rank=1+8*sum(row[1:]);need(rank>0 and row[0] in (-1,1),'source positive main diagonal')
        main[rank]+=width
        if row[0]==-1:
            for _ in range(width):inv.add('SCALE',-1)
    need(counter['LOCAL']==18 and counter['QUERY_SHEAR']==15 and counter['IDLE']==15 and
         counter['SIGNED_SWAP']==20 and counter['Q_POWER']==4,'complete direct caller retained controls')
    need(len(query_slots)==len(set(query_slots))==1680,'explicit private query slots')
    need(sum(main.values())==3584 and ctl['ambient_rank']==145,'actual unchanged main geometry')
    return inv,dict(counter),paid,main,query_slots


def main():
    start=time.monotonic();resource.setrlimit(resource.RLIMIT_CPU,(15,15))
    resource.setrlimit(resource.RLIMIT_AS,(256*1024**2,256*1024**2))
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=HERE.parents[2]);ap.add_argument('--output',type=Path,default=HERE/'V16-PRECISION-v2.json');a=ap.parse_args()
    manifest_path=HERE/'V16-SOURCES-v2.json';manifest=json.loads(manifest_path.read_bytes());data={}
    for r in manifest['rows']:
        raw=(a.root/r['path']).read_bytes();need(sha256(raw).hexdigest()==r['sha256'],'changed frozen input '+r['path'])
        if r['id']!='helper':data[r['id']]=json.loads(gzip.decompress(raw) if r['path'].endswith('.gz') else raw)
    spec=importlib.util.spec_from_file_location('frozen_own_v14_inventory_helpers',HERE/'check_v14_instruction_envelopes.py')
    h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
    p,n,w=data['provider'],data['normalizers'],data['word']['word']
    for label in ('B','F'):
        macro=next(e for e in data[label]['operations'] if e['op']=='PROVIDER_5402')
        need(macro['provider_sha256']==next(r['sha256'] for r in manifest['rows'] if r['id']=='provider'),
             'exact source provider bytes in local packet')
    need(data['alias_acceptance']['aliases_sha256']==data['B']['aliases_sha256']==data['F']['aliases_sha256'],
         'same root-executed400alias proof bytes')
    need(sha256((a.root/manifest['by_id']['aliases']).read_bytes()).hexdigest()==data['alias_acceptance']['aliases_sha256'],'actual accepted alias file')
    need(data['implementation']['execution_order']==['right_program','physical_events','left_program','main_normalizers'], 'actual source R-to-W-to-L execution')
    source,stages=h.forward_provider(p,n,w)
    b,alias_b=local(h,data['B'],p,data['aliases']);f,alias_f=local(h,data['F'],p,data['aliases'])
    B=h.combine(source,b);F=h.combine(source,f)
    ctl,ctlcounts,otherpaid,main,queryslots=controller(h,data['controller'])
    total=h.combine(multiple(h,B,18),ctl)
    paid=Counter({int(k):v*18 for k,v in data['B']['complete_paid_local_profile'].items()});paid.update(otherpaid)
    targets=Counter({int(k):v*18 for k,v in data['B']['helper_jobs'].items()});targets.update(main)
    need(sum(paid.values())==64260 and sum(targets.values())==10928,'complete actual mixed counts')
    owned=18*17+len(queryslots)
    # Physical class envelope: every actual rank<=145 fixed binary/phase map
    # uses <=64*(145+1)^3 primitive schemas including forward/inverse routes.
    # The cube over incidences pays explicit role permutations and descriptors,
    # all owned scans/parking and actual source/target normalizers; it is an
    # overestimate, separate from the exact scalar/literal primitive census.
    records=sum(total.ops.values());incidences=records+owned+sum(paid.values())+sum(targets.values())+1
    physical_raw_upper=64*(145+1)**3*incidences**3+total.tariff
    Graw=total.tariff+8*physical_raw_upper
    need(max(physical_raw_upper,Graw,owned,total.height,sum(paid.values()),sum(targets.values()))<2**128,
         'fresh finite raw VALUE bound A0=2^128')
    q=1024;ambient_log=8192
    strictified_log=2*(q*(2+2*128)+10+2*ambient_log)+6+3*(ambient_log+1)
    need(strictified_log<1048576,'fresh strictified D0=2^1048576')
    fund=data['funding'];H=fund['H'];j=fund['j'];gap=Q(fund['gap'])
    need(fund['status']=='PASS_CONDITIONAL_COMPLETE_PROFILE_ENDPOINT_ARITHMETIC_ONLY','root funded numerical scope')
    need(gap==(Q(fund['tested'])-Q(fund['kappa']))/7==Q(1,700000000000),'actual strict compiler gap')
    need(H==j*gap.denominator and (H+1)**1000<2**j,'actual funded carrier rank')
    need({int(k):v for k,v in fund['paid'].items()}==dict(paid) and {int(k):v for k,v in fund['targets'].items()}==dict(targets),'fresh raw profile equals root numerical instance')
    local_accept=data['local_acceptance']
    need(local_accept['status']=='PASS_COMPLETE_LOCAL_STANDARD_B_AND_F_WITH408POSITIVE_HELPERS','executed649column source endpoint')
    for key,label in [('backward','B'),('forward','F')]:
        need(local_accept['packet_sha256'][key]==next(r['sha256'] for r in manifest['rows'] if r['id']==label),'same frozen649-column packets')
    out=dict(status='PASS_SCOPED_V16C_PRECISION_STOCK_AND_FRESH_RAW_MAJORANTS',
        execution_order=['right_program','physical_events','left_program','main_normalizers'],
        v1_order_diagnostic='V16-CALLER-IMPLEMENTATION.json described boundaries in reverse order; v1 count/norm sums unchanged but ordered realization invalid. V2 binds corrected literal order.',
        carrier_H=H,carrier_j=j,carrier_gap=str(gap),
        source_forward_provider=source.record(),source_stages=stages,
        local_B=B.record(),local_F=F.record(),local_B_outside=b.record(),local_F_outside=f.record(),
        local_B_alias800_primitive_counts=alias_b,local_F_alias800_primitive_counts=alias_f,
        controller=ctl.record(),controller_bank_event_counts=ctlcounts,
        raw_global=total.record(),paid=dict(paid),targets=dict(targets),
        productive_fields=10928,paid_calls=64260,raw_LOCAL_private_fields=306,
        raw_query_private_fields=1680,raw_total_private_reservation=owned,
        private_policy='One tagged17bank allocation per rawLOCAL; one tagged queryZ per port/occurrence. Conservative disjoint reservation, not a claimed minimum. Parent banks remain parked through recursion.',
        raw_physical_value_upper=physical_raw_upper,raw_G_upper=Graw,
        raw_majorant_formula='64*(145+1)^3*(sourcefieldrecords+O+paid+productive+1)^3+exactscalarTariff',
        exact_scalar_tariff_is_not_TM_steps=True,
        expanded=dict(A0='2^128',strictified_log_upper=strictified_log,D0='2^1048576',
            recursion='F16(0)=D0; X_n=(n+1)*(D0+1)*(F16(n-1)+1); F16(n)=X_n^(16*(n+1)^2)',
            N='2^'+str(H),M='F16(2^'+str(H)+')',
            actual_counts_bound='W,P,U,O,R,G <= M',
            precision='Zbar=2M; Ebar=64*(4M+N+1)^3; Bbar=M+Ebar; C0bar=32*N*Bbar^2; C1=1',
            stock='[W*(O+1)]^Dord(d) times BIT stock and each additional independent live stock',
            no_old_raw_or_expanded_caps_reused=True),
        interval_scope='At fixed width, scalar field instructions and audited square native/monomial macros. Exact source COPY has maxnorm1/jointnorm<=2. FieldSWAP endpoint norm1 is separate from explicit26unit3ADD+sign microcode. Same-chart compatibility and exactzero retag at needed swap locations are retained physical-binding obligations.',
        residual='For either declared geometry and its L: ||e_out||<=2^L*(||e_in||+sum ||r_j||). Machine/site coordinate conversion remains explicit; no tape-step count is inferred from fieldsite count.',
        alias_productive_normalizers='All800sourcehelperaliases+16restoredhcanonicalmatchers+16paidD8routes are already inside1072Bmaps. No second16productive normalizer dispatcher bill is added.',
        full_compiler_outer_numeric_replayed=False,complete_admission=False,new_kappa=None,
        remaining=['written V16-APPLICATION-PROOF-v2 source specialization and aggregate independent review','retained selected native/movement/analytic hypotheses remain conditional premises'],
        seconds=time.monotonic()-start,checker_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        input_manifest_sha256=sha256(manifest_path.read_bytes()).hexdigest())
    # Actual parser controls do not invoke scientific semantics.
    controls=[]
    bad=copy.deepcopy(data['B']);i=next(i for i,e in enumerate(bad['operations']) if e['op']=='CLEAR');bad['operations'][i]['field']='h0'
    try:local(h,bad,p,data['aliases'])
    except ValueError:controls.append('borrowed h CLEAR rejected')
    else:raise ValueError('borrowed CLEAR accepted')
    need(total.Ljoint-total.Lmax==total.ops['COPY'],'all joint COPY factors charged')
    controls.append('joint COPY factor census')
    need(h.scalar_tariff('SWAP')==3*h.scalar_tariff('ADD',1)+h.scalar_tariff('SCALE',-1),'swap26unit exacttariff')
    controls.append('swap scalar microcode tariff26')
    out['controls']=controls
    need(not a.output.exists(),'new immutable output');a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(status=out['status'],local_scalar_B=B.tariff,local_scalar_F=F.tariff,
        local_field_L=[B.Lmax,B.Ljoint],global_scalar=total.tariff,
        global_field_L=[total.Lmax,total.Ljoint],global_micro_L=[total.Lmax+3*total.ops['SWAP'],total.Ljoint+3*total.ops['SWAP']],
        owned_reservation=owned,A0='2^128',D0='2^1048576',seconds=out['seconds'])))


if __name__=='__main__':main()
