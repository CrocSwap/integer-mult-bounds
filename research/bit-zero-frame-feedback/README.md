# Zero-frame target feedback: exact three-helper/three-target census

**Finite exact negative result and a scoped prefix-substitution lemma; no new
supplier or kappa.** For every binary 3-by-3 matrix K, allowing targets to feed
helpers does **not** shorten the minimum fully restored circuit

    (h, y) -> (h, y + K h).

Here all six registers are arbitrary dirty inputs, every gate is a unit-cost
single-source XOR, and there are no additional registers. The result covers
all word lengths: attained minima are at most seven, and the exhaustive search
rules out every shorter word. The same equality holds for all nine shapes with
1 <= helpers, targets <= 3: 682 labeled maps in total.

This is a refined `bit-helper-contract` investigation. Pending PR1194 already
addresses its original H2/K question for a fixed word but retains H1 even inside
D. We isolate that retained restriction inside the zero-frame prefix, prove
the boundary condition needed to remove it there, and test its local price.
[TASK.json](TASK.json) records the original card and the refinement.

## Alphabets, complete boundary, and cost

Order registers as h0,...,h(H-1),y0,...,y(T-1). A gate `[d,s]` means
`register[d] ^= register[s]`, with distinct indices. Compare:

* **Restricted:** every ordered pair except helper destination / target source.
  Helper-to-helper and target-to-target gates are allowed.
* **Unrestricted:** every ordered pair of distinct registers, including target
  feedback into helpers.

Every gate costs one, including preparation and restoration. All registers stay
at the same zero frame. The model contains no source reads, COPY/ERASE, recursive
calls, frame changes, allocation, clean ancillas, or unpriced basis changes.
Its required matrix, in column-vector convention, is

    T_K = [ I_H   0  ]
          [  K   I_T ].

Both helper identity and target identity blocks are checked. A circuit that
works only when targets or helpers start at zero does not meet this contract.
Separate helper/target permutations below only transport proofs and witnesses;
they are not free operations inserted in the executed circuit.

The complete local bill of a length-L prefix is L scalar ADDs and zero of the
other event types above. A substitution in an already legal continuation leaves
its literal events unchanged, conditional on the same common-frame realization.
This is not a physical precision or hosted-supplier invoice. In particular,
equal binary endpoints do not imply equal intermediate integer envelopes.

## Scoped prefix-substitution lemma

Let M be any F2 module, for example bit streams with pointwise XOR. Let D0 and D
be finite prefixes on M^(H+T), both operating wholly at a common zero frame,
touching only these helpers and targets, and with no other state changes or
interior observers. Suppose their complete coefficient matrices are both T_K.
Then any fixed deterministic continuation receives identical register values
and frames after either prefix, and has the same final semantic result.

**Proof.** Each XOR is an elementary matrix over F2. The product's coefficients
act on M by the same additions, so equality of the complete binary matrices
implies equality for every input in M^(H+T). Untouched sources and other state
are also equal. Composition with the identical continuation preserves equality.
No reordering or frame-free interpretation of the continuation is required.

Choose D0 to be the direct target-only shear, with one gate for each nonzero
entry of K. If a virtual word with D0 satisfies the inherited interface and
chronological assumptions, the lemma allows replacing just that prefix by D.
H1 is then needed for the unchanged continuation, not for D's intermediate
states. This is the same boundary-substitution mechanism used in PR1194; the
explicit difference here is dropping its D-local target-feedback prohibition.
The actual word D, not the virtual direct shear, must be priced and subjected
to any physical precision checks.

The enlargement is nonempty. With one helper h and target y,

    h ^= y; y ^= h; h ^= y; y ^= h; h ^= y

has exactly the boundary `(h,y) -> (h,y+h)`, yet uses target feedback. It costs
five gates; the restricted implementation costs one. The positive control
checks this example on the complete boundary. The census below establishes
that no more economical feedback example exists in the stated finite domain.

This lemma does not remove H1/H3 from A/scatter/B or alter the projected cleanup
rule. In particular it does not contradict PR1105's raw-feedback cleanup
counterexample: that example lacks the complete restored prefix boundary used
here. Physical all-size realization, tape/rounding and precision bounds remain
separate obligations.

## Exact certificate and lower-bound argument

For either alphabet, let B_r be all complete matrices reachable in at most r
gates, with exact breadth-first distances, and S_r its distance-r sphere.
Every generator is its own inverse. For any A in S_i, i <= 3, look up
`B = A T_K` in B_4. A hit gives `T_K = A^-1 B`, realized by the word for B
followed by the reversed word for A. Conversely, every word of length at most
seven splits into such pieces, because its factors have lengths at most four
and three. Thus the minimum hit is the exact minimum whenever a hit exists.
All 682 targets have hits; no unsearched length can be shorter.

`verify.py` uses packed binary matrix rows. It builds both radius-four balls,
checks every orbit under the independent helper and target permutation groups,
and records shortest restricted witnesses. These permutations conjugate both
gate alphabets and preserve unit cost, so their orbit distances are equal.
For 3-by-3 K there are 36 orbits covering all 512 labeled matrices.

`independent.py` imports no primary checker code. It represents a complete map
by its truth table on all 2^(H+T) dirty bit inputs, composes byte tables, and
checks all 682 labeled K without using orbit reduction for lower bounds. It
transports and replays the restricted witnesses on each labeled endpoint.
Unrestricted lower bounds and restricted upper bounds meet for every K.
Both implementations use the same proved meet-in-the-middle principle, so
this is independent representation and code, not an independent mathematical
lower-bound method. Full-group ordinary BFS for H,T <= 2 supplies a further
control; the largest case reaches all 20,160 elements of GL(4,2) and all 576
restricted elements.

