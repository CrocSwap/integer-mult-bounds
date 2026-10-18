# Exact floors for prefix-monomial permutation boundaries

The existing deferred-swap boundaries in the historical PR626 CK/JP8 words are **optimal in the following finite class**: use only the moved data coordinates and one workspace; allow every PR696 primitive, but require every intermediate register row to be zero or a signed incoming coordinate; restore the prescribed data permutation and leave the workspace zero. A transposition needs **4 primitives**, and a disjoint transposition plus three-cycle needs **8**. Both statements hold whether the workspace starts dirty or zero.

These are new scoped lower-bound certificates for the old boundary construction. They are **not whole-run or unrestricted arithmetic-circuit minima**. The original construction and its saving remain credited to ToikY's `complex-swap-runs-seed37` package. Its proof gives the construction cost d+c+1 and explicitly disclaims a whole-circuit optimum; it does not supply the finite quotient lower bound here.

| Actual boundary type | Per orientation | Exact minimum per real component |
|---|---:|---:|
| One two-cycle | 28 | 4 |
| Disjoint two-cycle and three-cycle | 14 | 8 |
| Total | 42 | 224 |

There are four frozen programs: CK and JP8, each forward and inverse transpose. All **168** actual boundaries attain these minima. An independently checked complete run census covers 2,219 runs per CK orientation and 2,199 per JP8 orientation, or 8,836 runs overall.

## Finite class and quotient proof

For n moved data registers, initially let their rows be the independent coordinates e_1,...,e_n. The workspace row is e_(n+1) for dirty entry, or zero for clean entry. No other register may be read or written. The endpoint is the declared positive data permutation and zero workspace; the incoming workspace dirt is erased, not restored, matching the pinned original macro interface.

Every available primitive has unit cost per real component: COPY, CLEAR, NEGATE, ADD, SUBTRACT, DOUBLE and HALVE. Binary operands are distinct. At every prefix each register row must belong to

```text
{0, +e_1, -e_1, ..., +e_(n+1), -e_(n+1)}.
```

This restriction retains the old boundary materializer's norm-one coordinate containment. It excludes temporary sums of different inputs, nonunit multiples, extra scratch registers, changes to intervening run operations, and crossing a scalar-frame or non-scalar barrier.

Forget each sign and retain only its coordinate label, with label zero for the zero row. COPY and CLEAR have their usual label effects. NEGATE is a label no-op. DOUBLE/HALVE can be admissible only on zero and are no-ops. An ADD/SUBTRACT of two distinct nonzero labels leaves the declared class. Equal nonzero labels either cancel to zero or create a forbidden coefficient of magnitude two. If one operand is zero, the output label is unchanged or copied from the other operand. Thus **every admissible primitive projects to one COPY, CLEAR or no-op**. This proves that a shortest path in the unsigned COPY/CLEAR quotient is a lower bound for the entire signed primitive alphabet.

If a required data label disappears from all registers, no allowed quotient operation can recreate it. States lacking any of labels 1,...,n can therefore be removed without deleting a successful path. There are only 18 admissible states for n=2 and 3,240 for n=5, within raw universes 4^3 and 7^6. The searches have no state cap or depth cutoff.

[finite.py](finite.py) exhausts all reachable quotient states from the exact entry and reconstructs a shortest word. [backward.py](backward.py) independently enumerates the full Cartesian-product state domain, then builds predecessor layers from the target by considering possible overwritten labels. It imports neither the forward search nor the candidate compiler.

| Type / work entry | Forward reachable states | Forward primitive edges | Minimum |
|---|---:|---:|---:|
| Two-cycle / dirty | 13 | 39 | 4 |
| Two-cycle / clean | 12 | 36 | 4 |
| Two+three / dirty | 2,521 | 21,606 | 8 |
| Two+three / clean | 2,520 | 21,600 | 8 |

Primitive-edge counts include different COPY sources with the same label. The independent reverse search covers all 18 or 3,240 admissible states; some are not reachable from the particular forward entry. Both methods agree on each requested distance. Every returned shortest word uses COPY/CLEAR only, so it lifts literally to the original signed-row model. A separate dense integer-matrix interpreter checks all data and workspace input columns, every intermediate row, and the full endpoint. This supplies matching upper bounds and completes the exact-minimum argument.

