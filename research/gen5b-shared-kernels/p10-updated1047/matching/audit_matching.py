"""Independently authored, read-only audit of finite matching witnesses.
No upstream or candidate-selector module is imported or run. Inputs are inert JSON.
Uses Python standard-library exact integer/rational algebra only.
"""
from pathlib import Path
from fractions import Fraction
from collections import Counter, defaultdict, deque
import json, gzip, hashlib, math, time, argparse
from decimal import Decimal, localcontext
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import support

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--experiment', type=Path, default=support.OUTPUT/'matching')
parser.add_argument('--graph-cache', type=Path, help='Optional prior graph/source folder for exact cross-checks')
parser.add_argument('--graph-only', action='store_true', help='Rebuild graph, write it to output, then stop before auditing witnesses')
parser.add_argument('--include-fixed', action='store_true', help='Also audit the separately restricted fixed-original-recipient witness')
parser.add_argument('--output', type=Path, default=support.OUTPUT/'matching')
args = parser.parse_args()
ROOT, OLD, OUT = args.experiment, args.graph_cache, args.output
OUT.mkdir(parents=True, exist_ok=True)
H = 20
START = time.time()

def need(ok, explanation):
    if not ok:
        raise ValueError(explanation)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load(path):
    return json.loads(path.read_text())

manifest = support.pins()
source_hashes = {}
for kind in ('word', 'frames'):
    rel = f'bitword/selected/bit/{kind}_p10.json.gz'
    rec = next(x for x in manifest['files'] if x['path'] == rel)
    raw = support.read_bytes(rel)
    sha = hashlib.sha256(raw).hexdigest()
    git = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    need(sha == rec['sha256'] and git == rec['git_blob'] and len(raw) == rec['bytes'], 'Source pin failed: ' + kind)
    parsed = json.loads(gzip.decompress(raw))
    if OLD is not None:
        need(parsed == load(OLD / (kind + '.json')), 'Cached-graph source differs: ' + kind)
    source_hashes[kind] = dict(sha256=sha, git_blob=git)
    if kind == 'word':
        word = parsed
    else:
        frames = parsed['frames']

cache = None
if OLD is not None:
    cache = {int(d): set(rs) for d, rs in load(OLD / 'postdescent_graph.json').items()}
    need(all(len(rs) == len(set(rs)) for rs in load(OLD / 'postdescent_graph.json').values()), 'Duplicate graph edges')
gauge = {z['role']: z for z in word['gauges']}
phase = word['phase1']
need(phase == sorted(set(phase)), 'Noncanonical phase ordering')
phase_set = set(phase)
order = phase + [i for i in range(len(word['ops'])) if i not in phase_set]
first, last, endframe = {}, {}, {}
for tick, opid in enumerate(order):
    for role in word['ops'][opid][:2]:
        first.setdefault(role, tick)
        last[role] = tick
        endframe[role] = word['op_frame'][opid]
roots = set(word['rootroles'])
sources = set(word['sources'].values())
donors = set(first) - set(gauge) - roots - sources
if cache is not None:
    need(set(cache) == donors, 'Donor universe differs')
rank = {d: frames[str(endframe[d])]['dim'] for d in donors}

def rref(rows):
    a = [list(map(Fraction, row)) for row in rows]
    need(all(len(row) == H for row in a), 'Bad frame row width')
    pivot_cols = []
    row = 0
    for col in range(H):
        pick = next((j for j in range(row, len(a)) if a[j][col]), None)
        if pick is None:
            continue
        a[row], a[pick] = a[pick], a[row]
        scale = a[row][col]
        a[row] = [x / scale for x in a[row]]
        for j in range(len(a)):
            if j != row and a[j][col]:
                scale = a[j][col]
                a[j] = [x - scale*y for x, y in zip(a[j], a[row])]
        pivot_cols.append(col)
        row += 1
    return a[:row], pivot_cols

memo_ann, memo_basis, signatures = {}, {}, {}

def kernel(rows):
    a, piv = rref(rows)
    result = []
    for free in sorted(set(range(H)) - set(piv)):
        v = [Fraction(0)] * H
        v[free] = 1
        for row, col in zip(a, piv):
            v[col] = -row[free]
        scale = math.lcm(*(x.denominator for x in v))
        result.append([int(x * scale) for x in v])
    return result

def ann(fid):
    if fid not in memo_ann:
        obj = frames[str(fid)]
        memo_ann[fid] = obj['a'] if 'a' in obj else kernel(obj['b'])
    return memo_ann[fid]

