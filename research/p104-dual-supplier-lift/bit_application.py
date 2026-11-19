"""Replay the changed ordinary BIT supplier and its two finite backends. Apache-2.0."""
import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
from pathlib import Path

from bit_native import build, digest, need, read_pinned

PAIRED = Path('research/paired-query-only-bit')
CALLER_SHA = '757b3523798f840bdb02028b23708c3416627a99ea09e7a3c4bcdc5cd0c7ce4b'
TRIAL = Q('.00385896180')
GAP = Q(1,10**10)
STEPS = (Q('.0038589356'), Q('.00385896149'))


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def reverse(word):
    n = word['public']
    adj = [1 << r for r in range(n)] + [0]*word['owned_fields']
    for op, r, *args in reversed(word['program']):
        if op == 'ADD':
            adj[args[0]] ^= adj[r]
        elif op == 'SWAP':
            s, = args
            adj[r], adj[s] = adj[s], adj[r]
        elif op in ('INIT','CLEAR'):
            adj[r] = 0
        else:
            need(op == 'MOVE', 'known binary tape instruction')
    need(adj[:n] == [(1 << r) ^ ((1 << (r+111)) if r < 111 else 0) for r in range(n)],
         'independent emitted-word full transpose')


def frames_and_sites(word, caller, native, audit):
    routes = []
    factors = set()
    for fid, frame in word['frames'].items():
        b, a, d = frame['B'], frame['A'], frame['dim']
        need((len(b),len(a)) == (d,8-d) and all(len(v)==8 for v in b+a), 'rational frame sizes')
        need(all(sum(Q(x)*Q(y) for x,y in zip(u,v)) == 0 for u in b for v in a), 'rational annihilator')
        inv, det = audit.matrix_inverse(list(zip(*(b+a))))
        routes.append([int(fid),str(det)])
        factors.update([abs(det.numerator), det.denominator])
        factors.update(Q(x).denominator for row in b+a+inv for x in row)
    for chart in native['charts']:
        det = Q(chart['determinant'])
        factors.update([abs(det.numerator),det.denominator])
        factors.update(Q(x).denominator for row in chart['inverse'] for x in row)
    position = sha256()
    def record(row):
        position.update(json.dumps(row,separators=(',',':')).encode())
        position.update(b'\n')
    word_moves = [(j,e[1],e[2],e[3]) for j,e in enumerate(word['program']) if e[0] == 'MOVE']
    ranks = {int(k):v['dim'] for k,v in word['frames'].items()}
    paid, targets, stages = Counter(), Counter(), []
    n, roles, ports = word['public'], caller['roles'], caller['ports']
    produced = {('root',p,i) for p in range(ports) for i in range(roles)}
    for j,(op,*args) in enumerate(caller['events']):
        if op == 'LOCAL':
            stage, x, y = args
            stages.append(stage)
            owners = [('root',p,x) for p in range(ports)] + [('root',p,y) for p in range(ports)]
            for r in range(2*ports,n):
                key = ('helper',j,r)
                need(key not in produced, 'fresh independent binary helper')
                owners.append(key)
                produced.add(key)
                grade = ranks[word['final'][r]]-ranks[word['start'][r]]
                need(grade > 0, 'productive binary helper')
                targets[grade] += 1
            need(len(owners) == len(set(owners)) == n, 'distinct public owners in the native occurrence')
            for clock,r,a,b in word_moves:
                need(n <= r < n+word['owned_fields'], 'owned paid sender')
                grade = abs(ranks[a]-ranks[b]); paid[grade] += 1
                record([j,clock,'owned',r-n,grade,a,b])
        elif op in ('QUERY','IDLE_ONE'):
            if op == 'QUERY':
                need(args[0] != args[1], 'binary query roles'); grade = 1
            else:
                mask = args[1]
                need(mask and len(mask)==len(set(mask)) and all(1<=s<=18 for s in mask), 'complete idle block')
                grade = 7*len(mask)
            for p in range(ports):
                paid[grade] += 1
                record([j,p,op,*args,grade])
    for endpoint in caller['diagonal']:
        ss = endpoint['stages']
        need(endpoint['q']==1 and ss and len(ss)==len(set(ss)), 'positive signed whole root')
        targets[1+7*len(ss)] += ports
    need(stages == [s for s in range(1,19) for _ in range(2)] and sum(targets.values()) == len(produced),
         '36 binary calls and all distinct targets')
    receipt = dict(ambient=134,rational_frames=len(routes), rational_main_charts=len(native['charts']),
                   rational_frame_sha256=digest(sorted(routes)), raw_prime_exclusions=sorted(factors),
                   native_calls=len(stages), fresh_helpers=len(stages)*(n-2*ports),
                   native_private_banks=len(stages)*word['owned_fields'], serial_query_bank=1,
                   productive_fields=len(produced), paid_calls=sum(paid.values()),
                   paid_position_sha256=position.hexdigest(), rank_surplus=sum(k*v for k,v in targets.items())-
                   sum(k*v for k,v in paid.items()))
    return targets, paid, receipt


