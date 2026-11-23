"""Path-only replay of the frozen numerical and production mass reviewers."""
from hashlib import sha256
from pathlib import Path
import argparse
import json
import sys
import types

HERE = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ArithmeticError(message)


def frozen_module(name, path):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    # Preserve every assertion even when this adapter is invoked with -O.
    exec(compile(path.read_bytes(), str(path), 'exec', optimize=0), module.__dict__)
    return module


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--runtime', type=Path, required=True)
    cli.add_argument('--stock', type=Path, required=True)
    cli.add_argument('--output', type=Path, required=True)
    args = cli.parse_args()
    runtime, stock, output = args.runtime.resolve(), args.stock.resolve(), args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    pins = json.loads((HERE / 'FROZEN.json').read_text())
    for name, expected in pins.items():
        need(sha256((HERE / name).read_bytes()).hexdigest() == expected,
             'frozen reviewer changed: ' + name)
    expected_review = json.loads((HERE / 'EVIDENCE.json').read_text())
    proof = HERE.parent / 'PROOF.md'
    need(sha256(proof.read_bytes()).hexdigest() == expected_review['proof_sha256'],
         'proof differs from accepted review')
    need(sha256((runtime / 'transport.py').read_bytes()).hexdigest()
         == expected_review['source_sha256'], 'wrong mass source')
    expected_binding = json.loads((HERE / 'PRODUCTION-BINDING.json').read_text())
    stock_pins = json.loads((HERE.parent / 'STOCK-BINDINGS.json').read_text())
    for name, record in stock_pins['files'].items():
        data = (stock / name).read_bytes()
        need(len(data) == record['size'] and sha256(data).hexdigest() == record['sha256'],
             'stock artifact changed: ' + name)
    for name, expected in expected_binding['source_hashes'].items():
        need(sha256((runtime / name).read_bytes()).hexdigest() == expected,
             'production source changed: ' + name)
    numerical = frozen_module('frozen_mass_numerical_review', HERE / 'check_review.py')
    numerical.HERE = output
    previous_argv = sys.argv
    try:
        sys.argv = [str(HERE / 'check_review.py'), '--source', str(runtime / 'transport.py'),
                    '--proof', str(proof)]
        numerical.main()
    finally:
        sys.argv = previous_argv
    observed = json.loads((output / 'EVIDENCE.json').read_text())
    need(observed == expected_review, 'numerical receipt differs from accepted review')
    binding = frozen_module('frozen_mass_production_review', HERE / 'bind_production.py')
    binding.HERE, binding.RUNTIME, binding.STOCK = output, runtime, stock
    binding.main()
    observed_binding = json.loads((output / 'PRODUCTION-BINDING.json').read_text())
    need(observed_binding == expected_binding, 'production receipt differs from accepted review')
    result = {'status': 'PASS_PORTABLE_MASS_ENCLOSURE_REVIEW',
              'proof_sha256': expected_review['proof_sha256'],
              'source_sha256': expected_review['source_sha256'],
              'frozen_review_sha256': pins,
              'assertion_semantics': 'Both frozen reviewers compiled with optimize=0',
              'numerical_receipt_identical': True, 'production_receipt_identical': True,
              'scope': 'Path-only adaptation; no production-size calendar execution'}
    (output / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
    print(result['status'], flush=True)


if __name__ == '__main__':
    main()
