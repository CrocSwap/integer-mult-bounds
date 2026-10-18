# SPDX-License-Identifier: Apache-2.0
"""Parameterize only the replication-dependent PR870 checker cardinalities.

The literal edit table records each before/after string and expected count.
Constants unrelated to replicas, including 144 factors per wrapper and the
scalar adapter multiplier 16, are unchanged. Source notices are preserved.
"""
import argparse
import shutil
from common import HERE, read, require, sha, dump


def materialize(out):
    source = HERE/'vendor/pr870'
    pins = read(HERE/'VENDOR-PINS.json')['pr870']['files']
    edits = read(HERE/'data/ADAPTER-EDITS.json')
    require(not out.exists(), 'Runtime output must be new')
    (out/'code').mkdir(parents=True)
    receipt = {}
    for path in sorted((source/'code').glob('*.py')):
        relative = 'code/'+path.name
        require(sha(path) == pins[relative], 'Vendored source pin: '+relative)
        text = path.read_text()
        for before, after, count in edits.get(path.name, []):
            require(text.count(before) == count, 'Exact edit multiplicity: '+path.name+' '+before)
            text = text.replace(before, after)
        target = out/'code'/path.name
        target.write_text(text)
        receipt[path.name] = dict(source_sha256=pins[relative], output_sha256=sha(target),
                                  edits=edits.get(path.name, []))
    shutil.copytree(source/'inputs', out/'inputs')
    dump(out/'ADAPTERS.json', receipt)
    return receipt


if __name__ == '__main__':
    from pathlib import Path
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('out', type=Path)
    materialize(parser.parse_args().out)
