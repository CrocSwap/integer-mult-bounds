"""Test every legal single exchange at the first promoted role."""

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import importlib.util
import json


HERE = Path(__file__).resolve().parent
PRIME = 65537


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def modular_word(skeleton, rows, columns, family, signs):
    values = [0]*14336
    values[family] = 1
    inv8 = pow(8, -1, PRIME)
    for event in skeleton['execution_schedule']:
        kind = event['kind']
        if kind == 'paired_input_boundary':
            pair = [skeleton['calls'][t] for t in event['times']]
            backward = pair[0]['orientation'] == 'backward'
            source = [[values[f] for f in call['data_families'][112:224]]
                      if backward else [values[f] for f in call['data_families'][:112]] for call in pair]
            z = [[values[f] for f in call['mode_families']] for call in pair]
            query = [[sum(c*source[j][p] for p, c in row) % PRIME for row in rows] for j in range(2)]
            next_modes = [[(-z[j][k]-(query[j][k]-query[1-j][k])*(inv8 if backward else 1)) % PRIME
                           for k in range(8)] for j in range(2)]
            h = [(z[0][k]+z[1][k]) % PRIME for k in range(8)]
            for j, call in enumerate(pair):
                targets = call['data_families'][:112] if backward else call['data_families'][112:224]
                for p, target in enumerate(targets):
                    kh = sum(c*h[k] for k, c in columns[p])
                    delta = -source[j][p]-8*kh if backward else source[j][p]-kh
                    values[target] = (values[target]+delta) % PRIME
                for k, target in enumerate(call['mode_families']):
                    values[target] = (-next_modes[j][k] if signs else next_modes[j][k]) % PRIME
        elif kind == 'bridge':
            base, dst, src, c = 896*event['replica'], event['dst'], event['src'], event['coefficient']
            for p in range(112):
                values[base+224*dst+p] = (values[base+224*dst+p]+c*values[base+224*src+p]) % PRIME
                values[base+224*src+112+p] = (values[base+224*src+112+p]-c*values[base+224*dst+112+p]) % PRIME
        elif kind == 'terminal':
            for pair in range(4):
                base = 896*event['replica']+224*pair
                for p in range(112):
                    values[base+p], values[base+112+p] = values[base+112+p], -values[base+p] % PRIME
    return values


def main():
    helper = HERE/'review_drift.py'
    spec = importlib.util.spec_from_file_location('independent_drift_review', helper)
    review = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(review)
    data = review.load()
    review.check_repair(data)
    need(all(PRIME % p for p in range(2, 257)), 'The fixed odd modulus is prime')
    interface_path = review.LANES/'circuit-interface/INTERFACE.json'
    need(sha256(interface_path.read_bytes()).hexdigest() == '5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3', 'The actual coefficient matrix')
    interface = json.loads(interface_path.read_text())
    rows = [[(int(p), int(c)) for p, c in row.items()] for row in interface['R']]
    columns = [[(k, dict(row)[p]*pow(4, -1, PRIME) % PRIME) for k, row in enumerate(rows) if p in dict(row)] for p in range(112)]
    skeleton = data['source-domain/productive-owner-drift/REPAIRED-SKELETON.json.gz']
    canonical = data['canonical']
    a, b = skeleton['calls'][:2]
    donors = [r for r in range(224, 704) if r not in review.MODES
              and len(canonical['frames'][canonical['final'][r]])-len(canonical['frames'][canonical['start'][r]]) == 9
              and a['owner_families'][r] not in b['owner_families']]
    need(len(donors) == 202, 'All legal same-call width-nine donors')
    paired = data['residual-syndrome/physical-algebra/ORIGINAL-PAIRED-GAP-PROGRAMS.json.gz']
    core = data['history-encoding/FULL-MODE-PROGRAMS.json.gz']
    cores = {(o, rev): review.scalar_core(core[o], rev) for o in ('forward', 'backward') for rev in (False, True)}
    for signs in (False, True):
        initial = [review.Fraction(0)]*14336
        initial[13005] = review.Fraction(1)
        exact = review.replay(skeleton, paired, cores, initial, signs)[0]
        modular = modular_word(skeleton, rows, columns, 13005, signs)
        need(modular == [x.numerator*pow(x.denominator, -1, PRIME) % PRIME for x in exact],
             'The endpoint algorithm agrees with the independent literal word')
    witnesses = []
    for donor in donors:
        candidate = deepcopy(skeleton)
        call = candidate['calls'][0]
        for key, offset in (('owner_families', 0), ('helper_source_roles', 224)):
            first, second = 225-offset, donor-offset
            call[key][first], call[key][second] = call[key][second], call[key][first]
        call['mode_families'] = [call['owner_families'][r] for r in review.MODES]
        family = call['owner_families'][225]
        need(set(call['owner_families']) == set(a['owner_families']) and
             sorted(call['helper_source_roles']) == sorted(a['helper_source_roles']) and
             not set(call['mode_families']) & set(b['owner_families']), 'The candidate preserves the legal same-call job contract')
        variants = []
        for signs in (False, True):
            output = modular_word(candidate, rows, columns, family, signs)
            differences = [(i, (value-(i == family)) % PRIME) for i, value in enumerate(output)
                           if value != (i == family)]
            need(differences, 'Every candidate has a certified nonzero defect for its new owner input')
            variants.append({'signs': signs, 'first_defect_mod_prime': differences[0],
                             'nonzero_defect_families_mod_prime': len(differences)})
        witnesses.append({'donor_role': donor, 'new_mode_family': family, 'variants': variants})
    receipt = {'status': 'PASS_ALL_SINGLE_FIRST_MODE_EXCHANGES_HAVE_EXPLICIT_DEFECTS',
               'repaired_skeleton_payload_sha256': review.PINS['source-domain/productive-owner-drift/REPAIRED-SKELETON.json.gz'],
               'review_checker_sha256': sha256(helper.read_bytes()).hexdigest(),
               'prime': PRIME, 'call': 0, 'mode_role': 225, 'tested_donors': len(donors),
               'variants_per_donor': 2, 'witnesses': witnesses,
               'scope': 'All single same-call width-nine exchanges at mode role225 of call0, with all other repaired assignments and graphs fixed. Nonzero reduction modulo an odd prime certifies an exact dyadic defect. This does not exclude several coordinated exchanges, changed graph shears, or another controller.',
               'checker_sha256': sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE/'FIRST-OWNER-EXCHANGES.json').write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')
    print(receipt['status'], len(witnesses))


if __name__ == '__main__':
    main()
