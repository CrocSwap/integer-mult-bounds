#!/usr/bin/env python3
"""Incremental whole-projector accounting for the pinned PR97 physical word.

Copyright 2026 icekylinx. Apache-2.0. Prepared with OpenAI Codex assistance.
PR97's reflected physical ledger is by Zhihao Chen; its frozen scalar/frame
witness is Swapnil Jain's round-seven construction. Original licenses, proof
boundaries, source notices and assistance disclosures remain in the snapshots.

This reconstructs the new profile from physical frame chains and their frozen
ledger receipt. It does not repeat the unchanged complete-basis scalar replay
or exact rational frame/lifted checks, and does not infer nesting from ranks.
"""
import argparse
from collections import Counter
import gzip
from hashlib import sha256
import importlib.util
import json
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'certificates/partial-gauge-bit-input.json'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def encoded(histogram):
    return {str(rank): count for rank, count in sorted(histogram.items()) if count}


def frozen_sources(record):
    manifest_path = ROOT / record['source_manifest']
    require(sha256(manifest_path.read_bytes()).hexdigest() == record['source_manifest_sha256'],
            'PR97 provenance manifest changed')
    manifest = json.loads(manifest_path.read_text())
    for name, digest in manifest['sha256'].items():
        require(sha256((manifest_path.parent/name).read_bytes()).hexdigest() == digest,
                'Pinned PR97 source changed: '+name)
    require(manifest['pr97']['commit'] == 'e15350b66e4bf796153a68c240a6cc1b788abe3e',
            'Unexpected PR97 commit')
    require(manifest['underlying']['commit'] == '741e7aa078392553815df7926ee17ac5e25a8c38',
            'Unexpected underlying witness commit')
    return manifest_path.parent, manifest


def local_ranks(folder):
    """Read actual role paths; reconstruct nonzero rank increments.

    Auxiliary chains are the same physical chains used by the reflected
    ledger. Target paths follow readout_order and retain only odd coefficients
    of the exact adjoint, as the actual F2 physical word does. X paths use the
    frozen per-leaf V order. Center moves are one rank-(h-1) copy per retained
    center. No inner-corner splitting is applied at this stage.
    """
    spec = importlib.util.spec_from_file_location('pinned_pr97_deferred', folder/'deferred.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with gzip.open(folder/'witness_23.json.gz', 'rt') as stream:
        witness = json.load(stream)
    with gzip.open(folder/'deferred_23.json.gz', 'rt') as stream:
        data = json.load(stream)
    require(witness['h'] == data['h'] == 23, 'Witness dimension mismatch')
    schedule = module.Schedule(witness, data)
    h, v, roles = schedule.h, schedule.v, schedule.R
    require(v == comb(h, 3), 'Witness source count mismatch')
    require(len(schedule.ret) == h and set(schedule.ret.values()) == set(range(h)),
            'Retained centers differ')
    require(len(schedule.readout) == len(set(schedule.readout)), 'Duplicate readout role')
    require(len(schedule.sigma) == len(schedule.readout), 'Readout bases mismatch')
    require(all(0 <= slot < roles for slot in schedule.readout), 'Readout role out of range')
    aux = module.chain_ranks(schedule)
    xhist = Counter(rank for path in schedule.xdata() for rank in path if rank)
    require(all(0 < rank <= h for rank in xhist), 'Invalid source path increment')
    adjoint = schedule.adjoint()
    current = [0] * v
    yhist = Counter()
    for slot in schedule.readout:
        rank = schedule.f[slot]
        for target, coefficient in adjoint[slot].items():
            if coefficient & 1:
                increment = rank-current[target]
                require(increment >= 0, 'Target physical path retreats')
                if increment:
                    yhist[increment] += 1
                current[target] = rank
    for rank in current:
        require(rank <= h-1, 'Target frame exceeds its output hyperplane')
        if rank < h-1:
            yhist[h-1-rank] += 1
    local = dict(aux=aux, data=xhist+yhist, center=Counter({h-1: len(schedule.ret)}))
    require(sum(r*n for r,n in local['data'].items()) == 2*v*(h-1),
            'Physical data path rank mass mismatch')
    exits = Counter(h-rank for rank in schedule.f)
    require(all(0 < rank <= h for rank in exits), 'Invalid physical exit nullity')
    require(sum(exits.values()) == roles, 'Missing physical exit')
    return h, v, roles, local, exits


def reconstruct(input_path=INPUT):
    record = json.loads(Path(input_path).read_text())
    folder, sources = frozen_sources(record)
    ledger = json.loads((folder/'bit-ledger-result.json').read_text())
    for flag in ('complete_forward_F2', 'complete_reflected_F2',
                 'reflected_frame_continuity', 'all_scalar_gates_equal_frame_keys',
                 'histogram_matches_external'):
        require(ledger[flag] is True, 'Pinned physical ledger lacks '+flag)
    h, v, roles, local, exits = local_ranks(folder)
    require((ledger['h'], ledger['roles'], ledger['formal_basis']) == (h, roles, 2*v+roles),
            'Physical ledger dimensions differ')
    require({kind: encoded(hist) for kind,hist in local.items()} == ledger['rank_histograms'],
            'Reconstructed physical ranks differ from the pinned reflected ledger')
    m, N = h*h, v*v
    W = 2*N+2*v*roles
    whole = Counter()
    for hist in local.values():
        for rank, count in hist.items():
            whole[rank] += 2*v*count
    # Each role's exterior I-(I-sigma) tensor Q has rank m-(h-dim sigma).
    for nullity, count in exits.items():
        whole[m-nullity] += 2*v*count
    # The original entrance projector is one rank-(h-1)^2 edge per bank pair.
    whole[(h-1)**2] += 2*N
    whole[1] += N  # physical copy correction
    mass = sum(rank*count for rank,count in whole.items())
    require(mass == ledger['recursive_rank'], 'Whole-projector rank mass changed')
    require(all(0 < rank < m and count > 0 for rank,count in whole.items()),
            'Invalid whole-projector child')
    result = dict(dimensions=[h,h], m=m, v=v, N=N, R=roles, W=W,
                  rank_mass=mass, deficit=W*m-mass, max_child=max(whole),
                  local_rank_histograms={kind: encoded(hist) for kind,hist in local.items()},
                  exit_nullity_histogram=encoded(exits),
                  whole_projector_histogram=encoded(whole))
    for key, value in result.items():
        require(value == record[key], 'Round-six expected profile differs: '+key)
    result['checks'] = dict(source_hashes_equal=True, physical_local_ranks_reconstructed=True,
                            physical_ledger_ranks_equal=True, whole_profile_equal=True,
                            full_upstream_audits_repeated=False)
    result['provenance'] = dict(pr97=sources['pr97'], underlying=sources['underlying'],
                                source_manifest=record['source_manifest'],
                                source_manifest_sha256=record['source_manifest_sha256'])
    result['scope'] = ('Incremental rank accounting from pinned physical chains and ledger; '
                       'scalar complete-basis replay and rational geometry remain inherited checks.')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=INPUT)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = reconstruct(args.input)
    text = json.dumps(result, indent=2, sort_keys=True)+'\n'
    if args.output:
        args.output.write_text(text)
    else:
        print(text, end='')


if __name__ == '__main__':
    main()
