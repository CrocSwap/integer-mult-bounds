"""Authenticate four initial intake observations after exact recorded revisions.

The mutable intake metadata describes the revised head. These receipts retain their original observations in immutable intake
evidence, including #4110 before its documented October 21 update. No Git access is
needed, including inside historical replay copies. This is an exact checkpoint
adapter: changed receipt bytes or another revision require explicit maintenance,
not a fallback to unverified ledger history. Future intake needs a durable pin
for each immutable initial observation.
"""
import hashlib
import json


INTAKE = 'docs/research/pr-intake-decisions.json'
RECEIPTS = {
    'queue-next-20261017': '6c5081877cc1c26bb758635a0ca2dfc2af4525744bd43dc6aaf79bdf67a9b183',
    'queue-tail-20261017': '1f5d355fe5fc44839f7ede91ce7f98691f1a87f1f9f856c7e057f00b98ad6249',
    'queue-refresh-20261017': '618a67ccba7857ba533da75742b01fa3e40020097b01ccb3e205c49b993e65b3',
    'queue-oct18-20261018': '9b8407cee0210bb30b193c8a1040aa14913de5405b496ca003ba279896c28e79',
    'queue-oct20f-20261020': '28751ed30182c5892e4569988a5ad8b931468c68c7d341a5bc2cbb22ee44191d',
    'queue-oct21a-20261021': 'd527aa1989ccffb02d33b1e5937606d8714440662ad5ac86bf1a22a9c137472f',
}
REVISIONS = {
    3107: ('queue-next-20261017', 'initial_archived_head', 'queue-next-20261017'),
    3184: ('queue-tail-20261017', 'previously_reviewed_head', 'queue-tail-20261017'),
    3251: ('queue-refresh-20261017', 'head', 'queue-oct18-20261018'),
    # #4110's reviewed October 21 successor changed the mutable intake head.
    4110: ('queue-oct20f-20261020', 'head', 'queue-oct21a-20261021'),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def initial_head_for_decision(root, family_path, decision):
    """Return an authenticated initial head without changing current metadata."""
    metadata = decision['metadata']
    number = decision['number']
    if family_path != INTAKE or number not in REVISIONS:
        return metadata['headRefOid']

    original_name, original_field, current_name = REVISIONS[number]
    rows = {}
    for name in dict.fromkeys((original_name, current_name)):
        path = root / 'docs/research/pr-intake-evidence' / (name + '.json')
        raw = path.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == RECEIPTS[name],
                'Changed initial-head receipt: ' + str(path))
        matches = [row for row in json.loads(raw)['contributions'] if row['number'] == number]
        require(len(matches) == 1, f'#{number}: ambiguous initial-head receipt')
        rows[name] = matches[0]
    original, current = rows[original_name], rows[current_name]
    require(type(metadata['number']) is int and metadata['number'] == number,
            f'#{number}: initial-head metadata number differs')
    require(metadata['headRefOid'] == decision['current_head'] == decision['reviewed_head'] == current['head'],
            f'#{number}: unrecorded intake revision')
    require(json.dumps(metadata['author'], sort_keys=True) ==
            json.dumps(original['author'], sort_keys=True) ==
            json.dumps(current['author'], sort_keys=True),
            f'#{number}: initial-head attribution differs')
    return original[original_field]
