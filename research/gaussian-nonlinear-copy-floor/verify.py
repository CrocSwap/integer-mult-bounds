#!/usr/bin/env python3
"""Source-pinned Gaussian nonlinear message floor. Python 3.10+, stdlib."""
import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def check_sources():
    sources = json.loads((HERE / 'SOURCES.json').read_text())
    require(sources['base_commit'] == 'f567884aeb8851b6e794af1184119a3bfbe1e631', 'base pin changed')
    require(set(sources['vendor']) == {'vendor/pr738/' + name for name in
            ('geometry.py', 'verify.py', 'certificate.json', 'PROOF.md', 'README.md', 'SOURCES.json')},
            'vendor pin inventory changed')
    require(set(sources['predecessors']) == {'785', '814'}, 'method pin inventory changed')
    require(set(sources['base_sources']) == {
        'certificates/selected-result.json', 'docs/research/current-status.md',
        'docs/research/pr-ledger.md', 'docs/research/community-frontier799-review.md',
        'research/gauge44-frames-x/PROOF-NOTE-FRAMES-X4.md',
        'research/e8-decoder-floors-and-cold14-notes/s1-extension-rings/REPORT.md',
        'research/e8-decoder-floors-and-cold14-notes/s1-extension-rings/gauss_geom.py',
        'research/e8-decoder-floors-and-cold14-notes/s1-extension-rings/algebra_lines.py',
        'research/format-limits/README.md'}, 'base pin inventory changed')
    for local, pin in sources['vendor'].items():
        require(digest((HERE / local).read_bytes()) == pin['sha256'], 'vendor source mismatch: ' + local)
    for pin in sources['predecessors'].values():
        require(digest((HERE / pin['local_path']).read_bytes()) == pin['sha256'], 'predecessor source mismatch')
    for local, pin in sources['base_sources'].items():
        require(digest((ROOT / local).read_bytes()) == pin['sha256'], 'base source mismatch: ' + local)
    selected = json.loads((ROOT / 'certificates/selected-result.json').read_text())
    require(selected['kappa'] == sources['selected_kappa'], 'selected kappa changed')
    return sources


def load_vendor():
    require(__debug__, 'retained PR738 geometry uses assertions; optimized Python is unsupported')
    def load(name, path):
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        require(Path(module.__file__).resolve() == path.resolve(), 'unexpected module origin')
        return module
    geometry = load('geometry', HERE / 'vendor/pr738/geometry.py')
    replay = load('gaussian_pr738_replay', HERE / 'vendor/pr738/verify.py')
    return geometry, replay


def demand_floor(demands, cliques):
    require(len(demands) == 60 and all(type(x) is int and x >= 0 for x in demands), 'invalid demand vector')
    averaged = (2 * sum(demands) + 2) // 3
    concentrated = max(sum(demands[i] for i in range(60) if (q >> i) & 1) for q in cliques)
    return max(averaged, concentrated)


def compare_receipt(actual, expected):
    require(actual == expected, 'certificate mismatch')


def calculate():
    check_sources()
    geometry, replay = load_vendor()
    # Retained verifier's calculate() is called without its historical source/selected
    # check. Our check_sources() binds the same geometry and the current base instead.
    inherited = replay.calculate()
    compare_receipt(inherited, json.loads((HERE / 'vendor/pr738/certificate.json').read_text()))
    lines = geometry.gaussian_lines()
    graph = geometry.nonorthogonality(lines)
    all_cliques = geometry.maximal_cliques(graph)
    cliques = tuple(q for q in all_cliques if q.bit_count() == 12)
    incidences = [sum((q >> i) & 1 for q in cliques) for i in range(60)]
    require(incidences == [128] * 60, 'unequal or incorrect clique incidence')
    require(demand_floor([1] * 60, all_cliques) == 40, 'uniform floor changed')
    concentrated = [(cliques[44] >> i) & 1 for i in range(60)]
    require(demand_floor(concentrated, all_cliques) == 12, 'concentration floor changed')
    rounded = [0] * 60
    rounded[44] = 1
    require(demand_floor(rounded, all_cliques) == 1, 'integer demand floor changed')
    spec = importlib.util.spec_from_file_location('gaussian_nonlinear_controls', HERE / 'independent_controls.py')
    controls = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(controls)
    finite = controls.calculate(lines, graph, cliques)
    deficits = {str(s): 40 * (s - 3) for s in (1, 2, 3, 5, 7)}
    require(deficits['3'] == 0 and deficits['5'] > 0, 'optimistic stage screen changed')
    return {
        'schema': 1,
        'base_commit': 'f567884aeb8851b6e794af1184119a3bfbe1e631',
        'assignment_seed': 44,
        'status': 'scoped negative result; no new kappa',
        'geometric_premise': inherited,
        'port_clique_incidences': incidences,
        'demand_coefficient': '2/3',
        'uniform_gaussian_floor_per_bit': 40,
        'uniform_rational_floor_per_bit': 80,
        'concentrated_twelve_port_floor': 12,
        'optimistic_deficit_per_bit': deficits,
        'finite_nonlinear_controls': finite,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-sources', action='store_true', help='check only immutable inputs, not the theorem')
    parser.add_argument('--output', type=Path, help='write a verified receipt to a NEW file')
    args = parser.parse_args()
    require(__debug__, 'retained PR738 geometry uses assertions; optimized Python is unsupported')
    if args.output:
        require(not args.output.exists(), 'output path already exists')
    if args.check_sources:
        check_sources()
        print('PASS_GAUSSIAN_NONLINEAR_SOURCES_ONLY')
        return
    actual = calculate()
    compare_receipt(actual, json.loads((HERE / 'CERTIFICATE.json').read_text()))
    if args.output:
        with args.output.open('x') as out:
            out.write(json.dumps(actual, indent=2, sort_keys=True) + '\n')
    print('PASS_GAUSSIAN_NONLINEAR_COPY_FLOOR lines=60 cliques=640 flat_pairs=2579856 floor=40b no_new_kappa')


if __name__ == '__main__':
    main()
