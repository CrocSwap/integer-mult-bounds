# Bounded target accumulation for selected complex coefficients

**Finite local circuit improvement; no new kappa.** On the fixed selected
PR626 complex programs, this compiler saves another **1,114 real-component
primitives per CK orientation and 4,086 per JP8 orientation** beyond
[Sagar Thakrar's PR696](https://github.com/CrocSwap/integer-mult-bounds/pull/696).
It changes how a dyadic scalar addition is executed, while preserving its
complete arbitrary-input map, source, frame and cleared coefficient work.

| Program | Selected Horner cost | PR696 cost | This compiler | Additional saving |
|---|---:|---:|---:|---:|
| CK forward | 224,938 | 169,618 | 168,504 | 1,114 |
| CK backward | 224,986 | 169,634 | 168,520 | 1,114 |
| JP8 forward | 257,232 | 200,380 | 196,294 | 4,086 |
| JP8 backward | 257,280 | 200,396 | 196,310 | 4,086 |

These are exact instruction counts on the same four pinned inputs, not a
wall-clock speed benchmark. The compiler chooses between three constructions;
it does not claim globally shortest circuits. Recursive calls, scalar macro
words, adapters, residual wrappers, paid profiles, ownership and the selected
conditional exponent are unchanged. No global assembly is repriced here.

## Reproduce

From the repository root, with Python 3.11 or later and no dependencies:

```sh
python3 -B research/complex-coefficient-accumulation/lower.py
```

Expected output:

```text
PASS_COMPLEX_COEFFICIENT_ACCUMULATION programs=4 columns=716 extra_savings=1114,1114,4086,4086 controls=10
```

The command reads pinned committed inputs and checks `EXPECTED.json` without
writing files. It executes the emitted primitives over all 716 arbitrary
input columns of each program, including all 492 dirty helper columns, plus
an independent arbitrary input to coefficient work. It checks all 686 distinct
signed coefficients against an independent three-register rational interpreter.
It verifies the reference counts, semantic input hashes, unchanged paid
histograms, exact endpoints and private clearing. Ten controls reject missing
cleanup/copy, a wrong sign, source/target/work prefix growth, nondyadic or zero
coefficients, and aliases. Checks remain active with Python `-O`.

`--write-certificate NEW_PATH` writes a freshly recomputed certificate to a
new file, refusing to overwrite an existing file. `lower(op)` is the callable
compiler; its caller executes the returned real-component primitives at the
original macro's frame, separately on the real and imaginary components.

Validation passed on macOS arm64 with Python 3.14.8, including isolated
optimized execution (`-I -O -B`). The existing selected-record/source-inventory
check and staged whitespace check also passed. These are local results;
the broader checks excluded below are not claimed.

## The two new circuits

Write the coefficient as `q = sign * a / 2^d`, in reduced form, with `a > 0`.
The incoming target, source and coefficient work are `T`, `S` and arbitrary
`W`. Every circuit ends with `T + q*S`, unchanged `S`, and `W = 0`.

1. **Descending binary accumulation.** Copy `S` to `W`, scale it to
   `2^(floor(log2(a))-d)*S`, then descend by halves. At each set bit of `a`,
   accumulate that summand directly into `T`. For `5/8`, this costs seven
   real primitives rather than nine in copy-Horner: copy, halve, add, halve,
   halve, add, clear. Fractional coefficients avoid an integer multiplication
   followed by a separate run of halvings.
2. **Ascending signed accumulation.** Compute the non-adjacent signed binary
   digits of `a`. Copy and halve `S` to `S/2^d`; visit digits from low to high,
   doubling `W` between positions and accumulating each signed summand in `T`.
   For `63/8`, this realizes `-S/8 + 8*S` in 13 real primitives, compared with
   16 for copy-Horner. If the highest work value would exceed `a*S`, replace
   its leading term with two accumulations of its half. This happens only for
   integral coefficients. For example, `15*S = -S + 8*S + 8*S` never requires
   a work value `16*S`.

The third option is PR696's copy-Horner construction, including its direct
unit accumulation plus work clear. Ties retain this predecessor. The chosen
new circuits replace 465 CK and 643 JP8 additions per orientation. All source
copies, shifts, signed accumulations and final clears are charged. There is
still only one private coefficient register, with no new helper or recursive
child and no extra frame transition.

## Exact substitution and prefix bound

Let `T0` and `S0` be arbitrary incoming values. The old Horner construction
permits work magnitude up to `a*|S0|`, as well as its arbitrary initial work
before clearing, and target bound `|T0| + |q|*|S0|`.

The independent checker establishes after every primitive that the source
is exactly `S0`, the target is `T0 + c*S0` with `|c| <= |q|`, and work is either
the untouched incoming work or `w*S0` with `|w| <= a`. The final map and work
clear are checked separately. Consequently the old per-register triangle
bounds remain valid at each macro, even though intermediate rows need not
occur in the old Horner trace. This is deliberately stronger than checking
only the endpoint and different from PR696's row-subsequence argument.

The binary proof is immediate: its summands have the same sign, partial sums
are bounded by the full coefficient, and its largest work value is at most
`a`. For signed digits, let `2^K` be the leading positive term. The next digit
is zero; the sum `B` of the absolute lower terms is less than `2^K/3` by the
non-adjacency property. Thus `a >= 2^K-B > B`. Before the leading term, every
partial signed sum has magnitude at most `B < a`; the last sum is `a`.
If the leading term is split, its first half gives `a-2^(K-1)`, which lies
strictly between zero and `a`, and the second gives `a`. The explicit split
condition guarantees the work bound. Negating all accumulation signs treats
negative coefficients identically. Intermediate denominators do not exceed
the original dyadic denominator.

Every primitive remains inside its original scalar event's frame. The source
and target are distinct and neither aliases work. Coefficient work is cleared
before any following event, as in Horner. Therefore the substitution preserves
the fixed macro program, all helper restoration, and the existing frame and
wrapper boundaries. The inherited prefix bounds and 192-bit local payload
allowance remain upper bounds; this is not a new rounded-arithmetic theorem.

## Scope, provenance and research choice

Base commit: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
Reviewed PR622 source: `f69477f4f6d3c7eb1f740b166881bffed4ffa9f6`.
Selected PR626 source: `660de893d27bb7abd1d5b01b1640207528a5c851`.
The comparison is pinned to PR696 at
`5a3f983715027c4fd83f50bc9001d4b18463bed1`; its files need not be installed.
`SOURCES.json` pins every consumed input and the inherited count/prefix code.
Gzip pins use decompressed bytes; no container-header equality is assumed.

OS assignment seed **28** selected the complex-supplier track. `CLAIM.json`
records the three considered tasks, bounded scope and overlap check. There
was no pinned sprint issue, so the claim stayed local. Coverage is the complete
686-coefficient corpus from both selected providers in both orientations.
There is no stochastic circuit search or uncompleted parameter sweep.

The prior campaign-100 item 38 found no paid-climb improvement from its
coefficient-3 rewrite. This result makes a different, explicitly scalar-only
claim on the selected words. PR681 resynthesizes a raw factory macro window;
PR696 retains one target accumulation; PR698 optimizes fixed CK B frames.
This contribution instead accumulates multiple coefficient summands into the
target while preserving the original macro boundary and magnitude envelope.

All inherited all-size compiler, common-label/mutable-basis realization,
whole-call hosting, normalized residual, precision/tape/exact-recovery,
analytic-transfer and bit-supplier assumptions remain. Finite rational replay
is not a Lean proof of the full multiplication theorem. The selected emitter
has not been switched to this compiler; cold provider regeneration, global
assembly, Linux CI and the repository-wide suite are outside this local result.
`upstream/` and all selected artifacts remain untouched.

Prepared for **Seb (@ZK-Snarky)** with substantial **OpenAI Codex assistance**
in research, code, proof analysis, verification and writing. Apache-2.0.
Credit to **Sagar Thakrar (@thakrarsagar), PR696**, for copy-Horner/unit
lowering and the sparse primitive replay used as a starting point;
**icekylinx**, PR425/433/531, for the scalar compiler and primitive vocabulary;
**Jeremy Kothe (@jeremykothe2)** for PR622's construction;
**Chafik Boukhalfa (@chafreaky)** for PR626 packaging/ownership;
**DreamingOfClouds** for the cold-helper and native verification lineage;
and **eumemic** for the retained PR543 bit supplier. Earlier source notices and
the complete lineage remain in the unchanged selected packages and maintainer
review. No independent human or delegated-agent review is claimed.
