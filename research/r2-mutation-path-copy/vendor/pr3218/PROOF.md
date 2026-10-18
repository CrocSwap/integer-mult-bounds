# Exact Clifford equality from signed Pauli action and one anchor

The complete criterion below is established Clifford algebra, already used by
the retained native producer's tableau and zero-column check. This package
does not claim its discovery. It implements the criterion separately for
Sagar Thakrar's PR1781 gate grammar, then substitutes that comparator into
24kHandsome1201's source-bound PR3202 audit. The intended contribution is
measured verification engineering, with exact coverage preserved.

## Domain and conventions

Basis labels are `x in F_2^n`, bit zero first. The implementation accepts
`1 <= n <= 9`; its current caller uses `n=9`. Gates are chronological:

- `P(G)|x> = |Gx>` for an invertible binary row matrix `G`.
- `X(b)|x> = |x+b>`.
- `D(Q,a)|x> = i^q(x)|x>`, where
  `q(x)=sum_j a_j x_j + 2 sum_{j<k} Q_jk x_j x_k (mod 4)`.
  Only the strict upper triangle of `Q` is read, exactly as in PR1781.
- `PH(p)=i^p I`.
- `C(v,s)=((1+s i)I+(1-s i)X(v))/2`, with `v != 0` and `s=+1` or `-1`.

The first four gates are unitary. `X(v)` is a Hermitian involution, and the
two eigenvalues of `C(v,s)` are `1` and `s i`; hence it too is unitary.
The validator checks both entire input words, including permutation
invertibility, before comparing them. This excludes unsupported non-Clifford
gates and prevents a mismatch early in a word from hiding a malformed gate.

Write a Pauli as `W(p,x,z)=i^p X(x) Z(z)`, so
`W(p,x,z)|y> = i^(p+2 z dot y)|y+x>`.
Its full phase modulo four is stored. Discarding that phase is unsound.

## Signed conjugation rules

The initial list consists of `X(e_j)` and `Z(e_j)` for every coordinate.
For each gate `A` replace every stored Pauli by `A W A^*`. Chronological
updates therefore produce the generator images under the complete word.

| Gate | Updated `(p,x,z)` |
|---|---|
| `P(G)` | `(p, Gx, G^(-T)z)` |
| `X(b)` | `(p+2 z dot b, x, z)` |
| `PH(k)` | `(p,x,z)` |
| `D(Q,a)` | `(p+q(x), x, z+B x)` |
| `C(v,s)`, if `z dot v=0` | `(p,x,z)` |
| `C(v,s)`, if `z dot v=1` | `(p-s, x+v, z)` |

Phases are reduced modulo four and binary coordinates modulo two. Here `B`
is symmetric with diagonal `a_j mod 2` and off-diagonal entries the strict
upper-triangle coefficients of `Q`, reflected across the diagonal.

For the diagonal gate, direct expansion gives

```
q(y+x)-q(y) = q(x) + 2 (Bx) dot y (mod 4),
```

which proves the stated rule. For `C`, put `T=X(v)`. A Pauli either commutes
or anticommutes with `T`. The commuting case is unchanged. In the other case,
expanding `((1+s i)I+(1-s i)T) W ((1-s i)I+(1+s i)T)/4`
gives `-s i T W`, which is exactly the last row. These derivations determine
the signs; they are not inferred by ignoring global phases in a tableau.

## Why the comparison covers every input

Let `U,V` be two accepted words. Suppose their **signed** images of every
`X(e_j)` and `Z(e_j)` agree. Then `V^* U` commutes with all those generators.
Commuting with all `Z(e_j)` forces its matrix to be diagonal: distinct basis
labels have distinct joint sign eigenvalues. Commuting also with all
`X(e_j)` makes its diagonal entries equal along every edge of the binary
cube. That cube is connected, so `V^* U=lambda I` and `U=lambda V`.

The additional equality `U|0>=V|0>` forces `lambda=1`, since `V|0>` is
nonzero. Thus the signed generator images plus **one exact anchor vector**
are a necessary and sufficient test of operator equality, including global
phase. At nine axes, this covers all 512 input basis columns and every complex
linear combination without constructing those 512 columns individually.

