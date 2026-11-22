# SPDX-License-Identifier: Apache-2.0
"""Replay the saturated chart-1 input cut on Ali Romman's #8027 tape and #8036 lists."""
from collections import Counter
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from carrier_invariant import EXPANDED_SHA, SHA, forward, rank, tape


def report(path):
    path = path / 'strong-bit.json.gz' if path.is_dir() else path
    packed = path.read_bytes()
    unpacked = decompress(packed)
    assert sha256(packed).hexdigest() == SHA and sha256(unpacked).hexdigest() == EXPANDED_SHA
    word = json.loads(unpacked)
    top = [i for i,chart in enumerate(word['final']) if chart == 1]
    classes = Counter(('first_rail' if i < 111 else 'second_rail' if i < 222 else 'helper',
                       word['frames'][str(word['start'][i])]['dim']) for i in top)
    assert classes == {('first_rail',1):111, ('helper',0):391, ('helper',4):3}
    arrivals = [row for row in word['program'] if row[0] == 'MOVE' and row[3] == 1]
    ranks = Counter(8-word['frames'][str(row[2])]['dim'] for row in arrivals)
    assert word['start'].count(1) == 0 and len(top) == len(arrivals) == 505
    assert ranks == {1:323, 2:180, 4:2}
    assert not any(row[0]=='MOVE' and row[2]==1 for row in word['program'])
    native, _, _, native_history = forward(word,tape(word,None))
    assert rank(native[i] for i in top) == rank(native_history) == len(top)
    results = {}
    for missing in (None, 'a', 'b'):
        instructions = tape(word,missing)
        count = sum(row[0]=='MOVE' and row[3]==1 for _,row in instructions)
        rows, _, _, history = forward(word,instructions,noise=True)
        target_rank = rank(rows[i] for i in top)
        history_rank = rank(history)
        merged_rank = rank(rows+history)
        expected_top = 505 - int(missing is not None)
        expected_full = 630 - int(missing is not None)
        assert count == target_rank == history_rank == expected_top
        assert rank(rows) == merged_rank == expected_full
        results['original' if missing is None else 'omit_'+missing] = {
            'incoming_moves':count, 'formal_top_public_rank':target_rank,
            'formal_top_history_rank':history_rank, 'formal_public_and_top_history_rank':merged_rank}
    return {'source_sha256':SHA, 'initial_top_fields':0, 'prescribed_top_output_rank':len(top),
            'original_ingress_by_paid_rank':dict(ranks), 'replays':results}


if __name__ == '__main__':
    print(json.dumps(report(Path(sys.argv[1])), sort_keys=True, indent=2))
