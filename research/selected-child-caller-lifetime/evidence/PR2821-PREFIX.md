# Exact numerical lifetime of the selected caller's validation prefix

The unchanged PR2697 `Consumer.apply` prefix, ending immediately before
`packet_engine.run`, has an exact additional residue peak of **4096 Words**.
Its exact additional index peak is **18** at program depth zero, **22** at
positive depth without a halving unit step, and **23** when such a step occurs.
All counts are above **all numerical residents on entry to `Consumer.apply`**.

This closes the initialization/validation part of
[PR2815's handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-18960449).
The extra index at a halving step comes from retaining `f`, parent/child and
the old loop state during a second four-Word division. Charging only the first
division misses that Word. The peak does not grow with program depth.

This is a written source-level lifetime proof with finite literal executions
and a separate AI specialist's integer ownership model. It is not a complete
caller reserve, physical-storage theorem, supplier admission or new kappa.

## Contract and proof

The [complete proof](INDEPENDENT.md) derives the primitive, directory,
initialization and validation lifetimes directly from the immutable source.
The residue/index arenas must be distinct, their incoming Words complete and
heads restored. Include modulus, Ring one, Context cap, parent size/depth,
unrelated matrices and suspended caller state in the entry baseline.
Assume selected dimension 64, current width 64..127, a legal fixed odd prime-power
ring, canonical matching program/field words, positive finite directory and
spectator counts, sufficient numerical capacity/margins and successful sequential
execution. The finite specification/binding/plan provider and observer allocate
no numerical Words. This is a conditional source contract; fixture metadata does
not certify actual selected-catalogue membership.

Let `h` be program depth, and let `H` say that an admitted `UNIT_KIND` step
has `half=1`. The phase ledger above the same entry baseline is:

| Phase | Residue Words | Index Words |
| --- | ---: | ---: |
| Complete directory production | exactly 4096 peak | 0 |
| Columns/field count, Geometry and Layout setup | 0 | exactly 9 peak |
| Retained caller context at validation entry | 0 | exactly 8 |
| Callback validation above that retained context | at most 12 | exactly 10/14/15 |
| Immediately before packet engine entry | 0 | exactly 8 |

The Callback alone retains two residue Words and six indices after initialization.
Its residue allowance 12 is attained with modulus 5, root unit 2; the callback
index maxima are 10 at h=0, 14 at h>0 without halving, and 15 with halving.
`frame.close` frees them before packet engine entry. A neutral engine-return
seam in the finite fixtures also lets the actual caller `finally` demonstrate
disposal of its eight indices. This does not prove engine cleanup or execution.

There is also an exact **joint occupied-content** formula. Put `r=b_R+1`,
`i=b_I+1` for each complete Word's digit cells plus RIGHT, and let
`K(h,H)` be 18/22/23. With `L_R,L_I` all entry live Words, the maximum over
the prefix is

```
(L_R+1)r + (L_I+1)i + max(4096r, 2r + K(h,H)i).
```

The two baseline `+1`s are the arena templates. The component peaks are not
simultaneous: the actual candidates are directory `(4096,0)` and validation
`(2,K)`. Other phase pairs, including inverse `(12,13)`, lie below their
maximum; the proof checks this for every positive `r,i`. Partial allocation
and erasure cannot exceed the complete-Word envelope. Both candidate cuts
occur in every successful execution satisfying the contract.

Count/record/control tapes, directory and payload content, LEFT markers,
erased backing slots, Python heap and physical movement are excluded. Failure
paths are excluded from the prefix theorem: its `try/finally` starts after
layout construction. Specific Callback rollback tests below do not establish
arbitrary caller exception safety. Coefficient evaluation and non-ADD/child
packet execution remain outside the result.

## Pins, credit and overlap

The twenty files under [vendor](vendor/) are unchanged PR2801 exports of
Jose Manuel/jmbarrancoml's PR2697 runtime at
`a53fdf4bcbe33c6732f0bec1badc8c023380f9d1`. Original paths, exact Git blobs
and SHA256 values are retained in
[PR2801's source manifest](evidence/PR2801-SNAPSHOT.json), itself hash-pinned
by the verifier. The loader compiles the bytes it authenticated and never
consults Python bytecode caches. Full original attribution is in
[NOTICE.md](vendor/NOTICE.md).

Credit Nick Petalas for PR2759's arithmetic proof, PR2770/2778/2781's numerical
components, PR2801 (`e2564b80b86fb77610b4b78701e5446a76fbe962`) and PR2815
(`ea10ca564948033cc79105ba2a7c280ede5177c3`); Ross Richardson's PR2810;
Arham Tahir's distinct PR2796 child coefficient lifecycle; and David Arias's
PR2753 coarser all-size logical reserve. Those coefficient/recursive proofs
are not prerequisites of this prefix lemma. The directory and Layout pieces
are independently rederived for composition, not claimed as new discoveries.
[PR2759's proof](evidence/PR2759-ARITHMETIC.md) is preserved with its original
attribution; new material is Apache-2.0.

The new contribution joins actual initialization and validation lifetimes at
one entry baseline, gives the exact 18/22/23 index classification, and proves
the joint occupied-content formula. It takes the released next task in the
[canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-18960943),
complementing the active physical Frame/controller audit. [TASK.json](TASK.json)
records the explicit override of the historical helper-contract picker card.
Entry overlap completely paginated 722 open PRs including drafts and 1463
Discussion/comment/reply records, plus 2026 local records, at 23:25–23:29 UTC
on 2026-10-15. The submission refresh completely paginated 704 open PRs at
23:38:54 UTC and 1466 Discussion records at 23:42:17 UTC, plus 2066 local
records, with no warnings. Relevant predecessor heads were unchanged. Metadata excludes arbitrary diffs, unpublished work and closed
PRs absent the ledger/notes; it is not a novelty certificate.

Prepared by Ross Richardson with substantial OpenAI Codex assistance and a
separate `math-storage-lifetimes` AI specialist. No independent human review
or formal proof-kernel result is claimed.

## Reproduce and exact finite coverage

From a Git checkout, with Python 3.12 and no third-party packages:

```sh
python3.12 -I -B scripts/research_package.py --package research/selected-validation-numerical-lifetime
```

For a Git-free export, run `verify.py`, `test_verify.py`, `independent.py`
and `compare_models.py` directly with `python3 -I -B`; optimized execution
is also supported. Normal replay is read-only. `verify.py --write` explicitly
regenerates only [RESULT.json](RESULT.json).

The literal replay covers 82 fixtures: 70 complete Callback lifecycles and 12
complete initialization/validation prefixes. Callback fixtures cover all good
ranks 1..42; zero, good, pair, unit and halving programs; depths 0, 1, 4, 8;
prime powers 3, 5, 27, 49; and unrelated borrowed residents. Prefix fixtures use
modulus 3 or 5 so every full 4096-word directory is executable, current widths 64
and 127, good/fallback metadata, and depths 0, 1, 4. The packet engine is replaced
only at the named endpoint by a neutral return seam; no Boolean payload or
selected GL64 execution is claimed. Serialized program/field bytes and heads,
entry numerical ownership/content/heads, decoded extents and high caps,
allocation peaks and sampled literal occupied cells are checked.

The independent model executes 4229 index histories and 1829 prime-power/unit
cases with native integers and an explicit allocation ledger, importing no
vendor implementation. `compare_models.py` requires every literal fixture's
exact validation peaks to agree with that model. The whole-prefix literal
fixtures exercise the directory-dominated branch of the joint formula; the
other branch and arbitrary valid depths/prime-power exponents are covered by
the written proof, not claimed as an exhaustive literal execution.

Controls reject a one-Word undercharge for each sharp Callback index class,
the residue inverse peak and the caller-relative half-step peak; malformed
codes, a nonunit root and inconsistent chronology; source/snapshot corruption;
and a boolean substituted into an integer receipt. A harmless restored extra
inverse temporary is rejected by the lifetime guard while the relaxed guard
admits its same endpoint, establishing defect sensitivity. A demonstrably
effective malicious `.pyc` is ignored by the authenticated-byte loader.
Specific invalid Callback fixtures check the constructor's own rollback before
teardown. [VALIDATION.md](VALIDATION.md) records executed environments and limits.

## Open next questions

Join each remaining non-ADD trace and successful child-return interval under
the same `Consumer.apply` entry baseline, using the exact program source and
callee restoration contracts. This is the next bounded step toward a complete
numerical caller allowance. Payload/count/control and physical backing/movement
still require separate simultaneous-lifetime ledgers; the current components
cannot simply be summed into a complete supplier reserve. See the structured
question and blockers in [TASK.json](TASK.json).
