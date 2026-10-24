"""Fixed-word lowering of the source mode map.
Ali Romman with OpenAI Codex assistance. Apache-2.0.
The source ROUND52 and range checks retain JoyboyBrian's credit.
"""
from collections import defaultdict


def need(ok, why):
    if not ok:
        raise ValueError(why)


def groups_for(columns):
    need(len(columns) == 8 and all(len(c) == 112 and all(type(v) is int and v in (-1, 0, 1) for v in c) for c in columns), 'Mode coefficients')
    groups = defaultdict(dict)
    for i in range(112):
        support = tuple(j for j in range(8) if columns[j][i])
        need(len(support) == 4, 'Four modes per owner')
        sign = columns[support[0]][i]
        mask = sum((columns[support[k+1]][i] != sign) << k for k in range(3))
        need(mask not in groups[support], 'Repeated cube vertex')
        groups[support][mask] = (i, sign)
    need(len(groups) == 14 and all(set(g) == set(range(8)) for g in groups.values()), 'Complete sign cubes')
    return groups


class Builder:
    def __init__(self):
        self.code = []
        self.next = 0

    def add(self, left, right, a=1, b=1, target=None):
        if target is None:
            target = ('t', self.next)
            self.next += 1
        self.code.append((target, left, right, a, b))
        return target


def emit(columns):
    groups = groups_for(columns)
    g, s = Builder(), Builder()
    for support, group in groups.items():
        sums, diffs = [], []
        for mask in range(0, 8, 2):
            i, si = group[mask]
            j, sj = group[mask+1]
            sums.append(g.add(('o', i), ('o', j), si, sj))
            diffs.append(g.add(('o', i), ('o', j), si, -sj))
        odd = g.add(g.add(diffs[0], diffs[1]), g.add(diffs[2], diffs[3]))
        t0 = g.add(sums[0], sums[1])
        t1 = g.add(sums[0], sums[1], b=-1)
        t2 = g.add(sums[2], sums[3])
        t3 = g.add(sums[2], sums[3], b=-1)
        out = [g.add(t0, t2), odd, g.add(t1, t3), g.add(t0, t2, b=-1)]
        for k, value in zip(support, out):
            g.add(('m', k), value, target=('m', k))
        a, b, c, d = [('m', k) for k in support]
        u = [s.add(a, b), s.add(a, b, b=-1)]
        v = [s.add(c, d), s.add(c, d, b=-1)]
        for mask in range(8):
            j = ((mask >> 1) ^ (mask >> 2)) & 1
            sign = 1 - 2*((mask >> 1) & 1)
            value = s.add(u[mask & 1], v[j], b=sign)
            i, own_sign = group[mask]
            s.add(('o', i), value, b=-own_sign, target=('o', i))
    return allocate(g.code), allocate(s.code)


def allocate(code):
    last = {}
    for pos, (_, left, right, _, _) in enumerate(code):
        for source in (left, right):
            if source[0] == 't':
                last[source] = pos
    live, free, result = {}, set(range(120, 128)), []
    peak = 0
    def locate(ref):
        if ref[0] == 'o': return ref[1]
        if ref[0] == 'm': return 112 + ref[1]
        need(ref in live, 'Read before temporary definition')
        return live[ref]
    for pos, (target, left, right, a, b) in enumerate(code):
        li, ri = locate(left), locate(right)
        for source in set((left, right)):
            if source[0] == 't' and last[source] == pos:
                free.add(live.pop(source))
        if target[0] == 't':
            need(bool(free), 'More than eight temporary words')
            dst = min(free)
            free.remove(dst)
            live[target] = dst
        else:
            dst = locate(target)
        peak = max(peak, len(live))
        result.append((dst, li, ri, a, b))
    need(not live, 'Live temporary at program end')
    return result, peak


def signed_sum(words, instruction):
    dst, left, right, a, b = instruction
    need(a in (-1, 1) and b in (-1, 1), 'Signed sum coefficients')
    carry = int(a < 0) + int(b < 0)
    for bit in range(len(words[dst])):
        total = (words[left][bit] ^ int(a < 0)) + (words[right][bit] ^ int(b < 0)) + carry
        words[dst][bit] = total & 1
        carry = total >> 1


def invoice(width, components):
    need(type(width) is int and width >= 3 and type(components) is int and components >= 0, 'Geometry')
    return {'tapes': 130, 'scratch_words': 17, 'signed_sums': 588*components,
            'round52_calls': 8*components, 'range_checks': 112*components,
            'zero_scans': 144*components+17,
            'transitions_upper': components*(2298*width+4722)+34*width+132,
            'scratch_cells': 17*(width+1),
            'owner_cells': 112*(components*(width+1)+1), 'bound_cells': width+1}


def component(owner_words, scratch, bound, program, source):
    width = source.word_width(bound)
    need(len(owner_words) == 112 and len(scratch) == 17, 'Owner and scratch counts')
    words = owner_words + scratch
    need(len({id(w) for w in words}) == len(words), 'Word aliases')
    for word in words:
        source.check_word(word, width)
    limit = source.encode(bound, width)
    for word in owner_words:
        need(source.within_bound(word, limit, words[128]), 'Input range')
    (gather, gp), (scatter, sp) = program
    for instruction in gather:
        signed_sum(words, instruction)
    for mode in words[112:120]:
        source.round52_into(mode, words[128])
    for instruction in scatter:
        signed_sum(words, instruction)
    for word in words[112:128]:
        source.clear(word)
    need(not any(words[128]), 'Divider return')
    return {'gather': len(gather), 'scatter': len(scatter), 'peak_temporaries': max(gp, sp)}


def recode_many(owner_records, scratch, bound, columns, source):
    width = source.word_width(bound)
    need(len(owner_records) == 112 and len(scratch) == 17, 'Record geometry')
    count = len(owner_records[0])
    need(all(len(row) == count for row in owner_records), 'Aligned records')
    all_words = [w for row in owner_records for w in row] + scratch
    need(len({id(w) for w in all_words}) == len(all_words), 'Record aliases')
    for word in all_words:
        source.check_word(word, width)
    for word in scratch:
        source.clear(word)
    program = emit(columns)
    receipt = {'gather': len(program[0][0]), 'scatter': len(program[1][0]),
               'peak_temporaries': max(program[0][1], program[1][1])}
    for coordinate in range(count):
        got = component([row[coordinate] for row in owner_records], scratch, bound, program, source)
        need(got == receipt, 'Fixed program receipt')
    return {**receipt, **invoice(width, count)}
