"""Check each fixed recoding against all independent entrance coordinates."""
from collections import Counter
from fractions import Fraction
from hashlib import sha1, sha256
from pathlib import Path
import gzip
import json
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / 'vendor'))
from basis_engine import Graph, basis, vector_sum, encoded, require, histogram
import construct
import recoding
from network import Network, main_roles
from caller16 import signed_caller


def read(name):
    data = (HERE / name).read_bytes()
    return json.loads(gzip.decompress(data) if name.endswith('.gz') else data)


def sparse(entries):
    row = {k: Fraction(q) for k, q in entries}
    require(len(row) == len(entries) and all(row.values()), 'nonzero distinct terms')
    return row


def graph(net):
    return Graph(net.initial, net.final, net.moves, net.forms, net.first_output)


def values(net):
    result, products, _ = basis(graph(net), net.forms)
    result.update({~r: (1, {r: 1}) for r in range(len(net.initial))})
    return result, products


def evaluate(row, data):
    return vector_sum((q, data[k]) for k, q in row.items())


def difference(left, right):
    return vector_sum([(Fraction(1), left), (Fraction(-1), right)])


def describe(value):
    denominator, row = value
    return [[r, str(Fraction(n, denominator))] for r, n in sorted(row.items())]


def one_cut(before, edit, step, old=None):
    products = 0
    if old is None:
        old, products = values(before)
    kind = edit['kind']
    expected = dict(old)
    sender, receiver = sparse(edit.get('sender', [])), sparse(edit['receiver'])
    record = dict(step=step, kind=kind, direction=edit['direction'])
    if kind == 'pivot':
        drop, lead = edit['remove'], edit['pivot']
        combination = sparse(edit['combination'])
        signal = evaluate(combination, old)
        response = sum(q * before.forms[k].get(drop, 0) for k, q in combination.items())
        require(response and combination.get(lead), 'nonzero elimination pivot')
        uses = {k: row[drop] for k, row in before.forms.items() if drop in row}
        require(combination.keys() <= uses.keys(), 'combination uses removed bank')
        for k, q in uses.items():
            if k != lead:
                expected[k] = vector_sum([(Fraction(1), old[k]), (-q / response, signal)])
        del expected[drop]
        expected[lead] = evaluate(sender, old)
        require(expected[lead] == vector_sum([(Fraction(1), signal),
                                             (Fraction(1), evaluate(receiver, old))]),
                f'sender identity at cut {step}')
        after = recoding.pivot(before, edit)
        record.update(remove=drop, retained=lead, response=str(response),
                      sender=edit['sender'], receiver=edit['receiver'],
                      signal=describe(signal), sender_value=describe(expected[lead]))
    else:
        t, j = edit['incoming'], edit['outgoing']
        direction = sparse(edit['innovation'])
        local = before.forms[j] if kind == 'feedback' else sparse(edit['group'])
        response = sum(q * direction.get(k, 0) for k, q in local.items())
        require(direction.get(t) == 1 and response, 'nonzero normalized hub direction')
        signal = old[j] if kind == 'feedback' else evaluate(local, old)
        sent = evaluate(sender, old) if kind == 'feedback' else signal
        if kind == 'feedback':
            require(signal == vector_sum([(Fraction(1), sent),
                                          (Fraction(1), evaluate(receiver, old))]),
                    f'feedback source identity at cut {step}')
        else:
            require(old[j] == vector_sum([(Fraction(1), signal),
                                          (Fraction(1), evaluate(receiver, old))]),
                    f'group receiver identity at cut {step}')
        expected[t] = sent
        for k, q in direction.items():
            if k != t:
                expected[k] = vector_sum([(Fraction(1), old[k]), (-q, old[t])])
        corrections = {}
        for k, row in before.forms.items():
            if k in (t, j):
                continue
            ratio = sum(q * direction.get(d, 0) for d, q in row.items()) / response
            if ratio:
                corrections[k] = ratio
                expected[k] = vector_sum([(Fraction(1), old[k]), (-ratio, signal)])
        determinant = 1 - sum(q * corrections.get(k, 0) for k, q in receiver.items())
        require(kind != 'feedback' or determinant, 'nonsingular receiver')
        after = recoding.hub(before, edit)
        record.update(incoming=t, outgoing=j, response=str(response),
                      corrections=[[k, str(q)] for k, q in sorted(corrections.items())],
                      determinant=str(determinant), sender=edit.get('sender'),
                      receiver=edit['receiver'], signal=describe(signal),
                      sender_value=describe(sent))
    actual, after_products = values(after)
    require(actual.keys() == expected.keys(), f'bank inventory at cut {step}')
    for k, wanted in expected.items():
        require(actual[k] == wanted, f'bank value at cut {step}, key {k}')
    field = 'sender' if sender else 'receiver' if receiver else 'group'
    fault_row = sparse(edit[field])
    donor = next(k for k in fault_row if old[k][1])
    fault_row[donor] += 1
    residual = difference(evaluate(fault_row, old), evaluate(sparse(edit[field]), old))
    require(residual[1], 'altered certificate coefficient control')
    owner, coefficient = next(iter(residual[1].items()))
    record.update(checked_nodes=len(after.forms), coefficient_products=products + after_products,
                  fault_field=field, fault_donor=donor, fault_owner=owner,
                  fault_residual=str(Fraction(coefficient, residual[0])))
    if kind == 'feedback':
        recovered_numerator = vector_sum([(Fraction(1), actual[t]),
                                          (Fraction(1), evaluate(receiver, actual))])
        require(vector_sum([(Fraction(1) / determinant, recovered_numerator)]) == signal,
                'explicit feedback recovery')
        require(vector_sum([(Fraction(1) / (determinant + 1), recovered_numerator)]) != signal,
                'wrong feedback denominator control')
        record['recovery_numerator'] = describe(recovered_numerator)
    return after, record, actual


