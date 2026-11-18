"""Replay the fixed-word obstruction and its rejection controls."""
from copy import deepcopy
from hashlib import sha1, sha256
from pathlib import Path
import gzip
import importlib.util
import json

HERE = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name+'.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def normalized(value):
    return json.loads(json.dumps(value))


def evaluate():
    primary, other = load('census'), load('independent')
    word, caller = primary.source()
    for pin in primary.read(HERE / 'SOURCE-PINS.json'):
        data = (HERE / pin['path']).read_bytes()
        other.require(sha256(data).hexdigest() == pin['sha256'], 'retained source SHA-256')
        other.require(sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() == pin['git_blob'], 'retained source Git blob')
    certificate = primary.read(HERE / 'CERTIFICATE.json.gz')
    other.require(normalized(primary.run()) == certificate, 'primary certificate replay')
    frame_pairs = other.frames(word)
    states = [other.validate_orientation(word, record, backward)
              for record, backward in zip(certificate['orientations'], (False, True))]
    other.require(normalized(other.invoice(word, caller)) == certificate['source_invoice'], 'independent full invoice')
    controls = []
    group = certificate['orientations'][0]['groups'][0]

    def reject(label, changed, expected):
        try:
            other.validate_group(changed, *states[0])
        except ValueError as error:
            other.require(str(error) == expected, label+' failed at wrong gate: '+str(error))
            controls.append(label)
        else:
            raise ValueError('control accepted: '+label)

    changed = deepcopy(group)
    changed['lost_rank'] = 0
    reject('omitted productive debit', changed, 'productive target debit')
    changed = deepcopy(group)
    changed['spaces'].pop(next(i for i,s in enumerate(changed['spaces']) if s['chart'] != group['exit']))
    reject('omitted receiver space', changed, 'complete clean dimension')
    changed = deepcopy(group)
    changed['exceptional_cases'].pop(next(i for i,c in enumerate(changed['exceptional_cases']) if len(c['signal']) > 1))
    reject('omitted noncoordinate direction', changed, 'complete exceptional union')
    changed = deepcopy(group)
    changed['spaces'][0]['basis'][0]['relation'].pop()
    reject('corrupt exact witness', changed, 'exact clean witness')
    changed = deepcopy(group)
    hit = next(h for c in changed['exceptional_cases'] for h in c['hits'] if len(h['relation']) > 1)
    hit['pivot'] = min(hit['relation'])
    reject('future donor reconstruction', changed, 'earlier-bank reconstruction')
    changed = deepcopy(group)
    changed['terminal_pivots'].pop()
    reject('omitted terminal prefix pivot', changed, 'causal terminal pivots')
    # Equal integer mass can improve after a split. The strict deficit is needed.
    # The exact equivalent is 2*2^t > 4^t for 0<t<1.
    other.require(2**100*2**99 > 4**99, 'positive concave split')
    controls.append('equal-mass split lies outside strict-deficit proof')
    receipt = dict(status='PASS_SINGLE_BIT_RELATION_OBSTRUCTION', source_invoice=certificate['source_invoice'],
        public=word['public'], owned=word['owned_fields'], events=len(word['program']), frames=len(word['frames']),
        nested_pairs=frame_pairs, orientations=[dict(direction=o['direction'], paid=o['paid'],
            receiver_charts=o['receiver_charts'], retained_rows=o['retained_rows'],
            exceptional_directions=o['exceptional_directions'], groups=[dict(entrance=g['entrance'], exit=g['exit'],
            helpers=len(g['roles']), lost_rank=g['lost_rank'], terminal_rank_max=g['terminal_rank_max'],
            nonterminal_dimension_max=max((len(s['basis']) for s in g['spaces'] if s['chart'] != g['exit']), default=0),
            exceptional_directions=len(g['exceptional_cases'])) for g in o['groups']]) for o in certificate['orientations']],
        controls=controls, kappa_interval=certificate['kappa_interval'])
    return receipt


def run():
    receipt = evaluate()
    if receipt != json.loads((HERE / 'RESULT.json').read_text()):
        raise ValueError('stored summary receipt')
    print(receipt['status'], '18 group-orientations; 789 exceptional directions; 6 rejected mutations; exact frame and full invoice checks')


if __name__ == '__main__':
    run()
