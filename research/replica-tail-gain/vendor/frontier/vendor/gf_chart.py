# SPDX-License-Identifier: Apache-2.0
# Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
# Exact GF(2) chart utilities extracted from PR2436 census.py; unchanged functions.

def gf_rank(xs):
    b = {}
    for x in xs:
        while x:
            j = x.bit_length()
            if j not in b:
                b[j] = x
                break
            x ^= b[j]
    return len(b)

def gf_extend(xs, h):
    out = list(xs)
    for j in range(h):
        if gf_rank(out + [1 << j]) > len(out):
            out.append(1 << j)
    assert len(out) == h
    return out

def gf_linear(cols, x):
    out = 0
    for j, c in enumerate(cols):
        if x >> j & 1:
            out ^= c
    return out

def gf_change(source, target, h):
    a, b = gf_extend(source, h), gf_extend(target, h)
    back = {gf_linear(a, x): x for x in range(1 << h)}
    assert len(back) == 1 << h
    return [gf_linear(b, back[1 << j]) for j in range(h)]