def run():
    pins = read('SOURCE-PINS.json')
    for pin in pins:
        raw = (HERE / pin['path']).read_bytes()
        require(sha256(raw).hexdigest() == pin['sha256'] and
                sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest() == pin['git_blob'],
                'source bytes: ' + pin['path'])
    word, certs = read('data/WORD.json.gz'), read('data/CERTS.json')
    raw, clears, moves = construct.raw_fold(word, certs['clear_event_index'])
    parent, relay = construct.contract(raw, word['frames'], clears, moves)
    parent_bytes = construct.serialized(parent, word['frames'], 'candidate',
                                       source_banked_graph_sha256=construct.PARENT, paid_relay=relay)
    require(sha256(parent_bytes).hexdigest() == construct.CHILD, 'exact PR7704 parent')
    net = Network(parent.first, parent.initial, parent.final, parent.moves, parent.forms)
    mains = main_roles(word)
    old_paid, old_targets = histogram(graph(net), word['frames'], mains)
    records, cached, orientation = [], None, None
    for step, edit in enumerate(read('data/PARENT-CUTS.json'), 1):
        require(edit['direction'] in ('forward', 'transpose'), 'cut direction')
        work = net.transpose() if edit['direction'] == 'transpose' else net
        after, record, cached = one_cut(work, edit, step,
                                        cached if orientation == edit['direction'] else None)
        orientation = edit['direction']
        keys = [edit['remove'], edit['pivot']] if edit['kind'] == 'pivot' else [edit['incoming'], edit['outgoing']]
        record['routes'] = [dict(key=k, before=list(work.moves[k]),
                                after=list(after.moves[k]) if k in after.moves else None,
                                old_rank=abs(len(word['frames'][work.moves[k][0]]) - len(word['frames'][work.moves[k][1]])),
                                new_rank=abs(len(word['frames'][after.moves[k][0]]) - len(word['frames'][after.moves[k][1]]))
                                if k in after.moves else None) for k in keys]
        net = after.transpose() if edit['direction'] == 'transpose' else after
        histogram(graph(net), word['frames'], mains)
        records.append(record)
    published = read('data/PARENT-APPLICATION.json')
    digest = sha256(encoded(recoding.layout(word, net))).hexdigest()
    require(digest == published['graph_sha256'] ==
            'db10e4ca7154b454f86bf404bc34b3a16d02de6cc008d5227e4eef2654cb0778',
            'exact PR7708 child')
    new_paid, new_targets = histogram(graph(net), word['frames'], mains)
    require(old_targets == new_targets, 'unchanged productive targets')
    signed = signed_caller(read('data/CALLER.json.gz'), word, 2025, 9)
    require(json.loads(json.dumps(signed)) == published['caller'], 'complete signed caller')
    def invoice(paid, targets):
        fields = []
        for native, fixed in ((paid, signed['fixed_caller_paid']),
                              (targets, signed['fixed_root_targets'])):
            row = Counter({r: 16 * n for r, n in native.items()})
            row.update(fixed)
            fields.append({str(r): n for r, n in sorted(row.items())})
        return dict(paid=fields[0], targets=fields[1])
    old, new = invoice(old_paid, old_targets), invoice(new_paid, new_targets)
    require(all(new[k] == published['invoice'][k] for k in new), 'complete signed invoice')
    delta = {str(r): 16 * (new_paid[r] - old_paid[r]) for r in sorted(old_paid.keys() | new_paid.keys())
             if new_paid[r] != old_paid[r]}
    require(sum(delta.values()) == -352 and sum(int(r) * n for r, n in delta.items()) == 0,
            '22 paid calls per stage and unchanged rank mass')
    native_delta = {int(r): n // 16 for r, n in delta.items()}
    tails = [sum(n for r, n in native_delta.items() if r >= j) for j in range(1, 8)]
    prefixes = [sum(tails[:j]) for j in range(1, 8)]
    require(prefixes[-1] == 0 and all(n < 0 for n in prefixes[:-1]),
            'strict concave moment improvement')
    return dict(status='PASS_ALL_RECODING_BANK_BASES', source_pins=len(pins),
                parent_sha256=construct.CHILD, graph_sha256=digest, public=len(net.initial),
                cuts=records, kinds=dict(Counter(e['kind'] for e in records)),
                checked_nodes=sum(e['checked_nodes'] for e in records),
                coefficient_products=sum(e['coefficient_products'] for e in records),
                invoice_before=old, invoice_after=new, full_paid_delta=delta,
                native_paid_tails=tails, native_paid_tail_prefixes=prefixes,
                source_claim_unchanged=published['claim'], signed_caller=signed)


if __name__ == '__main__':
    result = run()
    if sys.argv[1:] == ['--emit']:
        print(json.dumps(result, indent=2))
    else:
        require(not sys.argv[1:] and json.loads(json.dumps(result)) == read('RESULT.json'), 'exact receipt')
        print(result['status'], len(result['cuts']), result['checked_nodes'])
