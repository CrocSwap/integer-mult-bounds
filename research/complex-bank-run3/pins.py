#!/usr/bin/env python3
"""The bytes this package is allowed to depend on.

Two sources are pinned: #207's frontier certificate (the row pair the ladder is priced
against, taken verbatim from that submission's head) and the whole of #219's rung-1
package under `references/pr219-run1/`, which supplies rung 1 itself, the interval-moment
engine and the 47-constraint assembly.  A third upstream certificate is pinned on its own --
#233's source-assisted v4 layer, the *new row* the rank-3 rung is priced on, whose branch is
unmerged and whose head (`109a857`) is therefore pinned by digest rather than trusted.
The earlier heads of that same branch are pinned as well
(`references/pr233-heads/`), because the rank-3 rung's stability is measured against them:
a measurement that had to re-fetch a branch could not be re-run in a clone.
Everything else in this directory is the work of this package, including all three export
contracts: the complex side's own, the bit side's twin, and the rank-3 rung's.  The bit
drop's bodies are pinned too -- they are the bytes behind digests the pinned certificates
publish, and `verify.py` re-hashes every one of them against its anchor.
"""
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
VENDORED_RUN1 = 'references/pr219-run1'
BIT_DROP = 'exports-bit'
HEAD_ROWS = 'references/pr233-heads'

OWN = ('ledger3.py', 'run3.py', 'schedule66.py', 'schedule66.json', 'prototype66.py',
       'widths66.py', 'suppliers.py', 'instantiate66.py', 'importer66.py',
       'occurrences66.json', 'pins.py',
       'obligations.json', 'EXPORT-CONTRACT.md', 'export-contract.json',
       'EXPORT-CONTRACT-BIT.md', 'export-contract-bit.json',
       'bitindex.py', 'bitcontract.py', 'bit-drop-report.json',
       'instantiate_rank3.py', 'rank3contract.py', 'occurrences-rank3.json',
       'EXPORT-CONTRACT-RANK3.md', 'export-contract-rank3.json',
       'rank3stability.py', 'rank3-stability.json',
       'rank4rung.py', 'rank4-rung.json',
       'bitrung.py', 'bitrung.json', 'bitinstance.py', 'occurrences-bitrung.json',
       'references/pr207-coordinated-crossover.certificate.json',
       'references/pr233-source-assisted-v4-layer.certificate.json')


def pinned_paths():
    """Every file whose bytes this package is pinned to, as relative paths."""
    own = list(OWN)
    vendored = sorted(str(p.relative_to(HERE)).replace('\\', '/')
                      for p in (HERE / VENDORED_RUN1).rglob('*') if p.is_file())
    assert vendored, 'the vendored rung-1 package must be present'
    drop = sorted(str(p.relative_to(HERE)).replace('\\', '/')
                  for p in (HERE / BIT_DROP).rglob('*') if p.is_file())
    assert drop, 'the bit drop must be present: it holds the bodies behind the published digests'
    heads = sorted(str(p.relative_to(HERE)).replace('\\', '/')
                   for p in (HERE / HEAD_ROWS).rglob('*') if p.is_file())
    assert heads, 'the ranked heads of #233 must be present: the stability measurement is theirs'
    return own + vendored + drop + heads


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def manifest():
    return {name: digest(HERE / name) for name in pinned_paths()}
