"""Optional regression of the generalized complex checks on PR #346's own p = 10 program.

usage: python3 -B regress_pr346.py <PR #346 checkout>/research/w3-p10b-complex-p10

Copies PR #346's code/ tree to a fresh temporary directory, overlays this package's generalized complex checks
(code/complex/portable_complex.py and code/complex/code/*.py, including scatter.py) and runs, against PR #346's own
certificate and pins-p10f.json, both the original and the generalized checks. Every regression pin of PR #346 must
hold, and the two runs must agree byte for byte on both scalar schedules, both splice programs, both primitive
expansions, the ledger and the precision guard; the generalized run only adds the keys 'centres' (ledger) and
'centre_ranks' (labels)."""
import importlib.util, os, shutil, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
src = os.path.abspath(sys.argv[1])


def run(root):
    os.environ['CX_PINS'] = os.path.join(root, 'pins-p10f.json')
    for m in ['p10pins', 'scatter', 'complex_labels', 'complex_scalars', 'complex_splice', 'complex_basis']:
        sys.modules.pop(m, None)
    sys.path.insert(0, os.path.join(root, 'code'))
    spec = importlib.util.spec_from_file_location('pc_' + str(abs(hash(root))), os.path.join(root, 'portable_complex.py'))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    try:
        return mod.run(package_root=root)
    finally:
        sys.path.pop(0)


tmp = tempfile.mkdtemp(prefix='regress346-')
shutil.copytree(os.path.join(src, 'code'), os.path.join(tmp, 'code'))
new = os.path.join(tmp, 'code', 'complex')
shutil.copy(os.path.join(HERE, 'portable_complex.py'), new)
for f in os.listdir(os.path.join(HERE, 'code')):
    if f.endswith('.py'):
        shutil.copy(os.path.join(HERE, 'code', f), os.path.join(new, 'code'))
a = run(os.path.join(src, 'code', 'complex'))
b = run(new)
for o in ['forward', 'backward']:
    assert a['scalar_bill'][o]['schedule_sha256'] == b['scalar_bill'][o]['schedule_sha256'], o
    for k in ['program_sha256', 'scalar_primitive_sha256', 'scalar_projection_sha256']:
        assert a['splice']['program'][o][k] == b['splice']['program'][o][k], (o, k)
assert a['precision_guard'] == b['precision_guard']
assert {k: v for k, v in b['ledger'].items() if k != 'centres'} == a['ledger']
assert {k: v for k, v in b['label_checks'].items() if k != 'centre_ranks'} == a['label_checks']
assert a['five_stage_histogram'] == b['five_stage_histogram']
shutil.rmtree(tmp)
print('PASS: on PR #346\'s p = 10 program the generalized complex checks reproduce every pin and the original '
      'scalar schedules, splice programs, primitive expansions, ledger, labels and precision guard byte for byte')
