"""Replay endpoint constructions and invoices against their frozen receipts."""
from pathlib import Path
import argparse
import hashlib
import json
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'paid-controller'))
from portable import PACKAGE, replay_scripts, require, workspace_path

CASES = (
    ('clique_word.py', 'CLIQUE-WORD.json'),
    ('fused_clique_word.py', 'FUSED-CLIQUE-WORD.json'),
    ('hybrid_bound.py', 'HYBRID-BOUND.json'),
    ('native_tensor_price.py', 'NATIVE-TENSOR-PRICE.json'),
    ('tensor_price.py', 'TENSOR-PRICE.json'),
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, help='External output directory; temporary by default')
    parser.add_argument('--normal', action='store_true', help='Use -I without -O for child scripts')
    args = parser.parse_args()
    directory = Path(__file__).resolve().parent
    sources = json.loads((directory / 'sources/SOURCES.json').read_text())
    for name, source in sources.items():
        require(hashlib.sha256((directory / 'sources' / name).read_bytes()).hexdigest()
                == source['sha256'], f'Pinned upstream bytes: {name}')
    source = json.loads((directory / 'HYBRID-BOUND.json').read_text())['source']
    require(hashlib.sha256((PACKAGE / source['path']).read_bytes()).hexdigest()
            == source['sha256'], 'Pinned portable hybrid-bound dependency')
    workspace = workspace_path(args.workspace)
    rows = replay_scripts(directory, CASES, workspace, optimized=not args.normal)
    result = dict(status='PASS_ENDPOINT_COSTS_PORTABLE', cases=rows,
                  scope='Exact scalar/frame subwords and inherited-profile invoices. No fresh upstream supplier replay or exponent claim.')
    path = workspace / 'continuation/endpoint-costs/PORTABLE-REPLAY.json'
    path.write_text(json.dumps(result, indent=2) + '\n')
    print(f'Receipts and logs: {workspace}')


if __name__ == '__main__':
    main()
