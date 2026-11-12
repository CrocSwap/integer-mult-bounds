"""Compute the signed side-row circuits at the two minimal #7161 groups."""

from fractions import Fraction
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys

WORD_SHA = 'c1caec11ca3ee264ef03018dd91037eac10c3e28950c4c525ee1b4bf5ee210e2'
SIDE_SHA = '483d4802f609ce7669e8e46b89d333b5a7ecbfd751716539357e21478df90295'


def relation(selected, side, rows):
    basis = {}
    for role in side + selected:
        row, factors = rows[role].copy(), {role: Fraction(1)}
        while row:
            col = min(row)
            if col not in basis:
                scale = row[col]
                basis[col] = ({i:x/scale for i,x in row.items()}, {i:x/scale for i,x in factors.items()})
                break
            scale = row[col]
            for dst,src in zip((row,factors), basis[col]):
                for i,x in src.items():
                    v = dst.get(i,0)-scale*x
                    if v:
                        dst[i] = v
                    else:
                        dst.pop(i,None)
        if not row and role in selected:
            assert factors[role] == 1
            return factors
    raise AssertionError('missing circuit')


def run(word_path, side_path):
    data = word_path.read_bytes()
    assert sha256(data).hexdigest() == WORD_SHA
    word = json.loads(gzip.decompress(data))
    data = side_path.read_bytes()
    assert sha256(data).hexdigest() == SIDE_SHA
    groups = json.loads(data)['exact_positive_target_subgroups']
    groups = {cut:g for g in groups if len(g['events']) == 2
              for cut in range(g['witness_cut'],g['witness_cut']+g['eligible_cuts'])}
    assert set(groups) == {39802,39803,39804,45575,45576,45577}
    rows = [{i: Fraction(1)} for i in range(word['public'])] + [{} for _ in range(word['owned_fields'])]
    charts = word['initial'] + [None]*word['owned_fields']
    coefficients = {}
    answers = []

    def span(vectors):
        result = {0}
        for v in vectors:
            result |= {v^x for x in result}
        return result

    spans = list(map(span,word['frames']))
    for cut,(op,role,*args) in enumerate(word['program'][:max(groups)+1]):
        if cut in groups:
            events = groups[cut]['events']
            selected = [word['program'][i][1] for i in events]
            target = [word['program'][i][3] for i in events]
            sides = [i for i,c in enumerate(charts) if i not in selected and c is not None and rows[i]
                     and any(spans[c] == spans[t] for t in target)]
            factors = relation(selected,sides,rows)
            assert set(selected) & set(factors)
            check = {}
            for i,value in factors.items():
                for j,x in rows[i].items():
                    check[j] = check.get(j,0) + value*x
            assert check and not any(check.values())
            side_locality = {t:[i for i in sorted(factors) if i not in selected and spans[charts[i]] == spans[t]] for t in target}
            answers.append(dict(events=events,cut=cut,coefficients={i:str(v) for i,v in sorted(factors.items())},
                                target_side_roles=side_locality, selected_roles=selected,
                                target_span_distance=len(word['frames'][target[0]])+len(word['frames'][target[1]])
                                -2*((len(spans[target[0]] & spans[target[1]])).bit_length()-1)))
        if op == 'MOVE':
            assert charts[role] == args[0]
            charts[role] = args[1]
        elif op == 'CLEAR':
            assert charts[role] == args[0]
            charts[role],rows[role] = None,{}
        elif op == 'INIT':
            assert charts[role] is None and not rows[role]
            charts[role] = args[0]
        else:
            token = args[0 if op == 'SCALE' else 1]
            if token not in coefficients:
                coefficients[token] = Fraction(token)
            value = coefficients[token]
            if op == 'SCALE':
                rows[role] = {i:value*x for i,x in rows[role].items()}
            else:
                source = args[0]
                assert op == 'ADD' or op == 'COPY' and not rows[role]
                for i,x in rows[source].items():
                    z = rows[role].get(i,0) + value*x
                    if z:
                        rows[role][i] = z
                    else:
                        rows[role].pop(i,None)
    return answers


if __name__ == '__main__':
    if not __debug__:
        raise RuntimeError('Run with assertions enabled')
    print(json.dumps(run(*map(Path,sys.argv[1:])),indent=2,sort_keys=True))
