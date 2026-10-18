# Isolated X4 pair: algebra, primitive minimum, and local prefix guard

This claim concerns exactly two scalar registers, with no scratch register,
no free permutation, and unit cost for each of the ten instructions
`x += y`, `x -= y`, `y += x`, `y -= x`, and `NEG`, `HALF`, `DOUBLE` on either
register. It does not establish optimality of the full PR799 circuit or any
new multiplication bound. Source: base `f567884aeb8851b6e794af1184119a3bfbe1e631`,
the two pinned `native/local` JSON members of
`research/community-frontier799-audit/integrated799-replay.tar.gz`.

## Exact map and replacement

For an input column `(u,v)`, the archived forward triple is

```
x *= -1/2;  x += y/2;  y -= x.
```

It produces `((-u+v)/2, (u+v)/2)`, hence

```
A = (1/2) [-1  1]       A^(-T) = B = [-1  1].
          [ 1  1]                     [ 1  1]
```

The replacement forward primitive word is

```
x -= y;  NEG x;  HALF x;  y -= x.
```

Its four intermediate states are `(u-v,v)`, `(-u+v,v)`,
`((-u+v)/2,v)`, and `((-u+v)/2,(u+v)/2)`.

The letterwise inverse-transpose word, in the same chronological order, is

```
y += x;  NEG x;  DOUBLE x;  x += y.
```

It produces `(u,u+v)`, `(-u,u+v)`, `(-2u,u+v)`, and `(-u+v,u+v)`.
The archived backward triple `x *= -2; y -= x/2; x += y` has this same map.
Indeed `(G_n ... G_1)^(-T) = G_n^(-T) ... G_1^(-T)`; this explains why
letterwise inverse transposition preserves chronological order here.

## Four primitives are necessary

The determinant of `A` is `-1/2`; that of `B` is `-2`. In the declared
alphabet, an ADD has determinant `1`, NEG has determinant `-1`, HALF has
determinant `1/2`, and DOUBLE has determinant `2`. Each target therefore
requires at least one NEG and at least one HALF or DOUBLE. These are two
distinct diagonal instructions. Starting from the identity, a word with
at most one ADD and arbitrarily many diagonal instructions has at most
three nonzero matrix entries. Both target matrices have four nonzero
entries, so each also requires at least two ADDs. The lower bound is four,
attained by the words above. The argument does not presume a finite search
cutoff, but its scope remains exactly this two-register alphabet.

The independent checker cross-checks that argument in exact `Fraction`
arithmetic. BFS has first-seen frontier sizes `1,10,69,370,1646` at depths
0 through 4. Both targets first occur at depth 4. Independently enumerating
all `1+10+100+1000+10000 = 11111` words through length 4 finds exactly eight
shortest words for each target. There is no coefficient-size pruning.

For comparison, compiling the three original rational instructions
independently costs at least `2+3+1 = 6` primitives per scalar pair, in
either direction. A signed half/double needs the corresponding scale
and NEG. A half-ADD needs at least one HALF to introduce a fraction,
at least one DOUBLE to restore determinant one, and at least one ADD;
`HALF source; ADD destination, source; DOUBLE source` attains three.
The last unit ADD costs one. BFS independently confirms these minima.
Thus the fused word saves two primitives per scalar pair against that
specific gatewise baseline. For 56 disjoint scalar pairs this is 112
per orientation; applying the same words separately to real and imaginary
coordinates doubles both counts. This comparison is not a lower bound
for other whole-block implementations.

## Prefix and fraction guard

The guard here is the maximum absolute row sum of the matrix mapping the
two input registers to any intermediate state, including the input.

| Map and word | Maximum row sum | Maximum reduced denominator |
|---|---:|---:|
| Original rational forward | 1 | 2 |
| Fused primitive forward | 2 | 2 |
| Original rational backward | 2 | 1 |
| Fused primitive backward | 2 | 1 |

Every one of the eight shortest forward words has peak row sum 2 and
maximum denominator 2; every shortest backward word has peak row sum 2
and integer matrix entries. Thus a four-instruction replacement cannot
retain a local forward row-sum guard of 1. For example `(u,v)=(1,-1)`
already gives `x=2` after the first replacement instruction.

For arbitrary entry row vectors `u,v` with individual row sums at most
`M`, the displayed words have intermediate row sums at most `2M`.
If all entry coefficients have common denominator `D`, all forward
prefix denominators divide `2D`; all backward prefix denominators divide
`D`. These are local bounds; a global guard must be checked against the
actual entry state and all unchanged circuit phases.

## Reproduction and source checks

Run `python3 research/x4-precondition-seed22/independent_checker.py` from
the repository root (or run the script by absolute path). The checker
uses only the Python standard library and imports no integration code.
It verifies the archive SHA-256, both compressed member hashes, the exact
56 original pair triples, their 112 distinct registers, and the matching
first 168 scalar instructions in both archived programs. It then checks
the algebra, duality, exhaustive minima, all shortest-word local guards,
and three negative controls: missing NEG, wrong first ADD sign, and the
false forward prefix guard of 1. Its JSON result is `PASS` on the pinned
source; malformed or changed source data is rejected.