def basis(fid):
    if fid not in memo_basis:
        obj = frames[str(fid)]
        memo_basis[fid] = obj['b'] if 'b' in obj else kernel(obj['a'])
    return memo_basis[fid]

def signature(fid):
    if fid not in signatures:
        signatures[fid] = tuple(tuple(row) for row in rref(ann(fid))[0])
    return signatures[fid]

# Later equal-frame gauge tails are the bounded recipient screen inherited
# from the physical matching problem, not a claim to enumerate all possible reuse.
chains = defaultdict(list)
for z in word['gauges'][::-1]:
    for target in z['targets']:
        chains[target].append(z['role'])
recipients = []
for role, z in sorted(gauge.items()):
    if z['dim'] != 17:
        continue
    need(frames[str(z['frame'])]['dim'] == 17, 'Gauge dimension mismatch')
    eligible = True
    for target in z['targets']:
        chain = chains[target]
        need(chain.count(role) == 1, 'Repeated role in target gauge chain')
        for later in chain[chain.index(role) + 1:]:
            if signature(gauge[later]['frame']) != signature(z['frame']):
                eligible = False
                break
    if eligible:
        recipients.append(role)
need(len(recipients) == 960, 'Unexpected recipient universe')

# Nonzero modular determinant proves exact nondegeneracy. It also proves
# full row rank, so record row counts certify every used frame dimension.
prime = 65521

def det_mod(rows):
    a = [[x % prime for x in row] for row in rows]
    ans = 1
    for k in range(len(a)):
        pivot = next((i for i in range(k, len(a)) if a[i][k]), None)
        if pivot is None:
            return 0
        if pivot != k:
            a[k], a[pivot] = a[pivot], a[k]
            ans = -ans
        p = a[k][k]
        ans = ans * p % prime
        inv = pow(p, -1, prime)
        for i in range(k+1, len(a)):
            mult = a[i][k] * inv % prime
            for j in range(k+1, len(a)):
                a[i][j] = (a[i][j] - mult*a[k][j]) % prime
    return ans % prime

frame_ids = {endframe[d] for d in donors} | {gauge[r]['frame'] for r in recipients}
nd_witnesses = {}
for fid in sorted(frame_ids):
    obj = frames[str(fid)]
    rows = obj.get('a', obj.get('b'))
    dimension = obj['dim']
    need(len(rows) == (H - dimension if 'a' in obj else dimension), 'Frame row-count dimension mismatch')
    scale = 11 if 'a' in obj else 9
    gram = [[scale*sum(x*y for x,y in zip(a,b)) - sum(a)*sum(b) for b in rows] for a in rows]
    det = det_mod(gram)
    need(det != 0, 'Nondegeneracy not established for frame ' + str(fid))
    nd_witnesses[fid] = det

# Rebuild every edge with exact algebra. Equal 17-dimensional spaces are
# bucketed by canonical annihilator; lower ranks use sparse integer dot products.
by_frame = defaultdict(list)
for donor in sorted(donors):
    if rank[donor] <= 17:
        by_frame[endframe[donor]].append(donor)
recipient_annihilators = {r: ann(gauge[r]['frame']) for r in recipients}
recipient_signatures = defaultdict(list)
for r in recipients:
    recipient_signatures[signature(gauge[r]['frame'])].append(r)
rebuilt = {d: set() for d in donors}
exact_frame_pairs = 0
for fid, ds in sorted(by_frame.items()):
    if frames[str(fid)]['dim'] == 17:
        choices = recipient_signatures.get(signature(fid), [])
    else:
        B = basis(fid)
        need(len(B) == frames[str(fid)]['dim'], 'Donor basis dimension mismatch')
        sparse_basis = [[(i,x) for i,x in enumerate(row) if x] for row in B]
        choices = []
        for r in recipients:
            if all(sum(row[i]*x for i,x in vector) == 0
                   for vector in sparse_basis for row in recipient_annihilators[r]):
                choices.append(r)
    exact_frame_pairs += len(choices)
    for recipient in choices:
        for donor in ds:
            if last[donor] < first[recipient]:
                rebuilt[donor].add(recipient)
if cache is not None:
    need(rebuilt == cache, 'Exact graph reconstruction mismatch')
