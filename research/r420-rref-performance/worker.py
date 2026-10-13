# SPDX-License-Identifier: Apache-2.0
"""Fresh-process workload; both engines execute the original finite checks."""
import argparse
import gzip
import json
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import adapter


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('engine', choices=('reference', 'integer'))
    parser.add_argument('suite', choices=('check', 'controls'))
    args = parser.parse_args()
    if args.suite == 'controls':
        path = adapter.SOURCE if args.engine == 'reference' else HERE / 'adapter.py'
        sys.argv = [str(adapter.MUTANTS), str(path), str(adapter.WORD)]
        runpy.run_path(str(adapter.MUTANTS), run_name='__main__')
    else:
        checker = adapter.load_checker(args.engine == 'integer')
        with gzip.open(adapter.WORD, 'rt') as source:
            word = json.load(source)
        obj, labels, replay, hypotheses, conclusion, info = checker.check(word)
        adapter.require(all(hypotheses.values()) and all(conclusion.values()), 'Interface failed')
        print(json.dumps(dict(labels=labels, replay=replay, hypotheses=hypotheses,
                              conclusion=conclusion, interleaving=info,
                              dimensions=obj.fdim, annihilators=obj.fperp), sort_keys=True))


if __name__ == '__main__':
    main()
