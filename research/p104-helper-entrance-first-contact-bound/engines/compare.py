"""Reconcile the two full first-contact receipts and check all proper prefixes."""

from argparse import ArgumentParser
from collections import Counter
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path

WORD_SHA = 'c404b9b61220e6cf740d85276df2828bbb4a9d68a4d44b5e283f8d96f78c0fd9'
LABEL = {
    'excluded_role': 'excluded_comparator_role',
    'first_contact_not_move': 'first_contact_not_move',
    'move_rank_or_nesting': 'first_move_not_rank_one',
    'rank_one_target': 'zero_residual_rank',
}


def compare(root):
    a = loads((root/'CONTACT.json').read_bytes())
    b = loads((root/'independent/RESULT.json').read_bytes())
    price = sha256((root/'PRICE.json').read_bytes()).hexdigest()
    assert a['price_sha256'] == b['price_sha256'] == price
    raw = (root/'inputs/7314/WORD.json.gz').read_bytes()
    assert sha256(raw).hexdigest() == a['word_sha256'] == WORD_SHA
    word = loads(decompress(raw))
    tape, frames = word['program'], word['frames']
    assert a['events'] == b['visited_events'] == len(tape) == 76461
    assert not any((a['unvisited_roles'], b['remaining_roles'], a['survivors'], b['survivors']))
    ar = {row['role']:row for row in a['rows']}
    br = {row['role']:row for row in b['rows']}
    assert set(ar) == set(br) and len(ar) == len(a['rows']) == len(b['rows']) == 1101
    proper = []
    full = []
    for role,row in ar.items():
        other = br[role]
        assert LABEL[row['status']] == other['status']
        assert (row['initial'],row['final'],row['rank']) == (
            other['initial'],other['final'],other['old_productive_rank'])
        clock,op,access,*charts = row['first']
        access = {'SCALE':'unary','MOVE':'move'}.get(op,access)
        assert (clock,access,tape[clock]) == (
            other['first_clock'],other['first_access'],other['first_event'])
        assert tape[clock][0] == op
        if op != 'MOVE' or row['status'] == 'excluded_role':
            continue
        src,dst = charts
        target = row['final']
        assert src == row['initial']
        moved = len(frames[dst])-len(frames[src])
        residual = len(frames[target])-len(frames[dst])
        record = {'role':role,'clock':clock,'start':src,'first_dest':dst,'end':target,
                  'paid_rank':moved,'residual_rank':residual}
        if moved > 0 and dst == target:
            full.append(record)
        else:
            proper.append(record)
    assert len(full) == 10 and not proper
    return {'head':a['head'],'price_sha256':price,'roles_compared':len(ar),
            'events':len(tape),'status_counts':dict(Counter(r['status'] for r in ar.values())),
            'all_nonexcluded_first_moves':full,'proper_first_moves_any_positive_rank':proper,
            'support_saving_upper':0,'unresolved':0}


if __name__ == '__main__':
    parser=ArgumentParser(description=__doc__)
    parser.add_argument('root',type=Path)
    args=parser.parse_args()
    print(dumps(compare(args.root),indent=2,sort_keys=True))
