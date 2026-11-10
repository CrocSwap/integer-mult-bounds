#!/usr/bin/env python3
"""Portable driver for the separately written cut and accounting cores.

@CubeJerry with substantial OpenAI assistance. Apache-2.0.
The constructor only supplies hash-authenticated intermediate words. All
scientific reverse-prefix, suffix, contact-window and accounting predicates
come from the independent cores; they import no producer scientific code.
Mutation controls are retained from the separate frozen68 cross-review.
"""
from copy import deepcopy
import gzip
import json
from hashlib import sha256
from pathlib import Path
from construct import construct
import independent_directional as directional
import independent_accounting as accounting
import independent_moments as moments

HERE = Path(__file__).resolve().parent


def read(name):
    data = (HERE / name).read_bytes()
    return json.loads(gzip.decompress(data) if name.endswith('.gz') else data)


def need(value, message):
    if not value:
        raise ValueError(message)


def main():
    original_result = {k: v for k, v in read('RESULT.json').items()
                       if k != 'compatible_caller'}
    original_bytes = (json.dumps(original_result, sort_keys=True, indent=2) + '\n').encode()
    need(sha256(original_bytes).hexdigest() ==
         '1b44ec438e0d0eff162b6d56fc9189785bcdd73606fcbf3529eaa039bdc72b84',
         'Original scientific RESULT view reviewed independently')
    source = read('retained/data/word.json.gz')
    word = source
    receipts = []
    wrong_roles = cross_contacts = 0
    for step, entry in enumerate(read('WITNESSES.json'), 1):
        result = directional.check_cut(word, entry)
        result['step'] = step
        receipts.append(result)
        if entry['witness']['paths']:
            bad = deepcopy(entry)
            path = bad['witness']['paths'][0]
            path['role'] = (path['role'] + 1) % word['public']
            try:
                directional.prepare(word, bad)
            except ValueError:
                wrong_roles += 1
            else:
                raise ValueError('Wrong retiming owner accepted')
            path = entry['witness']['paths'][0]
            role, events = path['role'], word['program']
            def touches(event):
                return event[0] != 'MOVE' and (event[1] == role or
                       (event[0] in ('ADD', 'COPY') and event[2] == role))
            earlier = next((j for j in range(path['lo'] - 1, -1, -1)
                            if touches(events[j])), None)
            later = next((j for j in range(path['hi'], len(events))
                          if touches(events[j])), None)
            need(earlier is not None or later is not None,
                 'A real scalar-contact mutation exists')
            bad = deepcopy(entry)
            if earlier is not None:
                bad['witness']['paths'][0]['lo'] = earlier
            else:
                bad['witness']['paths'][0]['hi'] = later + 1
            try:
                directional.prepare(word, bad)
            except ValueError as error:
                need('no scalar or other operator incidence' in str(error),
                     'The contact mutation fails its mathematical guard')
                cross_contacts += 1
            else:
                raise ValueError('MOVE through a scalar contact accepted')
        word, _ = construct(word, entry['witness'])
    need(word == read('WORD.json.gz'), 'Final authenticated native payload')
    cuts = dict(cuts=len(receipts),
                retimed_MOVEs=sum(r['retimed_MOVEs'] for r in receipts),
                retimed_cuts=sum(bool(r['retimed_MOVEs']) for r in receipts),
                future_COPY_zero_guards=sum(r['future_COPY_zero_guards'] for r in receipts),
                wrong_functional_controls=len(receipts),
                wrong_retiming_owner_controls=wrong_roles,
                scalar_contact_crossing_controls=cross_contacts,
                receipts=receipts)
    need(cuts == read('INDEPENDENT-CUTS.json'), 'Independent cut receipt reproduced')
    original = read('retained/data/caller.json')
    for caller_name, receipt_name in (
            ('retained/data/caller.json', 'INDEPENDENT-ACCOUNTING.json'),
            ('retained/caller-blocks/data/caller-after.json',
             'INDEPENDENT-ACCOUNTING-COMPRESSED.json')):
        actual = accounting.check_accounting(
            word, source, read(caller_name), read('RESULT.json'),
            (HERE / 'retained/retained/bit/FRAGMENT-BIT-ADMISSION.json').read_bytes(),
            original)
        need(actual == read(receipt_name), 'Independent complete accounting reproduced')
    compressed = read('retained/caller-blocks/data/caller-after.json')
    claim = read('RESULT.json')['claim']
    moment = moments.check(word, compressed, claim)
    need(json.loads(json.dumps(moment)) == read('INDEPENDENT-MOMENTS.json'),
         'Independent literal invoice and rational moment receipt reproduced')
    bad_claim = dict(claim, kappa=claim['raw_upper'])
    try:
        moments.check(word, compressed, bad_claim)
    except ValueError:
        pass
    else:
        raise ValueError('An overstated headline passed the independent moment check')
    print(json.dumps({k: v for k, v in cuts.items() if k != 'receipts'}, sort_keys=True))
    print('PASS_INDEPENDENT_HELPER_CUTS_AND_ACCOUNTING')


if __name__ == '__main__':
    main()
