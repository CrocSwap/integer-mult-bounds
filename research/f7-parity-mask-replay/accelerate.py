#!/usr/bin/env python3
"""Source-pinned opt-in parity-mask adapter; frozen census is never edited.

Tekalign, with substantial OpenAI Codex assistance. Apache-2.0.
Derived census remains Nicholas Stone's PR2973 implementation.
"""
import hashlib
from pathlib import Path


PERMUTATION = r'''
/* On a fixed Hamming-parity coset x -> x>>1 is bijective.
 * epoints/opoints encode (point XOR q)>>1 at the CURRENT walk origin q;
 * ee/oo/eo encode global pair differences. A label-j step permutes the
 * point masks by XOR ((1<<j)>>1). The new current point has index zero.
 * E/O retain their original GLOBAL parity labels, including after a move. */
static mask_t epoints=1, opoints;
static inline mask_t step_translate(mask_t x, unsigned label) {
    static const mask_t low[7] = {0,
        UINT64_C(0x5555555555555555), UINT64_C(0x3333333333333333),
        UINT64_C(0x0f0f0f0f0f0f0f0f), UINT64_C(0x00ff00ff00ff00ff),
        UINT64_C(0x0000ffff0000ffff), UINT64_C(0x00000000ffffffff)};
    if (!label) return x;
    unsigned shift=1u<<(label-1);
    return ((x&low[label])<<shift)|((x>>shift)&low[label]);
}
'''


def rewrite(source):
    """Exact anchors fail closed; caller authenticates complete input bytes."""
    edits = [
        ('typedef unsigned __int128 mask_t;', 'typedef uint64_t mask_t;'),
        ('static mask_t seen=1, ee,oo,eo;',
         'static unsigned __int128 seen=1;\nstatic mask_t ee,oo,eo;'),
        ('return __builtin_popcountll((uint64_t)x)+__builtin_popcountll((uint64_t)(x>>64));',
         'return __builtin_popcountll(x);'),
        ('static inline mask_t bit(int x) { return (mask_t)1 << x; }',
         'static inline unsigned __int128 bit(int x) { return (unsigned __int128)1 << x; }\n'+PERMUTATION),
        ('if (pop(ee|oo|eo|1)==(1<<N)) {',
         'if (pop(ee|oo|1)+pop(eo)==(1<<N)) {'),
        ('mask_t add_same=0,add_cross=0;',
         'mask_t add_same=0,add_cross=0;\n        mask_t next_e=step_translate(epoints,(unsigned)j), next_o=step_translate(opoints,(unsigned)j);'),
        ('''            const int *same=p?O:E, *cross=p?E:O;
            int same_size=p?os:es,cross_size=p?es:os;
            for (int a=0;a<same_size;a++) add_same|=bit(nq^same[a]);
            for (int a=0;a<cross_size;a++) add_cross|=bit(nq^cross[a]);''',
         '''            add_same=p?next_o:next_e;
            add_cross=p?next_e:next_o;'''),
        ('mask_t old_seen=seen,old_ee=ee,old_oo=oo,old_eo=eo;',
         'unsigned __int128 old_seen=seen;\n        mask_t old_ee=ee,old_oo=oo,old_eo=eo,old_epoints=epoints,old_opoints=opoints;\n        epoints=next_e; opoints=next_o;'),
        ('if (p) { O[os++]=nq; oo|=add_same; }',
         'if (p) { O[os++]=nq; opoints|=1; oo|=add_same; }'),
        ('else { E[es++]=nq; ee|=add_same; }',
         'else { E[es++]=nq; epoints|=1; ee|=add_same; }'),
        ('seen=old_seen; ee=old_ee; oo=old_oo; eo=old_eo;',
         'seen=old_seen; ee=old_ee; oo=old_oo; eo=old_eo; epoints=old_epoints; opoints=old_opoints;'),
        ('seen=1; ee=oo=eo=0; current=&shards[a];',
         'seen=1; ee=oo=eo=0; epoints=1; opoints=0; current=&shards[a];'),
    ]
    for old, new in edits:
        if source.count(old) != 1:
            raise ValueError('census source anchor absent or ambiguous: '+old)
        source = source.replace(old, new)
    return source


def authenticate(path, expected):
    data = Path(path).read_bytes()
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError('source SHA256 mismatch: '+str(path))
    return data.decode()


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source', type=Path)
    p.add_argument('sha256')
    p.add_argument('output', type=Path)
    a = p.parse_args()
    result = rewrite(authenticate(a.source, a.sha256))
    with a.output.open('x') as f:
        f.write(result)
