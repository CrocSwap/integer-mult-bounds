# Two paid Q8 rank-one factors do not realize `diag(i,j,k)`

**Result: scoped finite exclusion in an abstract noncommutative register model.**
Each paid factor has unit cost in the model below. Exhausting all 38,416 ordered
two-factor words finds no realization of the three-register diagonal target.
The nearest word outputs have coefficient Hamming distance two. One factor is
also excluded by a complete 196-word census, and three factors realize the
target, so the minimum is exactly three in this alphabet.

## Model and statement

Work in the group algebra `F2[Q8]`, with labels ordered
`1,i,j,k,-1,-i,-j,-k`. For each binary rank-one idempotent
`N = x y^T` with `x,y in F2^3` and `y^T x = 1`, and each nonidentity
`g in Q8`, define the paid factor

```text
D_N(g) = I + (g + 1) N.
```

There are 28 such idempotents and seven allowed group labels. The exact
question is whether any ordered pair `D_N(g) D_M(h)` equals
`diag(i,j,k)` as a 3-by-3 matrix over the group algebra. Equality is checked
coefficient by coefficient in all 72 binary coordinates (nine matrix entries
times eight Q8 labels).

**Finite result.** No one- or two-factor word equals the target. The one-factor
census covers `28 * 7 = 196` words and has minimum coefficient Hamming distance
four. The two-factor census covers `28 * 7 * 28 * 7 = 38,416` words and reports
minimum distance two; six words attain that distance. The ordered two-factor
outputs have SHA-256
`2dad5d3c5068f65b2cd18be66ddef342cd38cce13b07b36c270bd9c99c845305`. The boundary control
`D_E11(i) D_E22(j) D_E33(k) = diag(i,j,k)` verifies that three paid factors
suffice. Thus three is the exact minimum under this factor-count convention.

This changes the label algebra to the nonabelian quaternion group while keeping
three binary register roles and the 28 rank-one idempotents familiar from the
abelian three-register work. It is a narrower, different alphabet census than
the GL3 two-role model in [the mixed-target predecessor](../bit-gl3-mixed-targets-length10/README.md)
and the all-rational-frame result in [the three-register predecessor](../bit-three-register-lower-bound/README.md).
The nearest active overlap is [PR #2248](https://github.com/CrocSwap/integer-mult-bounds/pull/2248),
which studies `diag(-1,-1,i/j)` and `diag(-1,-1,-1)` with paid labels `{i,j}`
and proves minima five and six. This package instead studies `diag(i,j,k)` and
allows every nonidentity Q8 label, exhausting only lengths one and two. The
claim and scope history are in [Discussion #2300](https://github.com/CrocSwap/integer-mult-bounds/discussions/2300).

## Cost and limits

Each `D_N(g)` is charged one abstract factor unit, with no free factor inserted
between calls. This model does not price a physical supplier, recursive child,
source access, register conversion, hosting, restoration or precision. No such
supplier is established here, and this result does not change the selected
conditional bound or `kappa`. It only rules out one- and two-factor
realizations of this target in the stated finite alphabet.

The verifier is an exact finite computation, not a proof-assistant certificate
or a universal statement about other groups, register counts, additional free
operations, or longer words.

## Cycle pins

- Seed: `189ad74f7eb7b99d43830c0ed0f15958`; track: `bit-mechanisms`;
  catalogue task: `bit-new-register-model`; priority revision: 4.
- Base commit: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`.
- Task-catalogue SHA-256: `d46eb6d5b3e279428753d770653663fbdf1063e55c255ea073d768f344927ef7`.
- Selected-record SHA-256: `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.

## Reproduce

From the repository root, regenerate the search receipt and independently
replay it using set-based group-algebra arithmetic:

```sh
python3 -B research/bit-q8-three-register-two-call-seed189ad74/search.py
python3 -B research/bit-q8-three-register-two-call-seed189ad74/verify.py
python3 scripts/research_package.py --package research/bit-q8-three-register-two-call-seed189ad74 --check-only
```

The verifier checks the literal Q8 multiplication table and associativity,
idempotent coverage, the one- and two-factor censuses, the three-factor positive
control, the output digest, and rejection of a non-idempotent rank-one control. Source
commits, blobs and hashes are pinned in [SOURCES.json](SOURCES.json). The
selected record and task catalogue are historical provenance pins.

## Open next questions

If a physical supplier for Q8-labeled factors is found, can one `D_N(g)` be
implemented with a complete all-size interface at less than one rank-one
factor's cost after conversion and restoration? This determines whether the
nonabelian label model can affect the multiplication bound. The first step is
to map one factor to a source and interface schedule and fully charge it. The
current blocker is that this package identifies no such supplier. This is
recorded with its first step and blocker in the structured
[task metadata](TASK.json#L57).

## Credit

Prepared by Cinna Davis with substantial OpenAI Codex assistance. The model
choice and finite scope were recorded in Discussion #2300. New work is
Apache-2.0; cited predecessor work remains attributed to its authors.
