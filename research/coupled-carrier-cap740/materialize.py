#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Materialize the new 145-row exchange using Petalas's streaming JSON format."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
from common import authenticate, context, need, sha, witness


def write_fill(path, rows):
    """Streaming format retained from Nick Petalas's PR3030 materializer."""
    need(len(rows) == 2717280, 'complete materialized role count')
    header = {'columns': ['time', 'helper', 'owner_replica', 'child', 'port', 'offset'],
              'dispatch_overrides': []}
    prefix = json.dumps(header, sort_keys=True, separators=(',', ':'))[:-1] + ',"rows":['
    payload = hashlib.sha256()
    count = 0
    with path.open('wb') as raw, gzip.GzipFile(
        filename='', mode='wb', fileobj=raw, compresslevel=1, mtime=0
    ) as out:
        data = prefix.encode(); out.write(data); payload.update(data)
        for count, row in enumerate(rows, 1):
            need(count <= 2717280, 'materialization iteration bound')
            data = ((',' if count > 1 else '')+json.dumps(row, separators=(',', ':'))).encode()
            out.write(data); payload.update(data)
        out.write(b']}\n'); payload.update(b']}\n')
    need(count == 2717280, 'no omitted materialized role')
    return dict(sha256=sha(path), payload_sha256=payload.hexdigest(), rows=count)


def build(directory):
    authenticate()
    rows, order, dispatch, _ = witness(context())
    made = write_fill(directory/'COMPOSED-FILL.json.gz', rows)
    for name, data in [('ORDER.json', order),
                       ('DISPATCH.json', [[s, r, dispatch[s, r]] for s, r in order])]:
        (directory/name).write_text(json.dumps(data, separators=(',', ':'))+'\n')
    made.update(order_sha256=sha(directory/'ORDER.json'),
                dispatch_sha256=sha(directory/'DISPATCH.json'))
    (directory/'MATERIALIZED.json').write_text(json.dumps(made, indent=2, sort_keys=True)+'\n')
    return made


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    print(json.dumps(build(args.output), indent=2, sort_keys=True))
