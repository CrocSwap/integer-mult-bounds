"""Independent exact verifier for Matroid Circulation Reclaim over Deferred Signed Networks.
Proves exact rational moments, all 47 assembly inequalities, and rejection of adjacent grid points.
"""
import sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode = True

from pathlib import Path
from fractions import Fraction as Q
from hashlib import sha256
import json, copy, importlib.util

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PARENT = ROOT / 'research/deferred-balanced'

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

moments = load('moments', PARENT / 'moments.py')
balanced = load('balanced_assembly', ROOT / 'research/copied-fixed/balanced_assembly.py')

js = moments.arithmetic.js

def rational(x):
    if isinstance(x, dict):
        return {k: rational(y) for k, y in x.items()}
    if isinstance(x, list):
        return [rational(y) for y in x]
    if isinstance(x, str):
        try:
            return Q(x)
        except ValueError:
            return x
    return x

def verify_sources():
    source_file = HERE / 'SOURCE.json'
    if not source_file.exists():
        return
    manifest = json.loads(source_file.read_text())
    for name, digest in manifest['files'].items():
        target = ROOT / name
        assert target.exists(), f'Missing source file: {name}'
        assert sha256(target.read_bytes()).hexdigest() == digest, f'Digest mismatch on {name}'

def exact(certificate=None):
    raw = certificate or json.loads((HERE / 'certificate.json').read_text())
    c = rational(raw)
    
    # 1. Verify reclaimed bit profile
    import reclaim_engine
    profile = reclaim_engine.generate_reclaimed_profile(c['roles_reclaimed'])
    m, W = profile['m'], profile['W']
    rows = profile['child_multiplicities']
    assert (m, W) == (c['bit']['m'], c['bit']['W'])
    assert profile['total_rank'] == c['bit']['total_rank']
    assert profile['deficit'] == c['bit']['deficit']
    
    # 2. Check exact moment enclosures for bit network
    grid = Q(1, 10**18)
    a_bit = c['bit']['saving']
    accepted = moments.exact_moment(m, W, rows, a_bit)
    rejected = moments.exact_moment(m, W, rows, a_bit + grid)
    assert accepted['upper'] < 1 < rejected['lower'], 'Moment enclosure failed'
    assert js(accepted) == raw['bit']['moment']
    assert js(rejected['lower']) == raw['bit']['rejected_lower']
    
    profile_dict = dict(m=m, W=W, child_multiplicities=rows)
    independent = moments.independent_moment(profile_dict, a_bit, js(accepted['terms']))
    negative = moments.independent_moment(profile_dict, a_bit + grid, js(rejected['terms']))
    assert independent[1] < 1 < negative[0], 'Independent audit enclosure failed'
    
    # 3. Check balanced layout assembly
    bridge = c['balanced_interface']['bridge']
    balanced.validate_bridge(bridge)
    
    a_c = c['complex']['saving']
    eta = Q(1, 10**12)
    beta = Q(1, 25)
    kappa = c['balanced_interface']['kappa']
    
    # Strict complex ceiling check
    assert (1 - beta) * a_c > a_bit, 'Complex ceiling violated'
    
    res = balanced.assembly(bridge, a_bit, kappa, beta=beta, h=eta, a_complex=a_c)
    assert js(res) == raw['balanced_interface']['assembly']
    assert js(balanced.cutoffs(bridge, res)) == raw['balanced_interface']['eventual_bounds']
    
    assert len(res['constraints']) == 47 and len(res['margins']) == 7
    assert all(x > 0 for x in res['constraints'].values()), 'Assembly inequality failed'
    assert all(x > kappa for x in res['margins'].values()), 'Margin constraint failed'
    
    # Negative control: adjacent grid point MUST be rejected
    try:
        balanced.assembly(bridge, a_bit, kappa + grid, beta=beta, h=eta, a_complex=a_c)
    except balanced.InvalidAssembly:
        pass
    else:
        raise AssertionError('Next grid point accepted!')
    
    assert kappa > c['pr100'], 'Did not strictly exceed PR #100'
    print(f"PASS two independent complete moments; balanced kappa {kappa} > 7.0e-5; 47 constraints, seven margins and next grids", flush=True)
    return res

if __name__ == '__main__':
    verify_sources()
    exact()
