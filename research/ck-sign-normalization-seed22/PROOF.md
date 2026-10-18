# Boundary-local register-sign normalization

This note proves the exact-arithmetic local substitution implemented by this
package. It concerns the historical PR626 CK scalar words after the lowering in
`research/complex-dyadic-lowering/lower.py`; it does not establish a new
multiplication exponent or repair inherited physical interfaces.

Contribution: Ross Richardson (@RossRichardson), with substantial OpenAI Codex assistance. The scalar lowering
is due to Sagar Thakrar with substantial OpenAI Codex assistance; its credited
PR425/433/531, PR622 and PR626 circuit lineage remains applicable. New material
is under the repository's Apache-2.0 license. The present base commit is
`f567884aeb8851b6e794af1184119a3bfbe1e631`.

## Object and boundaries

A run consists of consecutive lowered scalar primitives in one unchanged frame.
It ends before every non-scalar event, before any scalar frame change, and at the
end of the program. No sign state may pass one of those boundaries. The
normalizer emits an ordinary finite word over the predecessor's existing
alphabet: clear, copy, double, halve, negate, add and subtract. Sign bookkeeping
is a compile-time calculation and is absent from the emitted circuit.

Let `x_r` be the logical contents of register `r` in the predecessor circuit and
`y_r` its physical contents in the emitted circuit. Maintain signs
`epsilon_r in {+1,-1}` and the invariant

```
x_r = epsilon_r * y_r.
```

All signs initially equal `+1`. This statement is about arbitrary values, or
entire symbolic linear rows; it does not assume clean registers, independent
current register values, or any particular input assignment.

## Inductive transition proof

For each predecessor primitive, emit the following operation and update only
the listed signs. Here `sigma=+1` denotes add and `sigma=-1` denotes subtract.

| Predecessor operation | Emitted operation | Sign update |
| --- | --- | --- |
| `x_t <- 0` | `y_t <- 0` | `epsilon_t <- +1` |
| `x_t <- x_s` | `y_t <- y_s` | `epsilon_t <- epsilon_s` |
| `x_t <- 2*x_t` | `y_t <- 2*y_t` | none |
| `x_t <- x_t/2` | `y_t <- y_t/2` | none |
| `x_t <- -x_t` | no operation | `epsilon_t <- -epsilon_t` |
| `x_t <- x_t + sigma*x_s` | `y_t <- y_t + sigma*epsilon_t*epsilon_s*y_s` | none |

Clear satisfies the invariant because both sides are zero; resetting its sign
also avoids pointless later restoration. Copy satisfies it because
`epsilon_s*y_s=x_s`, including when the target previously had a different sign.
Doubling and halving commute with multiplication by a sign. Negation is exactly
represented by toggling the logical interpretation. For the final row,

```
epsilon_t * (y_t + sigma*epsilon_t*epsilon_s*y_s)
 = epsilon_t*y_t + sigma*epsilon_s*y_s
 = x_t + sigma*x_s,
```

using `epsilon_t^2=1`. Thus the invariant holds after every predecessor
primitive. The existing signed-addition alphabet implements either resulting
coefficient without extra source preparation or a helper register. If subtract
were unavailable or had a different cost, the stated cost identity would not
follow.

At each boundary emit one physical negation for every register whose sign is
negative, then set that sign to `+1`. Since `x_r=-y_r` before that negation,
`x_r=y_r` afterward. Other registers are unchanged. Every register therefore
has exactly the predecessor value before the next event or frame is entered.
The whole-program exact map follows by induction over runs and unchanged
non-scalar events, even if those events are treated as opaque operations.
Boundary negations remain in the outgoing frame, so this argument does not
move an instruction across a frame change or recursive interface.

## Prefix norm and dirty inputs

Regard each register as a rational linear row over all original input columns,
including arbitrary dirty helper and coefficient-work columns. At every matched
prefix, the emitted row is the predecessor row multiplied by a sign. Hence its
absolute entries, `l1` norm, reduced denominators, and absolute value on any fixed
input are unchanged.
An omitted logical negation changes no physical magnitude. At a boundary flush,
negating any subset of registers likewise changes no register magnitude. Each
emitted prefix is therefore covered by a predecessor prefix's per-register
absolute-value envelope; the predecessor's maximum row-norm bound still applies.
This is a sign-equivalence argument, not literal membership of an emitted row in
the predecessor's row set. A test demanding literal prefix-row containment would
be stronger than the property established here and can reject valid sign changes.

Because the complete boundary values agree, helper restoration, coefficient-work
clearing, output shears and source values agree at every preserved interface.
No additional stream, source access, copy, recursive child or frame adapter is
introduced. Flushed negations are real charged operations, not free changes of
representation. The inherited charged payload and rounding/tape realization
remain assumptions; exact row identities alone do not prove an all-size rounded
implementation.

## Complete scalar cost

For run `j`, let `C_j` be its predecessor primitive count, `N_j` its number of
negations, and `F_j` the number of negative signs at its ending boundary.
Every non-negation remains one primitive, every predecessor negation is removed,
and every ending negative sign costs one emitted negation. Therefore

```
C'_j = C_j - N_j + F_j.
```

The complete real-component scalar count is the sum over all runs. Applying the
same real-coefficient word to real and imaginary components gives

```
C'_complex = C_complex - 2 * sum_j(N_j - F_j).
```

All recursive child multiplicities and non-scalar charges remain unchanged.
Equivalently, if an inherited local recurrence is
`R = sum_i m_i R_i + C_complex + A`, its replacement is
`R' = sum_i m_i R_i + C'_complex + A`, with exactly the same `m_i`, interfaces
and non-scalar charge `A`. This is an accounting identity, not a new asymptotic
recurrence solution.

Normalization is not universally cheaper. For example, `negate A; copy B,A;
copy C,A` has three predecessor primitives but needs two copies and three
boundary negations under this rule. A claim of savings must check the complete
pinned word, or explicitly choose the original word for unprofitable runs. No
universal savings or optimality follows merely from deleting negation opcodes.

For each of the two CK orientations in this package, the complete census is
348 predecessor negations and 236 boundary negations per real component. The
resulting saving is `2*(348-236)=224` real primitives per orientation. The receipt
and exact replay, rather than this hand calculation alone, establish that these
counts cover the pinned programs.

## Discriminating controls

Useful implementation controls must distinguish endpoint equality, prefix
coverage, boundaries and accounting:

- Negate a source and then add it to a target: omitting the
  `epsilon_t*epsilon_s` coefficient correction produces the wrong linear map.
- Negate a source and copy it to another register: failing to inherit the source
  sign produces the wrong copied value when signs are flushed.
- Finish a run with one pending negative register: omitting its boundary
  negation breaks the boundary map even if a later run would cancel it.
- Insert `double S; halve S` before an otherwise correct circuit: endpoint
  equality survives, but a prefix bound chosen tight at `S` rejects the growth.
- Add an unnecessary pair of negations: endpoints and norms survive, but an
  exact primitive count or word hash rejects the extra cost.
- Use the copy-fanout word above as a positive accounting control: the verified
  formula must report growth rather than silently count only removed negations.

Keeping a negative sign after clear is not by itself a semantic counterexample:
zero has either sign. It is a normalization/cost deviation, and should not be
presented as a failed algebraic identity without an additional incorrect step.

The induction above proves the local algebraic rule for arbitrary finite words
in the stated alphabet and boundary discipline. A finite replay of the two CK
words independently checks the concrete implementation and its coverage; it is
not a formal proof of the full conditional integer-multiplication theorem.