cache = rebuilt
# Preserve the original timeline donor order to retain the independently
# source-bound cached graph's byte identity, while sorting each neighbor list.
graph_raw = (json.dumps({str(d): sorted(cache[d]) for d in first if d in donors})+'\n').encode()
graph_sha256 = hashlib.sha256(graph_raw).hexdigest()
need(graph_sha256 == 'e111c86a5230b59ab169468779b6832d2ef95a15bf9e4ceea534f6b1194a3685', 'Reconstructed graph pin mismatch')
(OUT/'postdescent_graph.json').write_bytes(graph_raw)
print('Rebuilt exact graph:', len(donors), len(recipients), sum(map(len, cache.values())), 'edges', flush=True)
if args.graph_only:
    print(json.dumps(dict(status='PASS_EXACT_GRAPH_RECONSTRUCTION',graph_sha256=graph_sha256,edges=sum(map(len,cache.values())),elapsed_seconds=time.time()-START)))
    raise SystemExit(0)

# BFS alternating-path matching, deliberately distinct from selector DFS.
# A vertex cover of equal size is independently checked for each rank prefix.
def maximum_with_cover(graph):
    match_d, match_r = {}, {}
    for start in sorted(graph):
        q = deque([start])
        seen_d, predecessor_r = {start}, {}
        finish = None
        while q and finish is None:
            d = q.popleft()
            for r in sorted(graph[d]):
                if r in predecessor_r or match_d.get(d) == r:
                    continue
                predecessor_r[r] = d
                if r not in match_r:
                    finish = r
                    break
                nxt = match_r[r]
                if nxt not in seen_d:
                    seen_d.add(nxt)
                    q.append(nxt)
        if finish is not None:
            r = finish
            while True:
                d = predecessor_r[r]
                prior = match_d.get(d)
                match_d[d], match_r[r] = r, d
                if prior is None:
                    break
                r = prior
    reach_d = set(graph) - set(match_d)
    reach_r = set()
    q = deque(reach_d)
    while q:
        d = q.popleft()
        for r in graph[d]:
            if match_d.get(d) == r or r in reach_r:
                continue
            reach_r.add(r)
            if r in match_r and match_r[r] not in reach_d:
                reach_d.add(match_r[r])
                q.append(match_r[r])
    cover_d, cover_r = set(graph) - reach_d, reach_r
    need(all(d in cover_d or r in cover_r for d,rs in graph.items() for r in rs), 'Invalid cover')
    need(len(cover_d) + len(cover_r) == len(match_d), 'Matching/cover gap')
    need(len(set(match_d.values())) == len(match_d), 'Matching repeat')
    return match_d, {'donors': sorted(cover_d), 'recipients': sorted(cover_r)}

old = dict(word['pairs'])
need(len(old) == len(word['pairs']) == len(set(old.values())) == 890, 'Invalid original matching')
phi = lambda x: x*math.log(100/x) if x else 0.0
benefit = lambda r: phi(20-r) - phi(17-r)
old_score = sum(benefit(rank[d]) for d in old)
def verify_network(arcs, potentials, source, target, desired_flow):
    balance = [0]*len(potentials)
    reduced_costs = []
    cost = 0
    for a,b,cap,c,f in arcs:
        need(0 <= f <= cap, 'Capacity violation')
        balance[a] -= f
        balance[b] += f
        cost += f*c
        if f < cap:
            reduced_costs.append(c+potentials[a]-potentials[b])
        if f:
            reduced_costs.append(-c+potentials[b]-potentials[a])
    need(balance[source] == -desired_flow and balance[target] == desired_flow and all(x == 0 for i,x in enumerate(balance) if i not in (source,target)), 'Flow conservation failed')
    need(min(reduced_costs) >= 0, 'Negative residual reduced-cost arc')
    return cost, reduced_costs

def verify_pairs(pairs, graph, cardinality):
    picked = dict(pairs)
    need(len(pairs) == len(picked) == len(set(picked.values())) == cardinality, 'Invalid candidate cardinality')
    need(all(d in graph and r in graph[d] for d,r in pairs), 'Ineligible candidate pair')
    return picked

results, covers = {}, {}
variants = [('unrestricted', '', 'matching-optimality-certificate.json', 'matching-result.json')]
if args.include_fixed:
    variants.append(('fixed_original_recipients', '_fixedrecipients', 'matching-fixedrecipients-optimality-certificate.json', 'matching-fixedrecipients-result.json'))
