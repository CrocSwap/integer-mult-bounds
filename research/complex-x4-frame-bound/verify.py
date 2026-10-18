"""Exact frame-assignment exclusion for the selected X4 complex word (standard library only).

Claim: for the fixed scalar program of the selected PR799 complex word, no assignment of
frames to its A, B and early-cleanup (tail) gates that satisfies the audit_local.py frame
contract admits the complex saving b_next = (selected complex endpoint) + 10^-24. Hence
frame reassignment alone cannot raise the selected kappa. See README.md for scope.
"""
import argparse
import gzip
import hashlib
import importlib.util
import itertools
import json
import sys
import tarfile
import time
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
import model as M  # noqa: E402

ARCHIVE = 'research/community-frontier799-audit/pr799-replay.tar.gz'
ARCHIVE_SHA256 = '4dff69f3509ca81ab768ebf4b39bb6313b331995e4b2a412729b541a39c8459a'
MEMBER = 'pr799-native-fresh/jx/FULL-WORD.json.gz'
WORD_SHA256 = '1e1d99ba7aab877d6b573c41f7030ee73de9a52fee51d0a822ddaae71251999f'
ASSEMBLY = 'research/community-frontier799-audit/ASSEMBLY.json'
SELECTED = 'certificates/checkpoints/frontier799.json'
ENGINES = 'research/complex-k492-owner-repair/vendor/multicold/engines'
ENGINE_PINS = {'moment.py': '81cbc864e106418fc7854322746f72180cb8110ff39f74450a3b8d55a82c1482',
               'base_two_moment.py': 'aee70c242a2f1d225528fabe2002e1564d1dc884797c07d28a831c7878ee9098'}
OUTER_PIN = 'c1ebb52163a7219504c728a5c2b098bf1e50bf20148a2879c5a74c3cadc7c03c'
DUALS = HERE / 'data' / 'DUALS.json.gz'
m_, W_, CALLS = 73, 7168, 72
RANKS = range(2, M.H + 1)


def require(ok, label):
    if not ok:
        raise RuntimeError(label)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def values_of(obj, key):
    """Every value stored under `key` anywhere in a JSON object."""
    if isinstance(obj, dict):
        for k, x in obj.items():
            if k == key:
                yield x
            yield from values_of(x, key)
    elif isinstance(obj, list):
        for x in obj:
            yield from values_of(x, key)


def load_selected_word(repo, word_path=None):
    """The X4 word, either from the retained PR799 replay archive or a fresh rebuild."""
    receipt = (repo / 'docs/research/community-frontier799-integration.json').read_text()
    recipe = json.loads((repo / 'research/gauge44-frames-x/construction/jx/RECIPE-X4.json').read_text())
    local = json.loads((repo / 'research/community-frontier799-audit/INDEPENDENT-LOCAL.json').read_text())
    require(list(values_of(recipe, 'output_content_sha256')) == [WORD_SHA256], 'RECIPE-X4 output pin')
    require(local['content_sha256'] == WORD_SHA256, 'independent local audit content pin')
    if word_path is None:
        archive = (repo / ARCHIVE).read_bytes()
        require(sha256(archive) == ARCHIVE_SHA256, 'replay archive hash')
        require(ARCHIVE_SHA256 in receipt, 'archive hash recorded in the integration receipt')
        with tarfile.open(repo / ARCHIVE) as tar:
            raw = tar.extractfile(MEMBER).read()
        source = dict(kind='retained PR799 replay archive', archive=ARCHIVE, archive_sha256=ARCHIVE_SHA256, member=MEMBER)
    else:
        raw = Path(word_path).read_bytes()
        source = dict(kind='supplied word file', path=Path(word_path).name)
    word = parse_word(gzip.decompress(raw))
    source.update(content_sha256=WORD_SHA256)
    return word, source


def parse_word(content):
    require(sha256(content) == WORD_SHA256, 'X4 word content hash')
    return json.loads(content)


def selected_assembly(repo):
    selected = json.loads((repo / SELECTED).read_text())
    raw = (repo / ASSEMBLY).read_bytes()
    require(selected['certificate'] == ASSEMBLY and sha256(raw) == selected['certificate_sha256'], 'selected assembly pin')
    return selected, json.loads(raw)