def ordinary(word, caller, targets, paid):
    uses = Counter(e[0] for e in caller['events'])
    n, m, count, h = caller['ports'], caller['roles'], uses['LOCAL'], 134
    # Sixteen sweeps can copy two full operands via serial scratch and restore the heads.
    # Each sweep charges every public and owned bank and four scratch banks.
    native_arrays = word['public']+word['owned_fields']+4
    native_transits = 16*native_arrays*len(word['program'])
    caller_transits = n*8*(uses['ADD']+3*uses['SWAP']) + 256*n*(count+uses['QUERY']+m)
    routes = 4*(sum(targets.values())+sum(paid.values())) + 8*n*(count+uses['IDLE_ONE'])
    routed_transits = routes*8*(10*h*h+10*h)
    backing = count*(word['owned_fields']+4) + 2*n*m*len(caller['events']) + 16*n*(count+uses['QUERY']+m)
    total = count*native_transits+caller_transits+routed_transits
    need(total<10**12 and backing<10**7, 'complete raw binary work and backing allowances')
    return dict(native_banks_and_scratch=native_arrays, native_bank_transits_per_call=native_transits,
                caller_bank_transits=caller_transits, route_groups=routes, route_records=routed_transits,
                ordinary_records=total, owned_backing=backing, raw_ordinary_allowance=10**12, raw_owned_allowance=10**7)