for name, suffix, certname, reportname in variants:
    graph = {d: rs if not suffix else rs & set(old.values()) for d,rs in cache.items()}
    report = load(ROOT / reportname)
    certificate = load(ROOT / certname)
    candidate_path = ROOT / ('word_weighted890' + suffix + '.json')
    candidate = load(candidate_path)
    pairs = candidate['pairs']
    picked = verify_pairs(pairs, graph, 890)
    need(pairs == certificate['pairs'], 'Certificate/candidate pair disagreement')
    need(digest(candidate_path) == report['candidate_sha256'], 'Candidate hash mismatch')
    need(graph_sha256 == report['graph_sha256'], 'Graph hash mismatch')
    need(report['head'] == manifest['head'], 'Head mismatch')
    need(sum(map(len, graph.values())) == report['graph_edges'], 'Reported edge count mismatch')
    need(set(candidate) == set(word) and all(candidate[k] == word[k] for k in word if k not in ('pairs','reads')), 'Unrelated candidate change')
    need(all(candidate['reads'].get(k) == v for k,v in word['reads'].items()), 'Existing read modified')
    need(all(candidate['reads'][str(r)] == first[r] and last[d] < first[r] for d,r in pairs), 'Selected edge lifetime/read failed')
    quotas = Counter(rank[d] for d in picked)
    need(dict(quotas) == {int(k): v for k,v in certificate['rank_quotas'].items()}, 'Certificate quota mismatch')
    need(dict(quotas) == {int(k): v for k,v in report['donor_rank_histogram'].items()}, 'Reported rank histogram mismatch')
    prefix_rows = []
    prefix_covers = {}
    for threshold in sorted(set(rank.values()), reverse=True):
        sub = {d: rs for d,rs in graph.items() if rank[d] >= threshold}
        matching, cover = maximum_with_cover(sub)
        cap = len(matching)
        achieved = sum(count for r,count in quotas.items() if r >= threshold)
        need(achieved == min(890,cap), 'Rank-prefix optimum not attained')
        prefix_rows.append({'minimum_donor_rank': threshold, 'matching_and_cover_size': cap, 'selected_prefix_size': achieved})
        prefix_covers[threshold] = {'matching': sorted(map(list,matching.items())), 'cover': cover}
    max_cardinality = prefix_rows[-1]['matching_and_cover_size']
    need(max_cardinality == report['maximum_cardinality'], 'Reported maximum cardinality mismatch')
    # Reconstruct all original network arcs with independently inferred flow.
    rn = {int(r): n for r,n in certificate['rank_nodes'].items()}
    dn = {int(d): n for d,n in certificate['donor_nodes'].items()}
    tn = {int(r): n for r,n in certificate['recipient_nodes'].items()}
    s, t = certificate['source'], certificate['target']
    p = certificate['potentials']
    need(set(rn) == set(quotas) and set(dn) == set(graph) and set(tn) == {r for rs in graph.values() for r in rs}, 'Network node domains differ')
    nodes = [s,t] + list(rn.values()) + list(dn.values()) + list(tn.values())
    need(len(nodes) == len(p) and set(nodes) == set(range(len(p))), 'Network node partition invalid')
    need(all(isinstance(x,int) for x in p), 'Noninteger potential')
    arcs = []
    for r in rn:
        arcs.append((s,rn[r],quotas[r],0,quotas[r]))
    for d in graph:
        if rank[d] in rn:
            arcs.append((rn[rank[d]],dn[d],1,0,int(d in picked)))
        for r in graph[d]:
            arcs.append((dn[d],tn[r],1,int(old.get(d) != r),int(picked.get(d) == r)))
    used_r = set(picked.values())
    for r in tn:
        arcs.append((tn[r],t,1,0,int(r in used_r)))
    cost, residual_costs = verify_network(arcs, p, s, t, 890)
    retained = sum(old.get(d) == r for d,r in pairs)
    need(cost == 890-retained == report['changed_pairs'], 'Cost mismatch')
    need(retained == report['retained_old_pairs'], 'Retained-pair mismatch')
    need(min(residual_costs) == report['minimum_residual_reduced_cost'], 'Minimum reduced cost mismatch')
    score = sum(benefit(rank[d]) for d in picked)
    # Independent second calculation purely from histogram, and donor transition histogram.
    old_hist = Counter(rank[d] for d in old)
    gain_by_histogram = sum((quotas[r]-old_hist[r])*benefit(r) for r in set(quotas)|set(old_hist))
    need(abs((score-old_score)-gain_by_histogram) < 1e-8, 'Score methods disagree')
    delta = Counter()
    for sign, matching in ((1,picked),(-1,old)):
        for d in matching:
            delta[17-rank[d]] += sign
            delta[20-rank[d]] -= sign
    need(abs(gain_by_histogram+sum(phi(r)*n for r,n in delta.items())) < 1e-8, 'Transition histogram score disagrees')
    with localcontext() as context:
        context.prec = 60
        def high_phi(r):
            return Decimal(r)*(Decimal(100)/r).ln() if r else Decimal(0)
        precise_gain = sum(Decimal(quotas[r]-old_hist[r])*(high_phi(20-r)-high_phi(17-r)) for r in set(quotas)|set(old_hist))
    result = dict(local_phi_gain_decimal=str(precise_gain),status='PASS',candidate_sha256=digest(candidate_path),certificate_sha256=digest(ROOT/certname),graph_edges=sum(map(len,graph.values())),maximum_cardinality=max_cardinality,selected_cardinality=890,rank_histogram=dict(sorted(quotas.items())),retained_original_exact_pairs=retained,changed_pairs=cost,flow_conservation=True,residual_arcs=len(residual_costs),minimum_reduced_cost=min(residual_costs),rank_prefix_certificates=prefix_rows,primary_score=score,old_primary_score=old_score,local_phi_gain=gain_by_histogram,transition_histogram_delta={r:n for r,n in sorted(delta.items()) if n and r},new_recipients=sorted(used_r-set(old.values())),removed_recipients=sorted(set(old.values())-used_r))
    results[name] = result
    covers[name] = prefix_covers
    print(name, json.dumps(result,sort_keys=True), flush=True)

