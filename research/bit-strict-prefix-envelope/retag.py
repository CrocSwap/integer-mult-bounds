"""The eight frozen #7001 backup retags from the Round 13 experiment."""

import copy

def touched(event):
    return event[1:3] if event[0] in ('ADD', 'SWAP') else event[1:2]


def modules(word):
    program = word['program']
    selected = []
    edited_indices = set()
    for start, (event, next_) in enumerate(zip(program, program[1:])):
        if not (event[0] == 'INIT' and next_[0] == 'ADD' and event[1] == next_[1]
                and next_[2] < 111 and event[2] == word['start'][next_[2]]):
            continue
        _, backup, source = event
        port = next_[2]
        body = start + 2
        while program[body][0] == 'MOVE' and program[body][2:] == [0, source]:
            body += 1
        ingress = list(range(start + 2, body))
        roles = {port} | {program[i][1] for i in ingress}
        assert len(roles) == len(ingress) + 1
        end_add = body
        while program[end_add][0] == 'ADD' and program[end_add][3] == source and set(touched(program[end_add])) <= roles:
            end_add += 1
        end = end_add + len(roles)
        exits = list(range(end_add, end))
        assert {program[i][1] for i in exits} == roles
        assert all(program[i][0] == 'MOVE' and program[i][2] == source for i in exits)
        init, copied, late, clear = (i for i in range(start, len(program)) if backup in touched(program[i]))
        assert (init, copied) == (start, start + 1)
        consumer = program[late][1]
        assert program[late - 1:late + 1] == [['MOVE', consumer, 0, source], ['ADD', consumer, backup, source]]
        assert program[late + 1][:3] == ['MOVE', consumer, source]
        assert program[clear] == ['CLEAR', backup, source]
        changes = set(range(start, end)) | {late - 1, late, late + 1, clear}
        assert not edited_indices & changes
        edited_indices.update(changes)
        selected.append({'port': port, 'backup': backup, 'source': source, 'init': start,
                         'first_add': body, 'exits': exits, 'ingress': ingress, 'late_add': late,
                         'late_consumer': consumer, 'clear': clear})
        if len(selected) == 8:
            break
    assert [m['port'] for m in selected] == [0, 1, 2, 3, 4, 5, 7, 8]
    return selected


def retag(word, selected):
    changed = copy.deepcopy(word)
    program = changed['program']
    drop, adjusted = set(), {}
    for m in selected:
        port, start, late, clear = (m[k] for k in ('port', 'init', 'late_add', 'clear'))
        changed['start'][port] = 0
        program[start][-1] = program[start + 1][-1] = program[clear][-1] = 0
        for j in range(m['first_add'], m['exits'][0]):
            program[j][-1] = 0
        for j in (*m['exits'], late + 1):
            program[j][2] = 0
            adjusted[j] = port
        program[late][-1] = 0
        drop.update([*m['ingress'], late - 1])
    origin = [i for i in range(len(program)) if i not in drop]
    changed['program'] = [program[i] for i in origin]
    return changed, origin, adjusted, sorted(drop)
