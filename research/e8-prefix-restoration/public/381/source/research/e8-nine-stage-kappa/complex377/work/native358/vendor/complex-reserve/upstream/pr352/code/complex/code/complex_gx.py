"""Exact scalar-identity admission of the pinned complex gcert/1 program.

The complex coarse saving is load-bearing in this package, so the complex stage now checks the complex program
itself. It runs two of Jacob Sussman's checkers, both vendored byte-identical from jacobalansussman/
wht-power-saving-lean at f010392c923279e3dd59ef3aa5fedad23affc5fd (Apache-2.0, Copyright 2026 Jacob Sussman) in
inputs/complex/sources and sha-checked here:

- the reference checker gx.check1(scalar=True): sizes, labels, scatter cut, shape, bracket rule, the exact
  scalar identity (E5: every x role restored and every target receives exactly its source), block histograms,
  N, and the exterior-gauge rule Q2;
- the gxcore Python mirror of his two Lean checks (labels and scalars).

The mirror's block histogram must equal the program's. Controls: one flipped scalar sign in a phase-A gate must
be rejected by both checkers on the scalar identity (E5). This is a Python check. It is not a Lean run, and no
Lean check of the program is pinned here. The run takes about 30 seconds.
Prepared by DreamingOfClouds with Anthropic Claude assistance; Apache-2.0.
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import importlib.util, json, time

GX = ('inputs/complex/sources/tools__gx__gx.py', '6f3dc8bb639933227a8dae181ec4a542e85c7276be9c9e330f49518e7b630b95')
GXCORE = ('inputs/complex/sources/tools__gx__gxcore.py', 'eb972c06fe8c322db2d9a8d9a7d05596e8f40c4ca8e5f42eb6df3c7361b5d517')


def _load(root, name, pin):
    path = Path(root) / pin[0]
    assert sha256(path.read_bytes()).hexdigest() == pin[1], 'vendored Sussman checker changed: ' + pin[0]
    spec = importlib.util.spec_from_file_location('complex_' + name, path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def _flip_one_sign(cert):
    """Negate the first coefficient of the first phase-A add gate with a coefficient list."""
    gate = next(g for g in cert['A'] if g[0] in ('out', 'in') and g[3])
    t, a, b = gate[3][0]
    gate[3][0] = [t, -a, b]
    return cert


def check(root, raw):
    """raw: the uncompressed gcert/1 bytes, already bound to source-pins.json by the caller."""
    begun = time.monotonic()
    gx = _load(root, 'gx', GX); gxcore = _load(root, 'gxcore', GXCORE)
    cert = json.loads(raw); stats = {}
    assert gx.check1(cert, scalar=True, stats=stats) is True
    blocks = Counter()
    for w in cert['blocks'].values():
        for r, n in w.items():
            blocks[int(r)] += n
    mirror = gxcore.mirror(gxcore.normal(json.loads(raw)))
    assert mirror['hist'] == dict(blocks), 'gxcore histogram differs from the blocks'
    controls = []
    try:
        gx.check1(_flip_one_sign(json.loads(raw)), scalar=True)
    except AssertionError as error:
        assert str(error).startswith('E5'), ('flipped sign rejected for the wrong reason', str(error))
        controls.append(dict(name='flipped_scalar_sign', checker='gx.check1', reason=str(error)))
    else:
        raise AssertionError('gx.check1 accepted a flipped scalar sign')
    try:
        gxcore.mirror(gxcore.normal(_flip_one_sign(json.loads(raw))))
    except gxcore.Reject as error:
        assert str(error).startswith('E5'), ('flipped sign rejected for the wrong reason', str(error))
        controls.append(dict(name='flipped_scalar_sign', checker='gxcore.mirror', reason=str(error)))
    else:
        raise AssertionError('gxcore mirror accepted a flipped scalar sign')
    return dict(status='PASS_COMPLEX_PROGRAM_GX_CHECK1_SCALAR_AND_GXCORE_MIRROR',
                gx_check1='ACCEPTED (labels, blocks, N, exact scalar identity E5, Q2)',
                gxcore_mirror='ACCEPTED (label and scalar checks; histogram equals the blocks)',
                scalar_denominators=stats['den'], scalar_max_abs=stats['maxabs'], distinct_frame_steps=stats['steps'],
                blocks_total=sum(blocks.values()), gates_A=len(cert['A']), gates_B=len(cert['B']),
                certificate_sha256=sha256(raw).hexdigest(), gx_sha256=GX[1], gxcore_sha256=GXCORE[1],
                controls=controls, lean='not run here; no Lean check of this program is pinned in this package',
                seconds=time.monotonic() - begun)
