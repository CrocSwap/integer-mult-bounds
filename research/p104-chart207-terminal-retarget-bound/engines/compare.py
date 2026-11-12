"""Compare both terminal coframe closure receipts."""
from argparse import ArgumentParser
from hashlib import sha256
from json import dumps, loads
from pathlib import Path

PINS = {
    'inputs/R136-LEAD-RESULT.json': 'df42aba453a35097d87933dbad69e829baaa6fafeb35b56712fb631352eaebe2',
    'RESULT.json': 'e2298f10dd9c23a4efb249f8d5a5f9763389885b8c1bf7ac2781b7dae2c929a8',
}


def unique(items):
    out = dict(items)
    if len(out) != len(items):
        raise ValueError('duplicate JSON key')
    return out


def main():
    assert __debug__
    cli = ArgumentParser(description=__doc__)
    cli.add_argument('--root', type=Path, default=Path(__file__).resolve().parent)
    args = cli.parse_args()
    receipts = []
    for path,digest in PINS.items():
        raw = (args.root/path).read_bytes()
        assert sha256(raw).hexdigest() == digest, ('changed receipt',path)
        receipts.append(loads(raw, object_pairs_hook=unique))
    lead,independent = receipts
    fields = ('head','caller','anchors','edges','unary','survivors','unresolved')
    for key in fields:
        assert lead[key] == independent[key], key
    stripped = [{k:v for k,v in r.items() if k != 'first_exterior_reason'} for r in independent['groups']]
    assert stripped == lead['groups']
    clock,before,after = independent['protected_role319_last_move']
    assert lead['excluded_anchor'] == [clock,['MOVE',319,before,after,False]]
    assert lead['first_unvisited_event'] is independent['progress']['first_unvisited_reverse_event'] is None
    assert independent['roles_visited'] == 615 and independent['progress']['events_visited'] == 76466
    print(dumps({'agreement':True,'pins':PINS,'roles':615,'literal_events':76466,
                 'terminal_anchors':len(lead['anchors']),'survivors':lead['survivors'],
                 'unary_recharts':lead['unary'],'external_contacts':sum(g['exterior_event_count'] for g in stripped),
                 'first_external':[g['first_exterior'] for g in stripped]},indent=2,sort_keys=True))


if __name__ == '__main__':
    main()