def compiler(root, targets, paid):
    package = root/PAIRED
    finite = load(package/'retained/inputs/credited_trim.py', 'bit_puncture_compiler')
    iv = load(package/'independent/interval_gate.py', 'bit_puncture_intervals')
    certificate = finite.certificate(targets,paid,TRIAL,768,15,16,Q(1,5),Q(1,5),label='new binary native')
    largest = certificate.pop('ambient')
    need(largest == '127^768', 'largest productive rank')
    certificate['largest_productive_rank'] = largest
    uniform = finite.uniform_certificate(TRIAL,768,15,16,134,GAP)
    need(uniform['N'] == '2^297130000000000' and uniform['logarithm_power']==618, 'actual binary ambient threshold')
    def margin(k):
        return iv.sub(iv.moment(targets,k), iv.moment(paid,k))
    lo, hi = Q('.00385896184247'), Q('.00385896184248')
    need(margin(lo)[0] > 0 > margin(hi)[1] and margin(TRIAL)[0] > 0, 'independent complete binary raw crossing')
    def positive(x):
        return iv.div(iv.exact(1), iv.expminus(x))
    def moment(hist,offset):
        total = (0,0)
        for r,z in hist.items():
            x = iv.smul(iv.log(r),abs(offset))
            scale = positive(x) if offset>0 else iv.expminus(x)
            total = iv.add(total,iv.smul(iv.mul(iv.power(r,TRIAL), scale),z))
        return total
    u = Q(1,5)
    tt = iv.moment(targets,TRIAL)
    ratios = [iv.div(iv.moment(paid,TRIAL),tt),
              iv.div(moment(paid,u),iv.mul(positive(iv.smul(iv.log(15),u)),tt)),
              iv.div(iv.mul(positive(iv.smul(iv.log(16),u)),moment(targets,-u)),tt)]
    bounds = [Q(s) for s in certificate['rational_upper_limits']]
    need(all(0 < a <= b <= bound*iv.B < iv.B for (a,b),bound in zip(ratios,bounds)),
         'independent three tail comparisons')
    aa, gg, ll = bounds
    need(1/(1+768*(1-aa))+2*gg**768+ll**768 < 1, 'paid splits and lost productive targets')
    theta = Q(42,43); p=uniform['logarithm_power']; H=uniform['H']
    factor = iv.exact(1)
    power = positive(iv.smul(iv.log(134),TRIAL))
    exponent = 768
    while exponent:
        if exponent & 1:
            factor = iv.mul(factor,power)
        exponent //= 2
        if exponent:
            power = iv.mul(power,power)
    eta = iv.div(iv.exact(1-TRIAL),factor)
    need(2*15**(768*43) <= 134**(768*42) and theta**p < Q(eta[0],iv.B) and Q(factor[1],iv.B)<2**p,
         'shifted and ambient logarithm inequalities')
    need((H+1)**p < 2**(H//GAP.denominator) and (H-GAP.denominator+1)**p >= 2**(H//GAP.denominator-1),
         'uniform threshold and preceding point')
    selected=(root/'certificates/frontier7000/CLAIM.json').read_bytes()
    need(sha256(selected).hexdigest()=='3f8add8252adb223b60418ec69351a69b6b5edfe601ec1c6b4b65cd9e2afd9b2',
         'selected completed BIT backend')
    previous=Q(json.loads(selected)['admitted_BIT_saving']); need(previous==Q('.00385248'),'source-bound start')
    covered=TRIAL-2*GAP; rho=Q(1,250); bootstrap=[]
    for admitted in STEPS:
        envelope=(1-rho)*covered+rho*previous
        need(previous<admitted<envelope<rho<1-envelope, 'complete ordinary envelope and stock')
        bootstrap.append(dict(previous=str(previous),envelope=str(envelope),admitted=str(admitted),slack=str(envelope-admitted)))
        previous=admitted
    return dict(raw_bracket=['0.00385896184247','0.00385896184248'],raw_trial=str(TRIAL),
                trial_margin=iv.show(margin(TRIAL)), finite_separation=certificate, working_ambient='134^768',
                uniform=uniform,covered=str(covered),ordinary_bootstrap=bootstrap,ordinary_admitted=str(previous))


def verify(root):
    package = root/PAIRED
    word, edits = build(root)
    reverse(word)
    audit = load(package/'retained/audit_binary_mixed.py', 'bit_puncture_transfer')
    paired = load(package/'check.py','bit_puncture_caller')
    p0,t0,native = audit.source_audit(word)
    caller = read_pinned(root,PAIRED/'EFREE-CALLER.json.gz',CALLER_SHA)
    need(paired.forward(caller) == audit.backward(caller) == 38**2, 'both exact complete binary caller transfers')
    targets, paid, contacts = frames_and_sites(word,caller,native,audit)
    baseline = json.loads((package/'EFREE-RESULT.json').read_bytes())
    p_old=Counter({int(k):v for k,v in baseline['paid'].items()});t_old=Counter({int(k):v for k,v in baseline['targets'].items()})
    p_old[1]-=288;p_old[3]-=288;t_old[4]-=288
    need(p_old==paid and t_old==targets and contacts['rank_surplus']==1506, 'all eight surrendered target and paid prices')
    return dict(native=edits, native_paid=dict(p0), native_targets=dict(t0), public=native['public'],
                owned_labels=native['owned_labels'], owned_lifetimes=native['owned_lifetimes'],
                nonzero_owned_erasures=native['nonzero_owned_erasures'], caller_coefficients_each_way=38**2,
                signed_positions=contacts, paid=dict(paid),targets=dict(targets),ordinary=ordinary(word,caller,targets,paid),
                compiler=compiler(root,targets,paid))


if __name__ == '__main__':
    args=argparse.ArgumentParser(description=__doc__)
    args.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2]);args.add_argument('--write-json',type=Path)
    args.add_argument('--emit-word',type=Path,help='write the complete finite native word as JSON')
    options=args.parse_args(); result=verify(options.root)
    if options.emit_word:
        options.emit_word.write_text(json.dumps(build(options.root)[0],separators=(',',':'))+'\n')
    if options.write_json:
        options.write_json.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS_CHANGED_ORDINARY_BIT',result['public'],result['native']['paid_packets'],result['compiler']['ordinary_admitted'])