For H=T=3 the exact sphere sizes at radii 0 through 4 are:

| Alphabet | 0 | 1 | 2 | 3 | 4 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Restricted | 1 | 21 | 264 | 2,436 | 17,142 |
| Unrestricted | 1 | 30 | 570 | 8,415 | 101,610 |

Both alphabets give the same labeled minimum-cost distribution:

| Minimum XORs | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Number of K | 1 | 9 | 36 | 84 | 126 | 132 | 96 | 28 |

[CERTIFICATE.json](CERTIFICATE.json) includes all dimensions, sphere counts,
orbit representatives, multiplicities, minimum costs and attaining witnesses.
The primary replay recomputes and compares every field. The all-ones 3-by-3 K,
for example, has cost seven in both alphabets, versus nine direct helper reads.
The gain over that direct implementation already exists in the restricted
alphabet; target feedback adds no saving.

## Reproduce

Python 3.12, standard library only; from the repository root:

```sh
timeout 60s python3 -I -B scripts/research_package.py --package research/bit-zero-frame-feedback --check-only
timeout 300s python3 -I -B scripts/research_package.py --package research/bit-zero-frame-feedback
```

The registered replay runs these two read-only checks in sequence:

```sh
timeout 120s python3 -I -B research/bit-zero-frame-feedback/verify.py
timeout 120s python3 -I -B research/bit-zero-frame-feedback/independent.py
```

Expected lines:

```text
PASS_ZERO_FRAME_FEEDBACK maps=682 six_wire_maps=512 orbits=36 max_minimum=7 feedback_gains=0 controls=8 no_new_kappa
PASS_INDEPENDENT_ZERO_FRAME_FEEDBACK labeled_maps=682 dirty_inputs_per_six_wire_map=64 full_GL4=20160
PASS_REGISTERED_RESEARCH_PACKAGE research/bit-zero-frame-feedback outcome=negative-result
```

Replay takes a few seconds on the donation host. `verify.py --write` explicitly
regenerates the certificate. Both scripts retain their checks under `-O`.

Two positive controls check a restored helper star and the five-gate feedback
word. Eight negative controls reject feedback under the restricted alphabet,
omitted helper restoration, a missing helper-input contribution, residual
target-basis mixing, the wrong target map, self-XOR, Boolean register indices,
and an insufficient search radius. Residual target mixing is invisible on
zero-target inputs; that control specifically enforces arbitrary target dirt.

[SOURCES.json](SOURCES.json) pins the base, original task and selected record,
plus the inherited checker/PR1062 documentation used to identify the contract.
The inherited checker is hash-checked as context and is not executed by this
package. Pending PR1194/1105 heads are contextual attribution, not imported
code or assumed accepted results. No predecessor or selected artifact changes.

## Limits and unchecked obligations

The equality of optimum costs is only for 1 <= H,T <= 3, F2, the stated two
single-source unit-cost alphabets, and no extra registers. It is not a theorem
for larger dimensions, multi-source gates with another billing rule, unequal
weights, nonzero frames, or other fields. No fixed R439/R420 circuit was edited,
and no new full physical supplier or recursive moment was constructed. The
all-size compiler, native replay, hosting, precision/tape bounds, source/frame
realization and outer analytic transfer were not checked here. The selected
frontier's cold replay was not rerun for this isolated finite result.

## Open next questions

1. **Does equality persist beyond three helpers and three targets?** A strict
   advantage would make the D-local feedback relaxation economically relevant.
   A feasible first step is one pinned 3-by-4 K, with a restricted upper bound
   and an unrestricted shorter candidate followed by exact shorter-word
   exclusion. Larger ball sizes and the lack of a candidate are the blockers;
   this result supplies no general no-feedback theorem.
2. **Can a useful legal supplier instance realize such a prefix with its full
   physical costs?** If a larger strict gain is found, compare its complete
   prefix matrix against the original D and then recount actual intermediate
   precision envelopes, paths and hosting. No shorter candidate or physical
   bridge has been supplied here, so supplier adoption remains blocked.

Structured versions are in [TASK.json](TASK.json). There is no reason to extend
the same 3-by-3 search: its exact no-gain result is complete.

## Credit

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
New work is Apache-2.0. This contribution claims the specified finite census
and explicit D-local scope clarification, not novelty for elementary matrix
substitution, CNOT synthesis or meet-in-the-middle search.

Credit @woklerx for [PR1194](https://github.com/CrocSwap/integer-mult-bounds/pull/1194)
(`2e39c98238f543d988f9efc1b076590a4b780dca`) and
[PR1105](https://github.com/CrocSwap/integer-mult-bounds/pull/1105)
(`20a960b545f4b0ade4f26922ef686bd5eaf275f4`), Zhihao Chen's PR425 scalar-interface
lineage, eumemic's interleaved checker and PR555, DreamingOfClouds's PR589,
Gareth Davidson's PR926 pairs, @theon199's PR967 stars, and Sagar Thakrar's
PR1062 with Aaron Wang's PR1015 and Ross Richardson's PR923 block work. PR1188's
exact GL5 window synthesis is related algorithmic work on different endpoints;
PR1122/1208 optimize fixed R439 words. This account's PR794 target-basis result is
separate and was not redone. Existing source licenses and notices are retained.
