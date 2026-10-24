"""Exploratory coupled frame search. Solver output is not a global proof.
Pinned discovery environment: highspy1.15.1,numpy2.5.4 in tmpfs.
"""
import argparse, sys, json, collections, time, gzip, tempfile, hashlib
from pathlib import Path
from decimal import Decimal, localcontext
HERE = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path, required=True, help='directory for discovery artifacts; do not use the retained record directory')
parser.add_argument('--solver-path', type=Path, help='optional directory containing the pinned highspy/numpy installation')
parser.add_argument('--time-limit', type=float, default=60.0)
args = parser.parse_args()
if args.solver_path:
    sys.path.insert(0, str(args.solver_path.resolve()))
sys.path.insert(0, str(HERE))
import highspy, numpy as np
import verify
from frame_dag import NativeSchedule, basis, space, join, image, dimension, linear, need
from replay import replay
OUT = args.output.resolve()
need(OUT != Path(__file__).resolve().parent, 'Choose a separate output directory; retained records are read-only')
need(0 < args.time_limit <= 600, 'Solver limit must be positive and at most 600 seconds')
need(highspy.Highs().version() == '1.15.1' and np.__version__ == '2.5.4', 'Use the pinned discovery requirements')
OUT.mkdir(parents=True, exist_ok=True)
started = time.monotonic()
retained = verify.source()
s = NativeSchedule(retained['canonical'], retained['programs']['forward'])
g = s.graph
lo, hi = g.bounds()
flex = [i for i in range(len(lo)) if lo[i] != hi[i]]
quotient = {}

def quotient_spaces(d):
    if d not in quotient:
        values = {1}
        for v in range(1, 1 << d):
            values |= {join(u, space([v])) for u in tuple(values)}
        quotient[d] = sorted(values)
    return quotient[d]

def domain(a, b):
    complement = []
    generated = a
    for v in basis(b):
        if not generated >> v & 1:
            complement.append(v)
            generated = join(generated, space([v]))
    return sorted({join(a, space([linear(complement, x) for x in basis(q)])) for q in quotient_spaces(len(complement))}, key=lambda v: (dimension(v), v))
D = {i: domain(lo[i], hi[i]) for i in flex}
need(sum(map(len, D.values())) == 4684, 'Full marginal domain census')
cost = []
initial = []
rows = []
lb = []
ub = []
x = {}
yd = {}
constant = 0.0
with localcontext() as ctx:
    ctx.prec = 80
    q = Decimal(1) - Decimal(15108879) / Decimal(5000000000)
    prices = [0.0] + [float(Decimal(r) - (q * Decimal(r).ln()).exp()) for r in range(1, 10)]

def var(objective=0.0, start=0.0):
    k = len(cost)
    cost.append(objective)
    initial.append(start)
    return k

def row(coeff, low, high):
    coeff = {i: v for i, v in coeff.items() if v}
    rows.append(coeff)
    lb.append(low)
    ub.append(high)
for i in flex:
    x[i] = [var(start=int(v == s.original_values[i])) for v in D[i]]
    need(sum((initial[k] for k in x[i])) == 1, 'Original frame in full marginal domain')
    row(dict.fromkeys(x[i], 1), 1, 1)
E = collections.Counter(((a, b, m) for b in range(len(g.parents)) for a, m in g.parents[b]))
for (a, b, m), count in E.items():
    if a not in D and b not in D:
        constant += count * prices[dimension(lo[b]) - dimension(lo[a])]
        continue
    if a not in D:
        for k, v in zip(x[b], D[b]):
            cost[k] += count * prices[dimension(v) - dimension(lo[a])]
        continue
    if b not in D:
        for k, v in zip(x[a], D[a]):
            cost[k] += count * prices[dimension(lo[b]) - dimension(v)]
        continue
    ranks = set()
    for ia, a_value in enumerate(D[a]):
        transported = image(m, a_value)
        allowed = []
        for ib, b_value in enumerate(D[b]):
            if transported & b_value == transported:
                allowed.append(x[b][ib])
                ranks.add(dimension(b_value) - dimension(a_value))
        need(allowed, 'Each source marginal extends along every edge')
        if len(allowed) != len(D[b]):
            coeff = {v: -1 for v in allowed}
            coeff[x[a][ia]] = 1
            row(coeff, -highspy.kHighsInf, 0)
    original_rank = dimension(s.original_values[b]) - dimension(s.original_values[a])
    ys = {r: var(count * prices[r], int(r == original_rank)) for r in sorted(ranks)}
    yd[a, b, m] = ys
    row(dict.fromkeys(ys.values(), 1), 1, 1)
    coeff = {k: dimension(v) for k, v in zip(x[b], D[b])}
    for k, v in zip(x[a], D[a]):
        coeff[k] = coeff.get(k, 0) - dimension(v)
    for r, k in ys.items():
        coeff[k] = -r
    row(coeff, 0, 0)
constant += 8 * prices[8]
for coeff, l, u in zip(rows, lb, ub):
    value = sum((a * initial[k] for k, a in coeff.items()))
    need(l - 1e-08 <= value <= u + 1e-08, 'Exact source start satisfies model rows')
