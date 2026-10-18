#!/usr/bin/env python3
"""Refresh derived joint/pair validation bindings omitted by production commit 73cc66d0.

Only the exact known old receipts and current composition certificates are
admitted. Every proof-relevant receipt byte is preserved; only the derived
certificate_sha256 or local replay-source binding changes. This is metadata
regeneration, not a replay. Run make verify-joint and make verify-pair afterward
to regenerate all three complete receipts and retain CI's exact clean-tree gate. Frozen source archives/manifests are not edited.
Credit Chafik Boukhalfa's verifier/certificates, Aaron Wang's containment scan,
and Wentao Li's production integration. Dennis, with OpenAI Codex; Apache-2.0.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# name, exact old receipt, exact current certificate, exact regenerated receipt
CASES = (
    ('joint-dual',
     'c95cb1d65bdfa9b2b501153c7f24d5007b95f712d8f8ed8e88f262d9dcaaac01',
     'c58269050eb946c1512c974a0111321a2d92747d28dbc1a93ba9dfd4d40c74d9',
     '2d0f764e15a4609f8072d057c7c788ebe640bb9956b1f04e8ab761a43285a0f5'),
    ('skip-frame',
     '29062e44d551124fbf961b49a77f4229901fc206bb142571497ca43e88f4b47c',
     '5d377638225148cdef1fbbdc67d97e500d7242b1702e40f9b89af7f6a315efba',
     'b1bcef62cac69216f6fe9acc53c45b167c5c4c0d6449a15b0acafd0c84cb01da'),
)


PAIR_PATH = 'research/pair-assembly/frame/frame-certificate.json'
PAIR_SOURCE = 'scripts/experiments/binary_frame_replay.py'
PAIR_OLD_SOURCE = '1a572dbb33faba6695b3293768a7e61392d11cb4c2d5f708eedcd2cb95d0aff9'
PAIR_SOURCE_SHA256 = 'a1cbab2900440baa9b32f482f1531518fd95d55de2fe30e40e7a5249420b33a0'
PAIR_OLD_RECEIPT = 'eb5e8d25c4404703cc968acb4cc4642555ae56c3e93c1bb6a1e073fad72294e6'
PAIR_NEW_RECEIPT = '003b37ad28404d1afb0b01d1ab006f9dc03f72682728bc892883bbe1b1101cd1'


def refresh(root=ROOT, write=False):
    outputs = []
    for name, old_receipt, certificate, new_receipt in CASES:
        folder = root / 'certificates'
        if sha256((folder / (name + '-kappa.json')).read_bytes()).hexdigest() != certificate:
            raise ValueError('Unrecognized composition certificate: ' + name)
        target = folder / (name + '-validation.json')
        raw = target.read_bytes()
        digest = sha256(raw).hexdigest()
        if digest not in (old_receipt, new_receipt):
            raise ValueError('Unrecognized validation receipt: ' + name)
        old = json.loads(raw)['certificate_sha256'].encode('ascii')
        if raw.count(old) != 1:
            raise ValueError('Ambiguous certificate binding: ' + name)
        regenerated = raw.replace(old, certificate.encode('ascii'))
        if sha256(regenerated).hexdigest() != new_receipt:
            raise ValueError('Unexpected regenerated receipt: ' + name)
        if not write and raw != regenerated:
            raise ValueError('Stale derived binding: ' + name + '; use --write then make verify-joint')
        outputs.append((target, regenerated))
    # The same production update also omitted the pair-frame replay-source pin.
    if sha256((root / PAIR_SOURCE).read_bytes()).hexdigest() != PAIR_SOURCE_SHA256:
        raise ValueError('Unrecognized pair replay source')
    target = root / PAIR_PATH
    raw = target.read_bytes()
    digest = sha256(raw).hexdigest()
    if digest not in (PAIR_OLD_RECEIPT, PAIR_NEW_RECEIPT):
        raise ValueError('Unrecognized pair-frame receipt')
    regenerated = raw if digest == PAIR_NEW_RECEIPT else raw.replace(
        PAIR_OLD_SOURCE.encode('ascii'), PAIR_SOURCE_SHA256.encode('ascii'))
    if sha256(regenerated).hexdigest() != PAIR_NEW_RECEIPT:
        raise ValueError('Unexpected regenerated pair-frame receipt')
    if not write and raw != regenerated:
        raise ValueError('Stale pair-frame binding; use --write then make verify-pair')
    outputs.append((target, regenerated))
    # Authenticate every case before changing any output.
    if write:
        for target, raw in outputs:
            target.write_bytes(raw)
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    refresh(write=args.write)
    print('PASS exact joint/skip/pair validation bindings; full mathematical replay is separate')


if __name__ == '__main__':
    main()
