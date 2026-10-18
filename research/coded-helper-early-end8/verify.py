"""Fresh eight-word native replay and complete four-variant packing screen."""
import gzip
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import comb
import os
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from construct import read, require, encode
from model import build, BASE
from packing import verify as price
from binomial import power_bounds, SCALE


def check_sources():
    pins = read(HERE / 'SOURCES.json')
    for name, expected in pins['repo_inputs'].items():
        require(sha256((ROOT / name).read_bytes()).hexdigest() == expected, 'Repository source drift: ' + name)
    for name, expected in pins['vendor_inputs'].items():
        require(sha256((HERE / name).read_bytes()).hexdigest() == expected, 'Vendored source drift: ' + name)
    return pins


def execute(script, arguments, log, env):
    with log.open('w', encoding='utf-8') as stream:
        result = subprocess.run([sys.executable, '-I', '-B', str(script), *map(str, arguments)],
                                env=env, stdout=stream, stderr=subprocess.STDOUT)
    require(result.returncode == 0, 'Native replay failed: ' + str(log) + '\n' + log.read_text()[-2000:])


def run(out):
    pins = check_sources()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONINTMAXSTRDIGITS='0')
    env.pop('PYTHONOPTIMIZE', None)
    old = out / 'original9'; old.mkdir()
    base = ROOT / BASE
    route = base / 'vendor/multicold/vendor/pr558/vendor/pr552/complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz'
    auditor = ROOT / 'research/complex-sw4-frame8/local/hpe_audit_and_transport.py'
    execute(HERE / 'vendor/pr855/native_worker.py', [HERE / 'vendor/pr855', auditor, route, old], out / 'original9-worker.log', env)
    new = out / 'early8';new.mkdir()
    execute(HERE / 'native_worker.py', [new], out / 'early8-worker.log', env)
    original, retimed = read(old / 'NATIVE-RESULT.json'), read(new / 'NATIVE-RESULT.json')
    require(original['assertions_enabled'] is True and retimed['assertions_enabled'] is True, 'Native assertions')
    model = build(ROOT, original['receipts'], retimed['receipts'])
    packing = price(model, read(HERE / 'vendor/pr855/EXACT-CERTIFICATE.json'))
    require(packing['excluded'] is True, 'This certificate does not exclude the extended mixtures')
    # Independent exact positive controls for the new power engine, without
    # invoking either predecessor log/exp routine: r^(1-1/2)=sqrt(r).
    for rank in (0,1,2,3,7,8,9,48,73):
        low,high = power_bounds(rank,Q(1,2))
        require(low*low <= rank*SCALE*SCALE <= high*high, 'Binomial square-root identity')
    selected = read(HERE / 'CONTEXT-SELECTED.json')
    kappa = Q(selected['kappa'])
    necessary_b = kappa/(1-kappa)
    require(necessary_b > Q(model['endpoint']), 'Pinned current target does not exceed the excluded endpoint')
    result = dict(base=pins['base'], source_prs=[781,855], status='PASS_EARLY8_CONSTRUCTION_AND_EXTENDED_COST_OBSTRUCTION',
                  native_words=8, new_constructions=retimed['constructions'],
                  new_native_receipts=retimed['receipts'], original_native_controls=original['controls_rejected'],
                  original_recompression=original['recompression_control'],
                  model=model, packing=packing, nonempty_mixture_count=comb(76,4)-1,
                  current_target=dict(kappa=str(kappa),necessary_b=str(necessary_b),
                                      excluded_from_b=model['endpoint'],source_head=pins['base']),
                  scope='Four rank-eight variants plus four original rank-nine words; fixed PR626 geometry/dispatch; whole-helper packing relaxation. Native identities/frames only; no new phase/global admission or multiplication exponent.')
    return json.loads(json.dumps(result))


def main():
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', type=Path)
    p.add_argument('--write', action='store_true')
    a = p.parse_args()
    def finish(out):
        result = run(out)
        if a.write:
            (HERE / 'EXPECTED.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
        else:
            require(json.dumps(result, sort_keys=True) ==
                    json.dumps(read(HERE / 'EXPECTED.json'), sort_keys=True),
                    'Recomputed evidence differs')
        (out / 'RESULT.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
        print(result['status'], '8 native words;', result['nonempty_mixture_count'], 'mixtures excluded; no new kappa')
    if a.out:
        out = a.out.resolve()
        require(not out.exists() and not out.is_relative_to(HERE), 'Fresh external output required')
        out.mkdir(parents=True)
        finish(out)
    else:
        with tempfile.TemporaryDirectory(prefix='early8-replay-') as tmp:
            finish(Path(tmp))


if __name__ == '__main__':
    main()