This relies on the validated Clifford gate grammar. It is not a method for
checking arbitrary linear operators from 18 generators and one sample.
Nor is it a polynomial-time implementation claim: the anchor representation
can contain `2^n` amplitudes. The implemented domain is bounded at nine axes.

## Exact anchor arithmetic and table reuse

`anchor` starts with `{0: (1,0)}`. Its state is a sparse Gaussian-integer
numerator vector with common denominator `2^k`, where `k` is the number of
`C` gates already applied. Permutations, translations and fourth-root phases
preserve that denominator. Each `C` applies its literal numerator formula
and increments `k`; exact zeros are removed. No rounding, floating point,
norm tolerance or projective normalization occurs.

Two anchors are compared after multiplication to the common denominator
`2^max(k,l)`. Python integers do not overflow. Equality tests retain every
nonzero coordinate, including the possibility that coordinate zero itself
vanishes; testing just the scalar amplitude at coordinate zero would not
suffice.

The bounded 64-entry cache contains only immutable gate tables. For a binary
permutation, `Gx=G(x-e_j)+G e_j` at the least set bit `j`. For a quadratic
phase, `q(x)=q(x-e_j)+a_j+2 sum_{k != j} B_jk x_k`. These are the known
binary recurrences used by Charles Bethin/#662 and ywz65/#2638, coded here
for the comparator's gate representation. Keys include dimension and every
operand. Caller-owned lists are frozen before use. No new acceptance-result
or state-vector cache is introduced. The retained audit's own full-circuit
deduplication is unchanged.

## Current-caller integration and limitations

`replay.py` authenticates all 25 source/input files before running any retained
code, copies the captured bytes into a fresh private snapshot, and loads the
unchanged PR3202 verifier with one explicit installation statement immediately
after its kernel initialization. The source anchor must occur exactly once.
The hook substitutes only `same_operator`; all source/event binding, canonical
frame construction, both orientations, the scalar restoration control, recipe
coverage, wrapper chronology and sixteen semantic mutants per provider remain.

Three modes run that identical caller: original packed kernel; the existing
#2638 table-cached packed kernel; and the new comparator. Every mode must
reproduce the entire original result. The benchmark also matches the multiset
of actual circuit pairs and Boolean decisions, with multiplicity. It uses
fresh serial processes and alternates order. Timing has no acceptance threshold.

The nested predecessor result retains its historical kernel hash; the enclosing
receipt separately identifies the actual mode, new engine, transformed verifier
and all captured source hashes. Its inherited `512`-column fields describe
the operator domain covered, not an assertion that the new engine explicitly
simulated 512 input columns. Native generation is outside this retained-artifact
benchmark; the source artifacts are authenticated on every replay.

This does not expand PR3202's scientific coverage, implement a fast recursive
multiplier, certify a supplier, or establish a new kappa. Native operations
outside the slice, physical ownership, complete cleanup, precision/tape and
outer/all-size obligations remain as in the predecessor.

## Executed failure and differential checks

`controls.py` uses the unchanged packed matrix implementation as an oracle
on 96 deterministic circuits (seed 86), dimensions one through four. It checks
`U P = image(P) U` for all generators on every input column: 480 signed Pauli
images and 4,704 matrix-column relations. It separately checks each complete
anchor vector and 480 comparator decisions, including adjoints and faults.
The small-dimensional computations are finite evidence for the implementation;
the preceding argument supplies the all-input implication for valid words.

Two controls expose the respective blind spots. `PH(1)` has identity Pauli
action but a different anchor. A nontrivial diagonal character fixes `|0>`
but changes a signed Pauli image. Its unsigned Pauli labels are unchanged,
so the latter control also detects dropping signs. Invalid gate, singular
matrix and mutable-cache-key controls fail explicitly under optimized Python.

Tekalign (@tekuuu), with substantial OpenAI Codex assistance. Apache-2.0.
No independent human or proof-kernel review is claimed.