# Negative controls validate that the certificate test detects two common errors.
# The source audit uses explicit exceptions rather than removable assertions.
control_results = {}
bad_edge = next([d,r] for d in donors for r in recipients[:1] if r not in cache[d])
try:
    verify_pairs([bad_edge], cache, 1)
except ValueError as exc:
    control_results['nonedge_pair_is_rejected'] = str(exc) == 'Ineligible candidate pair'
else:
    control_results['nonedge_pair_is_rejected'] = False
probe = next((d,r) for d,r in pairs if old.get(d) != r)
bad_potentials = list(p)
bad_potentials[dn[probe[0]]] += 10**6
try:
    verify_network(arcs, bad_potentials, s, t, 890)
except ValueError as exc:
    control_results['tampered_potential_is_rejected'] = str(exc) == 'Negative residual reduced-cost arc'
else:
    control_results['tampered_potential_is_rejected'] = False
bad_arcs = list(arcs)
a,b,cap,c,f = bad_arcs[-1]
bad_arcs[-1] = a,b,cap,c,1-f
try:
    verify_network(bad_arcs, p, s, t, 890)
except ValueError as exc:
    control_results['broken_flow_is_rejected'] = str(exc) == 'Flow conservation failed'
else:
    control_results['broken_flow_is_rejected'] = False
need(all(control_results.values()), 'Negative-control failed')
report = dict(status='PASS_INDEPENDENT_BOUNDED_MATCHING_AUDIT',source_head=manifest['head'],source_hashes=source_hashes,graph_sha256=graph_sha256,graph_legality=dict(donors=len(donors),eligible_recipients=len(recipients),edges=sum(map(len,cache.values())),full_exact_reconstruction=True,strict_lifetimes=True,exact_frame_pairs=exact_frame_pairs,nondegenerate_frames=len(nd_witnesses),nondegeneracy_modulus=prime),witnesses=results,negative_controls=control_results,checker_sha256=digest(Path(__file__)),elapsed_seconds=time.time()-START,scope='Optimal primary donor benefit and secondary retained exact original pairs at fixed cardinality 890 on each specified finite graph. Deterministic algorithmic ties are not a uniquely optimal or lexicographically minimal matching claim. No physical-stage admission, integer exponent, unrestricted reuse or global construction optimality claim.')
if args.include_fixed:
    report['unrestricted_primary_gain_over_fixed'] = results['unrestricted']['local_phi_gain']-results['fixed_original_recipients']['local_phi_gain']
report.pop('elapsed_seconds',None)
for witness in report['witnesses'].values():
    for key in ('primary_score','old_primary_score','local_phi_gain'):witness.pop(key,None)
(OUT/'audit-result.json').write_text(json.dumps(report,indent=2)+'\n')
(OUT/'rank-prefix-certificates.json').write_text(json.dumps(covers,sort_keys=True)+'\n')
(OUT/'frame-nondegeneracy-residues.json').write_text(json.dumps(nd_witnesses,sort_keys=True)+'\n')
print(json.dumps(report,sort_keys=True))