The inherited boundary realization uses l+1 COPYs per cycle of length l and one final CLEAR shared across cycles. All source accesses, saves, assignments and workspace cleanup are paid. Its prices 4 and 8 equal the independent lower bounds, including under the stronger clean-entry assumption.

## The joint-normalization pilot

The original question was whether jointly deferring signs and three-ADD signed rotations could improve the same frozen scalar runs. [joint.py](joint.py) implements that bounded pilot, including operand remapping, both candidate two-cycle materializations and all boundary signs/cleanup. It gives **no further saving** beyond the existing swap pass with identical known-zero CLEAR elision:

| Complete real-component count, either orientation | CK | JP8 |
|---|---:|---:|
| PR696 plus clear elision | 157,184 | 187,950 |
| Sign normalization plus clear elision | 156,960 | 187,726 |
| Deferred swaps plus clear elision | 156,624 | 187,390 |
| Deferred swaps, then signs, plus clear elision | 156,624 | 187,390 |
| Joint pilot plus clear elision | 156,624 | 187,390 |

The 224-real-primitive sign saving and 560-real-primitive swap saving against that comparator cannot simply be added. There are 126 recognized signed rotations per program, but no selected cheaper signed two-cycle boundary. Negative signs can still occur on three-cycles or fixed coordinates; no blanket positivity claim is made.

Every affected pilot run is replayed by the predecessor's separate dense checker. One explicit in-memory adaptation permits a prefix row or its negative, as required by sign deferral, while retaining the exact endpoint and arbitrary-work checks. No predecessor file is edited. The finite boundary lower bound is independent of this pilot and concerns the **old fixed boundary maps**. It does not prove that another signed-run strategy or a different boundary map could not improve the whole run.

## Reproduce and controls

From the repository root, Python 3.10+ and standard library only:

```sh
python3 -I -B research/complex-monomial-runs-seed25/verify.py
python3 -I -O -B research/complex-monomial-runs-seed25/verify.py
```

Use python on Windows. Expected final line:

```text
PASS_COMPLEX_MONOMIAL_FLOORS minima=4,8 programs=4 boundaries=168 controls=11 no_new_kappa
```

The default command reconstructs and compares every decoded field of [CERTIFICATE.json](CERTIFICATE.json). Add --write-certificate to deliberately regenerate it. It checks eight mandatory source pins, both finite-search methods, every witness, the complete actual-boundary census, the pilot counts and all 168 affected run maps. Eleven controls reject missing saves/cleanup, arithmetic mixing, nonunit scaling, a one-shorter claimed distance, omitted restoration, reversed three-cycle direction, missing source pins, duplicate/nonfinite JSON and Boolean number substitutions. Two positive controls cover paid paired signs and harmless scaling of zero work.

## Scope and provenance

Frozen base: 2921874911956718fcaaaf9396fe8267b3cfa9f0. Assigned seed **25** chooses the complex track; it is not rerolled and does not randomize correctness. [CLAIM.md](CLAIM.md) records the candidates and the one evidence-driven pivot from a tied construction pilot to a finite boundary lower bound. Exact source bytes and the base are bound by [SOURCES.json](SOURCES.json).

The accepted source at this base remains PR942's T37 composition, conditional kappa 0.001661960547713947, retaining PR589's bit supplier. This work deliberately studies historical PR626 CK/JP8 scalar programs. It changes no selected source, supplier, paid profile or frontier. PR1064's factory fusion, PR1060's P111 physical COPY word, PR1032's coefficient-work cache and PR1033's factory windows are different objects/classes; none is imported or composed.

The result proves exact local scalar boundary minima in the declared class. It does not re-execute the complete native physical program, phase/adapter realization, owner/invoice construction, production precision or outer assembly. The complete historical scalar endpoint evidence is inherited from the pinned predecessor; the actual changed-run pilot checks here are explicit. Compiler, common-label/mutable-source, hosting, precision/tape and analytic obligations remain. No new kappa, practical runtime improvement or unrestricted impossibility is claimed.

Prepared for **@woklerx** with substantial **OpenAI Codex assistance**. The independent algorithms and agent review are not independent human review. Apache-2.0. See [NOTICE.md](NOTICE.md) and [VALIDATION.json](VALIDATION.json).