baseline = replay(retained['canonical'], retained['programs']['forward'])
expected = sum((n * prices[r] for r, n in baseline.items()))
warm = sum((a * b for a, b in zip(cost, initial))) + constant
need(abs(expected - warm) < 1e-08, 'MIP objective matches native child profile at original source')
lp = highspy.HighsLp()
lp.num_col_ = len(cost)
lp.num_row_ = len(rows)
lp.sense_ = highspy.ObjSense.kMaximize
lp.offset_ = constant
lp.col_cost_ = cost
lp.col_lower_ = [0.0] * len(cost)
lp.col_upper_ = [1.0] * len(cost)
lp.row_lower_ = lb
lp.row_upper_ = ub
lp.integrality_ = [highspy.HighsVarType.kInteger] * len(cost)
lp.col_names_ = ['v' + str(i) for i in range(len(cost))]
lp.row_names_ = ['r' + str(i) for i in range(len(rows))]
starts = [0]
indices = []
values = []
for coeff in rows:
    for k, a in sorted(coeff.items()):
        indices.append(k)
        values.append(a)
    starts.append(len(indices))
lp.a_matrix_.format_ = highspy.MatrixFormat.kRowwise
lp.a_matrix_.start_ = starts
lp.a_matrix_.index_ = indices
lp.a_matrix_.value_ = values
h = highspy.Highs()
for key, value in [('threads', 1), ('parallel', 'off'), ('time_limit', args.time_limit), ('mip_rel_gap', 0.0), ('mip_abs_gap', 1e-10), ('log_to_console', False), ('log_file', str(OUT / 'coupled-mip.log'))]:
    need(h.setOptionValue(key, value) == highspy.HighsStatus.kOk, 'HiGHS option ' + key)
need(h.passModel(lp) == highspy.HighsStatus.kOk, 'HiGHS model load')
sol = highspy.HighsSolution()
sol.col_value = initial
sol.value_valid = True
need(h.setSolution(sol) == highspy.HighsStatus.kOk, 'HiGHS source warm start')
print(json.dumps({'stage': 'model_ready', 'seconds': time.monotonic() - started, 'nodes': len(lo), 'flex': len(flex), 'domain_values': sum(map(len, D.values())), 'variables': len(cost), 'rows': len(rows), 'nonzeros': len(indices), 'source_objective': expected}), flush=True)
temporary_model = tempfile.TemporaryDirectory(prefix='carried-mip-model-')
model_path = Path(temporary_model.name) / 'model.mps'
need(h.writeModel(str(model_path)) == highspy.HighsStatus.kOk, 'Model export')
h.run()
info = h.getInfo()
solution = h.getSolution()
need(solution.value_valid, 'Feasible solver assignment required')
chosen = lo[:]
for i in flex:
    selected = [j for j, k in enumerate(x[i]) if solution.col_value[k] > 0.5]
    need(len(selected) == 1, 'Integral single frame choice')
    chosen[i] = D[i][selected[0]]
g.check(chosen)
(OUT / 'coupled-values.json.gz').write_bytes(gzip.compress(json.dumps(chosen).encode(), mtime=0))
checks = {}
forward_variables = [i for i, fixed in enumerate(g.fixed) if fixed is None]
for direction, p in retained['programs'].items():
    schedule = NativeSchedule(retained['canonical'], p)
    assigned = schedule.original_values[:] if direction == 'backward' else chosen[:]
    if direction == 'backward':
        backward_variables = [i for i, fixed in enumerate(schedule.graph.fixed) if fixed is None]
        need(len(forward_variables) == len(backward_variables), 'Dual variable contact census')
        for a, b in zip(forward_variables, backward_variables):
            assigned[b] = chosen[a]
    schedule.graph.check(assigned)
    c, word = schedule.realize(assigned)
    paid = replay(c, word, direction == 'backward')
    cuts = verify.cut_differences(paid, baseline)
    checks[direction] = {'paid': verify.profile_record(paid), 'rank_mass': sum((r * n for r, n in paid.items())), 'min_rank_cuts': cuts, 'operator_endpoint_pass': True, 'frames': len(c['frames'])}
    payload = json.dumps({'canonical': c, 'program': word, 'values': assigned}, sort_keys=True).encode()
    (OUT / ('coupled-' + direction + '.json.gz')).write_bytes(gzip.compress(payload, mtime=0))
report = {'stage': 'completed_discovery_only', 'solver': 'highspy ' + h.version(), 'numpy': np.__version__, 'status': str(h.getModelStatus()), 'objective': info.objective_function_value, 'source_objective': expected, 'gap': info.mip_gap, 'dual_bound': info.mip_dual_bound, 'mip_nodes': info.mip_node_count, 'elapsed': time.monotonic() - started, 'changed_contacts': sum((chosen[i] != s.original_values[i] for i in flex)), 'checks': checks, 'not_a_rigorous_optimality_certificate': True, 'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'source_modules_sha256': {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest() for name in ('frame_dag.py', 'replay.py', 'verify.py')}, 'source_manifest_sha256': hashlib.sha256((HERE / 'SOURCES.json').read_bytes()).hexdigest(), 'source_base_commit': json.loads((HERE / 'SOURCES.json').read_text())['base_commit'], 'time_limit': args.time_limit, 'model_dimensions': {'columns': len(cost), 'rows': len(rows), 'nonzeros': len(indices), 'marginal_choices': sum(map(len, D.values()))}}
(OUT / 'coupled-mip-result.json').write_text(json.dumps(report, indent=2) + '\n')
(OUT / 'coupled-model.mps.gz').write_bytes(gzip.compress(model_path.read_bytes(), mtime=0))
temporary_model.cleanup()
print(json.dumps(report), flush=True)