def excluded_exponent(repo):
    """Next 10^-24 grid point above the selected complex endpoint."""
    _, assembly = selected_assembly(repo)
    lower = F(assembly['complex_lower'])
    require(lower.denominator == 10 ** 24, 'complex endpoint grid')
    return lower + F(1, 10 ** 24)


def load_engines(repo):
    engines = {}
    for name, pin in ENGINE_PINS.items():
        path = repo / ENGINES / name
        require(sha256(path.read_bytes()) == pin, 'engine pin ' + name)
        spec = importlib.util.spec_from_file_location('x4fb_' + name[:-3], path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        engines[name] = module
    mercator = lambda H, W, b: engines['moment.py'].moment(H, m_, W, b, False)
    base_two = lambda H, W, b: engines['base_two_moment.py'].moment(m_, W, sorted(H.items()), b)
    return {'mercator': mercator, 'base_two': base_two}


def charges(engine, b):
    """Outward rational bounds on C_d = M_d - d*M_1 with M_d = d*(73/d)^b, d = 2..9."""
    Mb = {}
    for d in range(1, M.H + 1):
        lo, hi = engine({d: 1}, 1, b)          # d*(73/d)^b / 73, outward
        Mb[d] = (m_ * lo, m_ * hi)
    out = {}
    for d in RANKS:
        out[d] = (Mb[d][0] - d * Mb[1][1], Mb[d][1] - d * Mb[1][0])
        require(out[d][0] <= out[d][1] < 0, 'charge interval')
    return out


def lower_value(vec, bounds):
    return sum((x * (bounds[d][0] if x > 0 else bounds[d][1]) for d, x in vec.items() if x), F(0))


def nsub(k):
    """Number of subspaces of F_2^k (sum of Gaussian binomials)."""
    total = 0
    for j in range(k + 1):
        num = den = 1
        for i in range(j):
            num *= (1 << (k - i)) - 1
            den *= (1 << (j - i)) - 1
        total += num // den
    return total


def parse_duals(raw):
    data = json.loads(gzip.decompress(raw))
    comps = []
    for c in data['components']:
        duals = {}
        for key, vec in c['duals'].items():
            duals[key] = {int(d): F(x) for d, x in vec.items()}
            require(all(d in RANKS for d in duals[key]), 'dual coordinate outside C_2..C_9')
        comps.append(dict(first=c['first'], nodes=c['nodes'], duals=duals))
    return data, comps


def check_components(model, comps, duals, bounds, baseline):
    """Weak-duality certificate per component; returns the summed baseline cost vector."""
    require(len(duals) == len(comps), 'component count')
    total = Counter()
    stats = Counter()
    for comp, entry in zip(comps, duals):
        require(entry['first'] == json.dumps(comp[0]) and entry['nodes'] == len(comp), 'component identity')
        labels, unary, pairs = model.component_problem(comp)
        for node in comp:
            k = len(model.hi[node]) - len(model.lo[node])
            require(len(labels[node]) == nsub(k), 'incomplete domain')
            require(len(set(labels[node])) == len(labels[node]), 'repeated label')
            require(all(M.contained(model.lo[node], Fr) and M.contained(Fr, model.hi[node]) for Fr in labels[node]), 'label outside interval')
        rows, rhs, cols = M.lp(labels, unary, pairs)
        keys = [json.dumps(r) for r in rows]
        index = {k: i for i, k in enumerate(keys)}
        require(all(k in index for k in entry['duals']), 'dual for an unknown row')
        q = [entry['duals'].get(k, {}) for k in keys]
        for key, c, entries in cols:
            r = {d: F(c[d]) for d in RANKS}
            for i, a in entries:
                for d, x in q[i].items():
                    r[d] -= a * x
            if any(r.values()):
                for name, b in bounds.items():
                    require(lower_value(r, b) > 0, 'negative reduced cost (%s) at %s' % (name, key))
                stats['positive'] += 1
            else:
                stats['zero'] += 1
        objective = Counter()
        for i, vec in enumerate(q):
            for d, x in vec.items():
                objective[d] += rhs[i] * x
        base = M.assignment_cost(labels, unary, pairs, {node: baseline[node] for node in comp})
        require(all(objective[d] == base[d] for d in RANKS), 'dual objective differs from the baseline')
        for d in RANKS:
            total[d] += base[d]
        stats['columns'] += len(cols)
        stats['rows'] += len(rows)
    return total, stats


def brute_force(model, comps, bounds, baseline, limit):
    """Independent cross-check without duality: enumerate small components completely."""
    checked = assignments = 0
    for comp in comps:
        labels, unary, pairs = model.component_problem(comp)
        size = 1
        for node in comp:
            size *= len(labels[node])
        if size > limit:
            continue
        base = M.assignment_cost(labels, unary, pairs, {node: baseline[node] for node in comp})
        for choice in itertools.product(*(labels[node] for node in comp)):
            X = dict(zip(comp, choice))
            if not all((X[a], X[b]) in table for (a, b), table in pairs.items()):
                continue
            c = M.assignment_cost(labels, unary, pairs, X)
            diff = {d: c[d] - base[d] for d in RANKS}
            if any(diff.values()):
                for b in bounds.values():
                    require(lower_value(diff, b) > 0, 'brute force found a cheaper or tied assignment')
            assignments += 1
        checked += 1
    return checked, assignments


def global_step(assembly, local_profile, engines, b):
    profile = {int(r): n for r, n in assembly['complex_profile'].items()}
    require(sum(r * n for r, n in profile.items()) == m_ * W_ - 2560, 'global rank deficit')
    rest = {r: profile.get(r, 0) - CALLS * local_profile.get(r, 0) for r in set(profile) | set(local_profile)}
    require(all(x >= 0 for x in rest.values()), 'global profile below 72 local calls')
    require(assembly['provider_counts'] == {'gauge44': CALLS} and assembly['binding'] == 'complex', 'single complex provider')
    out = {}
    for name, engine in engines.items():
        lo, hi = engine(profile, W_, b)
        out[name] = str(lo - 1)
        require(lo > 1, 'baseline admitted at the excluded exponent (%s)' % name)
        lo2, hi2 = engine(profile, W_, F(assembly['complex_lower']))
        require(hi2 < 1, 'baseline not admitted at the selected endpoint (%s)' % name)
    return dict(remainder={str(r): x for r, x in sorted(rest.items()) if x}, moment_minus_one_lower=out)


def kappa_step(selected, b):
    """outer.py requires kappa < eps*q = (1-eta)q/(1+q), q = a(1-2*eta), and a < b, so kappa < b/(1+b)."""
    outer = REPO / ENGINES / 'outer.py'
    require(sha256(outer.read_bytes()) == OUTER_PIN, 'outer engine pin')
    k = F(selected['kappa'])
    require(b / (1 + b) < k + F(1, 10 ** 18), 'excluded exponent does not exclude the next kappa tick')
    return dict(selected_kappa=selected['kappa'], next_kappa_tick=str(k + F(1, 10 ** 18)),
                outer_engine_sha256=OUTER_PIN, b_next_over_one_plus_b_next_below_next_tick=True)


def legal_worse_assignment(model, comps, bounds, baseline):
    """A legal assignment of one small component that is strictly costlier than the baseline."""
    for comp in comps:
        labels, unary, pairs = model.component_problem(comp)
        if len(comp) < 2 or len(list(itertools.product(*(labels[n] for n in comp)))) > 5000:
            continue
        base = M.assignment_cost(labels, unary, pairs, {node: baseline[node] for node in comp})
        for choice in itertools.product(*(labels[node] for node in comp)):
            X = dict(zip(comp, choice))
            if not all((X[a], X[b]) in table for (a, b), table in pairs.items()):
                continue
            c = M.assignment_cost(labels, unary, pairs, X)
            diff = {d: c[d] - base[d] for d in RANKS}
            if any(diff.values()) and all(lower_value(diff, b) > 0 for b in bounds.values()):
                worse = dict(baseline)
                worse.update(X)
                model.profile(worse)       # raises unless every frame chain is monotone
                return worse
    raise RuntimeError('no legal worse assignment found for the control')


def run(word_path=None, duals_path=DUALS, mutate=None):
    begin = time.monotonic()
    require(__debug__, 'run without -O: the model relies on assertions')
    word, source = load_selected_word(REPO, word_path)
    if mutate == 'wrong_word':
        tampered = json.loads(json.dumps(word))
        tampered['B'][0][-1] = list(M.FULL)
        word = parse_word(json.dumps(tampered).encode())
    selected, assembly = selected_assembly(REPO)
    b = excluded_exponent(REPO)
    model = M.Model(word)
    baseline = model.baseline()
    local_profile = model.profile(baseline)
    require(local_profile == {int(k): x for k, x in word['report']['local_profile'].items()}, 'baseline profile')
    engines = load_engines(REPO)
    bounds = {name: charges(engine, b) for name, engine in engines.items()}
    data, duals = parse_duals(Path(duals_path).read_bytes())
    require(data['word_content_sha256'] == WORD_SHA256 and F(data['excluded_b']) == b, 'dual payload binding')
    comps = model.components()
    if mutate == 'drop_component':
        duals = duals[:-1]
    if mutate == 'inflate_dual':
        entry = max(duals, key=lambda e: e['nodes'])
        key = sorted(k for k in entry['duals'] if k.startswith('["N"'))[0]
        entry['duals'][key][2] = entry['duals'][key].get(2, F(0)) + 1
    if mutate == 'omit_label':
        node = max(model.domain, key=lambda x: (len(model.domain[x]), x))
        model.domain[node] = model.domain[node][:-1]
    if mutate == 'worse_baseline':
        baseline = legal_worse_assignment(model, comps, bounds, baseline)
    total, stats = check_components(model, comps, duals, bounds, baseline)
    small, assignments = brute_force(model, comps, bounds, baseline, 200000) if mutate is None else (0, 0)
    if mutate == 'accepted_endpoint':
        b -= F(1, 10 ** 24)     # the duals still certify; the global step must refuse this b
    globally = global_step(assembly, local_profile, engines, b)
    kappa = kappa_step(selected, b)
    return dict(status='PASS_X4_FRAME_ASSIGNMENT_EXCLUSION',
                word=source, excluded_b=f'{b.numerator}/{b.denominator}',
                gates=len(model.gates), free_gates=len(model.domain),
                domain_sizes={str(k): x for k, x in sorted(Counter(len(d) for d in model.domain.values()).items())},
                components=len(comps), lp_rows=stats['rows'], lp_columns=stats['columns'],
                zero_reduced_costs=stats['zero'], positive_reduced_costs=stats['positive'],
                cone_ceilings=len(model.ceil), baseline_local_profile={str(k): x for k, x in local_profile.items()},
                brute_forced_components=small, brute_forced_assignments=assignments,
                global_step=globally, kappa_step=kappa, engines=sorted(ENGINE_PINS),
                elapsed_seconds=round(time.monotonic() - begin, 1))


CONTROLS = ['drop_component', 'inflate_dual', 'omit_label', 'accepted_endpoint', 'worse_baseline', 'wrong_word']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--word', type=Path, help='optional freshly rebuilt X4 FULL-WORD.json.gz')
    parser.add_argument('--duals', type=Path, default=DUALS)
    parser.add_argument('--controls', action='store_true', help='also require every negative control to be rejected')
    parser.add_argument('--output', type=Path, help='write the JSON receipt here')
    args = parser.parse_args()
    result = run(args.word, args.duals)
    if args.controls:
        rejected = {}
        for name in CONTROLS:
            try:
                run(args.word, args.duals, mutate=name)
            except (RuntimeError, AssertionError, ValueError) as exc:
                rejected[name] = str(exc)[:120]
            else:
                raise SystemExit('FAIL: control accepted: ' + name)
        result['controls_rejected'] = rejected
    text = json.dumps(result, indent=2) + '\n'
    if args.output:
        args.output.write_text(text, newline='\n')
    print(text, end='')
    print(result['status'] + (' controls=%d/%d' % (len(result['controls_rejected']), len(CONTROLS)) if args.controls else ''))


if __name__ == '__main__':
    main()
