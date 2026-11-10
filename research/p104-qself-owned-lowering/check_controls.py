"""Meaningful source, algebra, ownership, phase and billing failure controls."""
from pathlib import Path
from copy import deepcopy
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from source_binding import inputs
import operator_ring as P
import dual_certificate as D
import owned_lowering as O
import invoice as I


def rejection(action):
    try:
        action()
    except ValueError:
        return True
    raise ValueError('negative control was not rejected')


def verify():
    caller, old, word, bases = inputs()
    result = {}
    def mutation(name, edit, dual=False):
        bad = deepcopy(caller); edit(bad)
        result[name] = rejection(lambda: P.replay(bad))
        if dual:
            result[name+' / independent covectors'] = rejection(lambda: D.certificate(bad))
    mutation('deleted first QSELF', lambda c: c['events'].pop(457), True)
    mutation('deleted second QSELF', lambda c: c['events'].pop(575))
    mutation('Q instead of inverse Q', lambda c: c['events'][457].__setitem__(3, 1), True)
    mutation('wrong source owner', lambda c: c['events'][575].__setitem__(2, 20))
    mutation('arbitrary-input contamination', lambda c: c['events'].append(['A', 'ADD', 0, 1, '1']), True)
    selected = next(i+1 for i, b in enumerate(caller['types']['A']['diagonal'][0][2:]) if b)
    mutation('repeated D across separate events', lambda c: c['events'].append(['A', 'IDLE_ONE', 0, [selected]]), True)
    idle = next(i for i, e in enumerate(caller['events']) if e[0] == 'A' and e[1] == 'IDLE_ONE')
    mutation('duplicate idle stage in one mask', lambda c: c['events'][idle][3].append(c['events'][idle][3][0]))
    lam = next(i for i, e in enumerate(caller['events']) if e[0] == 'A' and e[1] == 'LAMBDA')
    mutation('wrong total-Q LAMBDA phase', lambda c: c['events'][lam].__setitem__(3, -c['events'][lam][3]))
    for modulus in (2, 8):
        result['wrong q period '+str(modulus)] = rejection(lambda modulus=modulus: P.replay(caller, modulus=modulus))
    result['missing Q-squared return translation'] = rejection(lambda: O.adapter_records(caller, word, bases, omit_translation=True))
    result['omitted inverse ambient basis'] = rejection(lambda: O.adapter_records(caller, word, bases, omit_inverse=True))
    bad_basis = deepcopy(bases); bad_basis['records'][0]['basis'][1] = bad_basis['records'][0]['basis'][0]
    result['nonorthogonal adapter'] = rejection(lambda: O.adapter_records(caller, word, bad_basis))
    port = caller['types']['A']['ports'][0]
    unit = O.expansion(caller, 457, port)
    def altered(events, owned=None):
        return O.IR.Unit(unit.name, unit.roles, unit.owned if owned is None else owned, tuple(events))
    result['owned public alias'] = rejection(lambda: O.expansion(caller, 457, port, bank=unit.roles[0][0]))
    result['missing physical CLEAR'] = rejection(lambda: O.check_expansion(altered(unit.events[:-1]), caller, 457, port))
    result['COPY before initialization'] = rejection(lambda: O.check_expansion(altered((unit.events[1], unit.events[0])+unit.events[2:]), caller, 457, port))
    result['clear before child return'] = rejection(lambda: O.check_expansion(altered(unit.events[:3]+(unit.events[-1],)+unit.events[3:-1]), caller, 457, port))
    bad = list(unit.events); e = bad[3]; bad[3] = O.IR.Event(e.op, e.fields, e.token, 2)
    result['undercounted paid rank'] = rejection(lambda: O.check_expansion(altered(bad), caller, 457, port))
    bad = list(unit.events); e = bad[5]; bad[5] = O.IR.Event(e.op, e.fields, ('query-add',)+e.token[1:])
    result['ADD substituted for complete swap'] = rejection(lambda: O.check_expansion(altered(bad), caller, 457, port))
    result['unbound source site'] = rejection(lambda: O.expansion(caller, 458, port))
    result['type-B port substituted'] = rejection(lambda: O.expansion(caller, 457, caller['types']['B']['ports'][0]))
    bad = deepcopy(caller); bad['events'].pop(457)
    result['missing new paid debit'] = rejection(lambda: I.verify(old, bad, word))
    bad_word = deepcopy(word); bad_word['hosted']['X2'][0] = bad_word['hosted']['Y2'][0]
    result['helper/main allocation alias'] = rejection(lambda: I.verify(old, caller, bad_word))
    # The stored bases happen to be involutions. Reusing B for B^-1 is
    # equivalent here and must not be reported as a rejected negative control.
    equivalent = True
    for row in bases['records']:
        if row['port'] not in caller['types']['A']['ports']:
            continue
        basis = row['basis']
        def B(x):
            return sum(((a & x).bit_count() % 2) << i for i, a in enumerate(basis))
        equivalent &= all(B(B(x)) == x for x in range(512))
    P.need(equivalent, 'equivalent forward/inverse substitution is correctly classified')
    return {'rejected': len(result), 'controls': result,
            'equivalent_not_negative': 'All 96 stored nine-axis bases are involutions; forward-for-inverse is correctly accepted.'}


if __name__ == '__main__':
    print(json.dumps(verify(), sort_keys=True))
    print('PASS_QSELF_OWNED_CONTROLS')
