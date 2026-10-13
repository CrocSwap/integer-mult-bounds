"""Exact joint omission controls for two sequential cold kernels.

Every mutant uses the final correct word's compensation. The first and second
recipe inputs/outputs and actual inserted instructions are independently bound.
Prepared with OpenAI Codex assistance; Apache-2.0.
"""
import argparse
import copy
import gzip
import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path

if not __debug__:
    raise SystemExit('Assertions required.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('word', 'first-recipe', 'second-recipe', 'out'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    assert not args.out.exists()
    raw = gzip.decompress(args.word.read_bytes())
    word = json.loads(raw)
    first = json.loads(args.first_recipe.read_text())
    second = json.loads(args.second_recipe.read_text())
    assert first['output_content_sha256'] == second['input_content_sha256']
    assert hashlib.sha256(raw).hexdigest() == second['output_content_sha256']
    assert first['part'] == second['part'] == 'B'
    assert (first['pivot'], second['pivot']) == (494, 518)
    assert first['index'] == 368 and second['index'] in (397, 409)
    v = len(word['ports'])
    n = 2*v + word['report']['R']
    assert (v, n) == (112, 728)

    def inverse(event, dual=False):
        event = copy.deepcopy(event)
        if event[0] == 'add':
            event[3] *= -1
            if dual:
                event[1], event[2] = event[2], event[1]
        else:
            assert event[0] == 'scale'
            event[2], event[3] = event[3], event[2]
        return event

    def ident():
        return [{r: Q(1)} for r in range(n)]

    def apply(event, rows):
        if event[0] == 'scale':
            target = event[1]
            factor = Q(event[2], event[3])
            rows[target] = {j: factor*x for j, x in rows[target].items()}
            return
        assert event[0] == 'add'
        target, source = event[1:3]
        assert target != source
        factor = Q(event[3], event[4])
        for j, x in list(rows[source].items()):
            value = rows[target].get(j, Q(0)) + factor*x
            if value:
                rows[target][j] = value
            else:
                rows[target].pop(j, None)

    def replay(events):
        rows = ident()
        for event in events:
            apply(event, rows)
        return rows

    groups = []
    for recipe in (first, second):
        expected_gates = []
        for donor, coefficient in sorted(recipe['coefficients'].items(), key=lambda z: int(z[0])):
            q = Q(coefficient)
            expected_gates.append(['add', int(donor), recipe['pivot'],
                                   -q.numerator, q.denominator, recipe['frame']])
        assert len(expected_gates) == 5
        index = recipe['index']
        assert word['B'][index:index+5] == expected_gates
        assert word['start_extra'][str(recipe['pivot'])] == recipe['frame']
        groups.append(list(range(index, index+5)))
    assert max(groups[0]) < min(groups[1])

    main_word = word['A'] + word['cut'] + word['B']
    endpoint = replay(main_word)
    dirty = [{} for _ in range(n)]
    for target in range(v, 2*v):
        dirty[target] = {j: x for j, x in endpoint[target].items() if j >= 2*v}
    for event in word['precondition']:
        apply(event, dirty)
    compensation = []
    for target in range(v, 2*v):
        for source, coefficient in sorted(dirty[target].items()):
            assert not word['start_extra'].get(str(source))
            compensation.append(['add', target, source, -coefficient.numerator,
                                 coefficient.denominator, []])
    cleanup = [inverse(event) for event in reversed(word['A'] + word['B'])
               if not v <= event[1] < 2*v]
    assert [event[:-1] for event in cleanup] == [event[:-1] for event in word['cleanup']]
    expected, backward = ident(), ident()
    for t in range(v):
        expected[v+t][t] = Q(1)
        backward[t][v+t] = Q(-1)
    program = word['precondition'] + compensation + main_word + cleanup
    assert replay(program) == expected
    assert replay([inverse(event, True) for event in program]) == backward

    mutations = [('individual_gate', [i]) for group in groups for i in group]
    mutations += [('whole_first_kernel', groups[0]), ('whole_second_kernel', groups[1]),
                  ('both_kernels', groups[0] + groups[1])]
    controls = []
    for name, omitted in mutations:
        changed = [event for i, event in enumerate(word['B']) if i not in omitted]
        reverse = [inverse(event) for event in reversed(word['A'] + changed)
                   if not v <= event[1] < 2*v]
        mutant = word['precondition'] + compensation + word['A'] + word['cut'] + changed + reverse
        assert replay(mutant) != expected, ('forward accepted', omitted)
        assert replay([inverse(event, True) for event in mutant]) != backward, ('backward accepted', omitted)
        controls.append(dict(kind=name, omitted_B_indices=omitted,
                             forward_rejected=True, reflected_rejected=True))
    assert len(controls) == 13
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    report = dict(status='PASS_EXACT_TWO_KERNEL_JOINT_OMISSION_CONTROLS',
                  word_sha256=digest(args.word), final_content_sha256=hashlib.sha256(raw).hexdigest(),
                  first_recipe_sha256=digest(args.first_recipe), second_recipe_sha256=digest(args.second_recipe),
                  columns_each_orientation=n, recipe_chain_bound=True, actual_inserted_gates_bound=True,
                  correct_final_compensation_frozen=True, compensation_entries=len(compensation),
                  controls=controls,
                  scope='The exact final two-kernel word passes both arbitrary-dirty scalar orientations. Ten individual gates, each entire kernel, and both kernels are omitted with regenerated cleanup but unchanged correct final compensation; both orientations reject every mutant. Physical phases, owners, finite invoice and assembly remain separate.')
    args.out.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(report['status'], len(controls))


if __name__ == '__main__':
    main()
