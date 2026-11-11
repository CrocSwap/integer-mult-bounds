#!/usr/bin/env python3
"""Legal S(16) is impossible for a floor word realizing every weight-2 mask and the weight-6 mask.

Evidence class: exhaustive finite census. The C enumerator and, for the
two-zero centre shape, an independent Python enumerator both report no witness.
Failures are SystemExit, so python -O cannot silence them. The PR #6216
empty-fibre certificate is not read.
"""

import itertools
import subprocess
import sys
import tempfile
from functools import lru_cache
from pathlib import Path

K = 6
LENGTH = 30
A = (0, 1, 5, 6, 10)
EDGES = [(i, j) for i in range(K) for j in range(i + 1, K)]
EIDX = {pair: i for i, pair in enumerate(EDGES)}
SORTED = '000001111122222333334444455555'
WEIGHT2_LEGAL = '001211112322203343354444555500'
WEIGHT6_LEGAL = '012300333300112241122545545544'
HERE = Path(__file__).resolve().parent


def fail(msg):
    raise SystemExit('FAIL: ' + msg)


def res(v):
    return 0 if v == 5 else v


def prefixes(word):
    counts = [0] * K
    out = [tuple(counts)]
    for ch in word:
        counts[int(ch)] += 1
        out.append(tuple(counts))
    return out


def mask_bits(sum_vec):
    bits = []
    for value in sum_vec:
        if value in (1, 6):
            bits.append(1)
        elif value in (0, 5, 10):
            bits.append(0)
        else:
            return None
    return tuple(bits)


def scan(word):
    if len(word) != LENGTH or any(word.count(str(j)) != 5 for j in range(K)):
        fail('not a floor word: ' + word)
    pref = prefixes(word)
    found = set()
    for s in range(LENGTH):
        for t in range(s, LENGTH):
            bits = mask_bits(tuple(pref[s][j] + pref[t][j] for j in range(K)))
            if bits is not None and sum(bits) in (2, 6):
                found.add(bits)
    q = pref[16]
    letter = int(word[16])
    centre = tuple(2 * q[j] + (j == letter) for j in range(K))
    w2 = sum(sum(mask) == 2 for mask in found)
    w6 = sum(sum(mask) == 6 for mask in found)
    return {
        'w2': w2,
        'w6': w6,
        'q16': q,
        'letter': letter,
        'centre': centre,
        'legal': all(value in A for value in centre),
    }


def legal_centre_census():
    pairs = []
    for counts in itertools.product(range(6), repeat=K):
        if sum(counts) != 16:
            continue
        for letter in range(K):
            if counts[letter] >= 5:
                continue
            centre = tuple(2 * counts[j] + (j == letter) for j in range(K))
            if all(value in A for value in centre):
                pairs.append((counts, letter, centre))
    return pairs


def arithmetic_shapes():
    """The only legal count patterns, from the two-row equations in the README."""
    found = []
    # Centre letter count 0. The other five coordinates lie in {0,3,5} and sum to 16.
    for n5 in range(6):
        for n3 in range(6 - n5):
            n0 = 5 - n5 - n3
            if 5 * n5 + 3 * n3 == 16:
                found.append(('r0', n5, n3, n0))
    # Centre letter count 2. The other five coordinates sum to 14.
    for n5 in range(6):
        for n3 in range(6 - n5):
            n0 = 5 - n5 - n3
            if 5 * n5 + 3 * n3 == 14:
                found.append(('r2', n5, n3, n0))
    return found


def canonical_prefix_count(mode):
    """Count first-occurrence canonical length-16 prefixes of one legal shape."""
    if mode == 0:
        @lru_cache(maxsize=None)
        def dp(n, c0, c1, c2, c3, nxt):
            if n == 16:
                return int(sorted((c0, c1, c2, c3), reverse=True) == [5, 5, 3, 3] and nxt == 4)
            total = 0
            cs = [c0, c1, c2, c3]
            for j in range(4):
                if cs[j] >= 5 or (cs[j] == 0 and j > nxt):
                    continue
                cs[j] += 1
                nn = nxt if cs[j] > 1 else (j + 1 if j == nxt else nxt)
                total += dp(n + 1, cs[0], cs[1], cs[2], cs[3], nn)
                cs[j] -= 1
            return total
        return dp(0, 0, 0, 0, 0, 0)

    @lru_cache(maxsize=None)
    def dp2(n, c0, c1, c2, c3, c4, nxt):
        if n == 16:
            return int(sorted((c0, c1, c2, c3, c4), reverse=True) == [5, 3, 3, 3, 2] and nxt == 5)
        total = 0
        cs = [c0, c1, c2, c3, c4]
        for j in range(5):
            if cs[j] >= 5 or (cs[j] == 0 and j > nxt):
                continue
            cs[j] += 1
            nn = nxt if cs[j] > 1 else (j + 1 if j == nxt else nxt)
            total += dp2(n + 1, cs[0], cs[1], cs[2], cs[3], cs[4], nn)
            cs[j] -= 1
        return total
    return dp2(0, 0, 0, 0, 0, 0, 0)


