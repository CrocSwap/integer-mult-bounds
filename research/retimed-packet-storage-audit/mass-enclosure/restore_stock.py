"""Restore the frozen review's graph/layout through the original authenticated loader."""
from hashlib import sha256
from pathlib import Path
import argparse
import gc
import json
import sys
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ArithmeticError(message)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--runtime', type=Path, required=True)
    cli.add_argument('--output', type=Path, required=True)
    args = cli.parse_args()
    runtime, output = args.runtime.resolve(), args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    expected = json.loads((HERE / 'review/PRODUCTION-BINDING.json').read_text())
    data = (runtime / 'strong_complex.py').read_bytes()
    need(sha256(data).hexdigest() == expected['source_hashes']['strong_complex.py'],
         'original graph loader source differs')
    sys.path.insert(0, str(runtime))
    from upstream import install
    held = install()
    from strong_complex import load_changed
    graph, layout = load_changed(runtime / 'inputs')
    pins = json.loads((HERE / 'STOCK-BINDINGS.json').read_text())
    for name, value in (('graph.json', graph), ('layout.json', layout)):
        # This is the exact source digest serialization, with no added newline.
        raw = json.dumps(value, separators=(',', ':'), sort_keys=True).encode()
        pin = pins['files'][name]
        need(len(raw) == pin['size'] and sha256(raw).hexdigest() == pin['sha256'],
             'reconstructed stock differs: ' + name)
        (output / name).write_bytes(raw)
    for item in held:
        if hasattr(item, 'cleanup'):
            item.cleanup()
    for item in gc.get_objects():
        if isinstance(item, TemporaryDirectory):
            item.cleanup()
    result = {'status': 'PASS_AUTHENTICATED_MASS_REVIEW_STOCK',
              'source_commit': pins['source_commit'], 'files': pins['files'],
              'method': 'Unchanged strong_complex.load_changed and its authenticated journals'}
    (output / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
    print(result['status'], flush=True)


if __name__ == '__main__':
    main()
