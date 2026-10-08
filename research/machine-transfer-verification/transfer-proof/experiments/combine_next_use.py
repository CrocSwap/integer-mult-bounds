#!/usr/bin/env python3
"""Compare exactly emitted next-use-score axes with the public PR68 baseline.

This does not regenerate a word. It reconstructs complete profiles and uses
independent rational enclosures to select a combination only when intervals
strictly separate. The selected word still requires full replay/profile
validation. Public cost/live composition credit belongs to PR67/PR68.
"""
import argparse
import hashlib
import importlib.util
import itertools
import json
import shutil
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUTPUTS = HERE.parents[1]
sys.path.insert(0, str(OUTPUTS))
from independent_moment import encode, moment, root_bracket
from independent_assembly import assemble

def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def read(path):
    return json.loads(path.read_text())

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', type=Path, required=True)
    ap.add_argument('--include-order23', action='store_true')
    args = ap.parse_args()
    root = args.repo.resolve()
    base = root/'research/cost-live-both'
    old = read(base/'candidate.json')
    source = {h: [base, root/f'research/audit-next{h}'] for h in (23,25)}
    if args.include_order23:
        source[23].append(root/'research/audit-order23')
    sys.path[:0] = [str(root/'scripts/experiments'), str(root/'research/pair-assembly')]
    constructor = load(root/'research/pair-assembly/frame/frame_verify.py', 'profile_constructor')
    constructor.check_sources()
    trials = []
    for choices in itertools.product(range(len(source[23])), range(len(source[25]))):
        profiles, axes = [], {}
        for h, choice in zip((23,25), choices):
            src = source[h][choice]
            profiles.append(read(src/f'frame-profiles-{h}.json'))
            axes[str(h)] = read(src/'frame-compiler.json')['axes'][str(h)]
        constructor.WIRES_S = 2*4073300 + sum(4073300//p['v']*p['R'] for p in profiles)
        constructor.MASS_S = 575*constructor.WIRES_S - 1846900
        profile = constructor.profile(profiles, dict(axes=axes))
        rows = {int(t):n for t,n in profile['child_multiplicities'].items()}
        bound = moment(profile['m'], profile['W'], rows, Q(old['bit_saving']))
        trials.append(dict(choices=choices, profile=profile, axes=axes, moment=bound))
    baseline = trials[0]
    assert encode(baseline['profile']) == old['bit']
    best = baseline
    for trial in trials[1:]:
        if trial['moment'][1] < best['moment'][0]:
            best = trial
    summary = dict(baseline_pin='85781f662b57521743cce07cdd5ea194e6f3879d',
                   baseline_kappa=old['kappa'], reference_saving=old['bit_saving'],
                   trials=[dict(choices=t['choices'], W=t['profile']['W'],
                                R=[t['axes'][str(h)]['compiled']['roles'] for h in (23,25)],
                                moment=t['moment'],
                                delta=[t['moment'][0]-baseline['moment'][1],
                                       t['moment'][1]-baseline['moment'][0]]) for t in trials],
                   strict_characteristic_improvement=best is not baseline,
                   selected_choices=best['choices'],
                   choice_names={h:[str(p.relative_to(root)) for p in choices] for h,choices in source.items()},
                   scope='Emitted-word and exact paid-profile screen; full independent replay still required')
    if best is not baseline:
        dst = root/'research/audit-selected'
        shutil.copytree(base, dst, ignore=shutil.ignore_patterns('build'), dirs_exist_ok=True)
        for h, choice in zip((23,25), best['choices']):
            src = source[h][choice]
            for prefix,suffix in [('frame-word-', '.json.gz'), ('frame-profiles-', '.json'), ('frame-transitions-', '.json')]:
                shutil.copyfile(src/f'{prefix}{h}{suffix}', dst/f'{prefix}{h}{suffix}')
            shutil.copyfile(src/'compiler.py', dst/f'compiler-source-{h}.py')
        records = dict(axes=best['axes'])
        (dst/'frame-compiler.json').write_text(json.dumps(records, indent=2)+'\n')
        rows = {int(t):n for t,n in best['profile']['child_multiplicities'].items()}
        lo,hi = root_bracket(575, best['profile']['W'], rows, digits=18)
        old_wire_bits = old['finite_bridge']['bit']['wire_bits']
        bridge = json.loads(json.dumps(old['finite_bridge']))
        bridge['bit']['W'] = best['profile']['W']
        bridge['bit']['wire_bits'] = best['profile']['W'].bit_length()
        assert bridge['bit']['wire_bits'] == old_wire_bits
        exact = load(root/'research/slot-cost-rank-pair/arithmetic/refine.py', 'inherited_exact_assembly')
        preferred = exact.assemble(bridge, lo, Q(1,10**12), 10**18)
        selected = dict(status='Exact profile improvement; pending full replay',
                        bit=best['profile'], finite_bridge=bridge, bit_saving=lo,
                        kappa=preferred['kappa'], preferred=preferred,
                        accepted_moment=exact.exact_moment(575,best['profile']['W'],rows,lo),
                        rejected_moment=exact.exact_moment(575,best['profile']['W'],rows,hi),
                        source_sha256={str((dst/f'compiler-source-{h}.py').relative_to(root)):
                                       hashlib.sha256((dst/f'compiler-source-{h}.py').read_bytes()).hexdigest() for h in (23,25)},
                        baseline_pin=summary['baseline_pin'], choices=best['choices'])
        independent = assemble(selected,lo,preferred['kappa'],Q(1,10**12))
        assert independent['constraints'] == preferred['assembly']['constraints']
        assert independent['margins'] == preferred['assembly']['margins']
        (dst/'candidate.json').write_text(json.dumps(encode(selected),indent=2)+'\n')
        summary.update(kappa=preferred['kappa'], bit_saving=lo, root_bracket=[lo,hi],
                       delta_kappa=preferred['kappa']-Q(old['kappa']),
                       assembly_constraints=47, assembly_margins=7,
                       selected_relative_path='research/audit-selected')
    (HERE/'next-use-comparison.json').write_text(json.dumps(encode(summary),indent=2)+'\n')
    print(json.dumps(encode({k:v for k,v in summary.items() if k!='trials'}),indent=2))

if __name__ == '__main__':
    main()