def hand_edge_death():
    """On the weight-6 legal word, edge {1,3} is already impossible at depth 12.

    This is one concrete case of the future-box test, small enough to read.
    It is not the census.
    """
    word = WEIGHT6_LEGAL[:12]
    counts = [0] * K
    seen = [tuple(0 for _ in range(K))]
    for ch in word:
        counts[int(ch)] += 1
        seen.append(tuple(res(counts[j]) for j in range(K)))
    if counts != [5, 1, 1, 5, 0, 0]:
        fail('hand prefix counts changed: ' + str(counts))
    # Sources 0 and 3 are finished, so two future prefixes have residue 0 there.
    # Mask bit 1 on source 3 therefore needs a past residue 1. Those prefixes
    # are exactly the ones below, and each has a nonzero residue on the finished
    # source 0, which can no longer supply the residue 0 that mask bit 0 needs.
    partners = [d for d in seen if d[3] == 1]
    if [d[0] for d in partners] != [1, 2, 3]:
        fail('hand partners changed: ' + str(partners))
    for digits in partners:
        if digits[0] == 0:
            fail('a residue-1 prefix on source 3 kept residue 0 on source 0')
    return len(partners)


def python_mode0():
    """Independent enumerator for the two-zero legal shape. Same prune as census.c."""
    counts = [0] * K
    seen = [tuple(0 for _ in range(K))]
    realized = 0
    got_w6 = 0
    examined = 0
    alive = 0
    solutions = 0
    nodes = 0

    def partners(digits, bits):
        for j in range(K):
            want = (((bits >> j) & 1) - digits[j]) % 5
            if want and counts[j] > want:
                return False
        return True

    def all_alive():
        if not got_w6 and any(counts[j] >= 4 for j in range(K)):
            if not any(partners(digits, 63) for digits in seen):
                return False
        need = (~realized) & ((1 << 15) - 1)
        edge = 0
        while need:
            if need & 1:
                a, b = EDGES[edge]
                if counts[a] >= 4 or counts[b] >= 4:
                    if not any(partners(digits, (1 << a) | (1 << b)) for digits in seen):
                        return False
            need >>= 1
            edge += 1
        return True

    def absorb(nr):
        nonlocal realized, got_w6
        for digits in seen:
            bits = 0
            good = True
            weight = 0
            for j in range(K):
                s = (digits[j] + nr[j]) % 5
                if s > 1:
                    good = False
                    break
                if s:
                    bits |= 1 << j
                    weight += 1
            if not good:
                continue
            if weight == 6:
                got_w6 = 1
            elif weight == 2:
                a = (bits & -bits).bit_length() - 1
                b = (bits ^ (1 << a)).bit_length() - 1
                realized |= 1 << EIDX[(a, b)]

    def shape():
        c5 = c3 = c0 = other = 0
        for value in counts:
            if value == 5:
                c5 += 1
            elif value == 3:
                c3 += 1
            elif value == 0:
                c0 += 1
            else:
                other += 1
        return c5 == 2 and c3 == 2 and c0 == 2 and other == 0

    def rec_suf(depth, nxt):
        nonlocal nodes, solutions, realized, got_w6
        nodes += 1
        if depth == LENGTH:
            if realized == (1 << 15) - 1 and got_w6:
                solutions += 1
            return
        for j in range(K):
            c = counts[j]
            if c >= 5 or (c == 0 and j > nxt):
                continue
            counts[j] = c + 1
            nr = tuple(res(counts[t]) for t in range(K))
            save_r, save_w = realized, got_w6
            seen.append(nr)
            absorb(nr)
            if c == 0 or all_alive():
                rec_suf(depth + 1, nxt if c else j + 1)
            seen.pop()
            realized, got_w6 = save_r, save_w
            counts[j] = c
            if solutions:
                return

    def rec(depth, nxt):
        nonlocal examined, alive, realized, got_w6
        if depth == 16:
            if not shape():
                return
            used = sum(value > 0 for value in counts)
            for letter in range(K):
                if counts[letter] >= 5 or (counts[letter] == 0 and letter != used):
                    continue
                centre = tuple(2 * counts[j] + (j == letter) for j in range(K))
                if any(value not in A for value in centre):
                    continue
                examined += 1
                c = counts[letter]
                counts[letter] = c + 1
                nr = tuple(res(counts[t]) for t in range(K))
                save_r, save_w = realized, got_w6
                seen.append(nr)
                absorb(nr)
                if all_alive():
                    alive += 1
                    rec_suf(17, nxt if c else letter + 1)
                seen.pop()
                realized, got_w6 = save_r, save_w
                counts[letter] = c
                if solutions:
                    return
            return
        for j in range(K):
            c = counts[j]
            if c >= 5 or (c == 0 and j > nxt):
                continue
            positive = above3 = 0
            for t in range(K):
                value = counts[t] + (t == j)
                positive += value > 0
                above3 += value > 3
            if positive > 4 or above3 > 2:
                continue
            counts[j] = c + 1
            nr = tuple(res(counts[t]) for t in range(K))
            save_r, save_w = realized, got_w6
            seen.append(nr)
            absorb(nr)
            rec(depth + 1, nxt if c else (j + 1 if j == nxt else nxt))
            seen.pop()
            realized, got_w6 = save_r, save_w
            counts[j] = c
            if solutions:
                return

    rec(0, 0)
    return examined, alive, nodes, solutions


def start_c_census():
    work = Path(tempfile.mkdtemp(prefix='c5-joint-s16-'))
    binary = work / 'census'
    compiled = subprocess.run(
        ['gcc', '-O3', '-std=c11', '-o', str(binary), str(HERE / 'census.c')],
        capture_output=True, text=True,
    )
    if compiled.returncode != 0:
        fail('gcc failed: ' + compiled.stderr[-500:])
    return subprocess.Popen([str(binary)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def finish_c_census(proc):
    stdout, stderr = proc.communicate()
    if proc.returncode != 0:
        fail('census failed: ' + stderr[-500:] + stdout[-500:])
    if 'PASS_C5_JOINT_MASK_S16_CENSUS solutions=0' not in stdout:
        fail('census marker missing: ' + stdout[-500:])
    if 'mode 0 examined 10090080 alive 8793 nodes 31821 solutions 0' not in stdout:
        fail('mode 0 line changed: ' + stdout)
    if 'mode 1 examined 67267200 alive 13496310 nodes 419423032 solutions 0' not in stdout:
        fail('mode 1 line changed: ' + stdout)
    return stdout


def controls():
    for x, y in itertools.product(range(6), repeat=2):
        total = x + y
        in_a = total in A
        congruent = (res(x) + res(y)) % 5 <= 1
        if in_a != congruent:
            fail('residue equivalence failed on %s+%s' % (x, y))
    pairs = legal_centre_census()
    if len(pairs) != 300:
        fail('legal centre count %s' % len(pairs))
    shapes = {tuple(sorted(counts, reverse=True)) for counts, _letter, _centre in pairs}
    if shapes != {(5, 5, 3, 3, 0, 0), (5, 3, 3, 3, 2, 0)}:
        fail('legal shapes changed: ' + str(shapes))
    for counts, letter, _centre in pairs:
        if counts[letter] not in (0, 2):
            fail('centre letter count left {0,2}')
        if 0 not in counts:
            fail('legal centre without a zero coordinate')
    equations = arithmetic_shapes()
    if equations != [('r0', 2, 2, 1), ('r2', 1, 3, 1)]:
        fail('shape equations changed: ' + str(equations))
    near = (3, 3, 3, 3, 3, 1)
    if any(all(2 * near[j] + (j == letter) in A for j in range(K)) for letter in range(K) if near[letter] < 5):
        fail('near-miss centre was accepted')
    if canonical_prefix_count(0) != 10090080 or canonical_prefix_count(1) != 67267200:
        fail('canonical prefix counts changed')
    sorted_info = scan(SORTED)
    if sorted_info['w2'] != 15 or sorted_info['w6'] != 0 or sorted_info['legal']:
        fail('sorted word changed: ' + str(sorted_info))
    if sorted_info['centre'] != (10, 10, 10, 3, 0, 0):
        fail('sorted centre changed')
    legal_info = scan(WEIGHT2_LEGAL)
    if legal_info['w2'] != 15 or legal_info['w6'] != 0 or not legal_info['legal']:
        fail('weight-2 legal word changed: ' + str(legal_info))
    if legal_info['centre'] != (6, 10, 10, 6, 1, 0):
        fail('weight-2 legal centre changed')
    weight6 = scan(WEIGHT6_LEGAL)
    if weight6['w6'] != 1 or weight6['w2'] == 15 or not weight6['legal']:
        fail('weight-6 legal word changed: ' + str(weight6))
    if weight6['centre'] != (10, 6, 6, 10, 1, 0) or weight6['w2'] != 5:
        fail('weight-6 legal details changed: ' + str(weight6))
    if hand_edge_death() != 3:
        fail('hand edge death count changed')
    return len(pairs)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'full'
    census_proc = start_c_census()
    centres = controls()
    python_solutions = None
    if mode == 'full':
        examined, alive, nodes, python_solutions = python_mode0()
        if (examined, alive, nodes, python_solutions) != (10090080, 8793, 31821, 0):
            census_proc.kill()
            fail('python mode 0 changed: %s %s %s %s' % (examined, alive, nodes, python_solutions))
    elif mode != 'c-only':
        census_proc.kill()
        fail('unknown mode ' + mode)
    compiled = finish_c_census(census_proc)
    if 'solutions 0' not in compiled:
        fail('C census reported a solution')
    py = 'na' if python_solutions is None else str(python_solutions)
    print(
        'PASS_C5_JOINT_MASK_S16 centres=%s shapes=2 canonical_r0=10090080 '
        'canonical_r2=67267200 python_mode0_solutions=%s c_solutions=0 '
        'legal_centre_impossible=1 mode=%s'
        % (centres, py, mode)
    )


if __name__ == '__main__':
    main()
