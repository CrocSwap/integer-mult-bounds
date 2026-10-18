# Shorter rank-seven programs with a lower native bound

Twenty-four exact commuting contractions remove 27 A gates and 27 inverse
cleanup gates from each pinned six-skip provider. The complete native primitive
bound falls by **340 per word and orientation** relative to PR3060. All recursive
children and helper widths remain charged; **κ is unchanged**.

The new source is an explicit edit certificate and producer, not a new search
engine. [PROOF.md](PROOF.md) proves each contraction on arbitrary dirty inputs.
[EDITS.json](EDITS.json) records sequential addresses, both old gates, the exact
combined coefficient and each strict tariff decrease. Three zero-sum pairs
disappear; the other 21 pairs combine. The first 84 A events remain fixed.

```text
                         PR3042       PR3060       this composition
A gates                    4079         4079         4052
inverse cleanup gates      5216         5216         5189
forward primitive bound  158148       158124       157784
backward bound           158196       158172       157832
```

The earlier 24-unit restore saving belongs to PR3060. These A contractions add
340 units of improvement and compose with it exactly. The metric is the inherited
emitter's conservative real-component primitive bound. It is neither a measured
runtime nor a fully materialized instruction count.

## Evidence and complete bill

Fresh native transport and emitter runs cover PR3042, PR3060 and the composition
for both providers. Each verifies all 632 live input columns in both orientations.
A separate recount prices every emitted scalar and checks the full non-scalar
stream against each predecessor. All 240 native warp events, 408 ordered helper
widths, 91 private buffers and erasure checks remain. The emitted scalar-macro
count falls from 17,449 to 17,395. [RESULT.json](RESULT.json) contains deterministic
word/program hashes and full native check records.

The frame tracker checks all 704 original registers. The unchanged local profile
is `{1:2433, 2:712, 3:232, 4:108, 5:18, 8:8}`. Therefore any otherwise valid
unchanged allocation has the same recursive invoice and physical-family charge.
That implication is conditional on its inherited interface; no ownership or
complete supplier/outer release is claimed here.

Behavioral controls check exact dirty matrices, cancellation, positive source
fan-out, forbidden target reads/source writes, frame and warp barriers, coefficient
and preimage corruption, stale cleanup, source hashes, and wrong native cost,
profile, erasure and non-scalar streams. A passing forward word followed by its
matched inverse cannot replace the separate edit proof.

## Reproduce

Python 3.12 and its standard library suffice. No network, solver, Lean, Docker or
unrelated historical suite is needed. Use an existing session-owned external
directory as `RUN`; `native` must not already exist.

```sh
mkdir -p "$RUN/tmp"
TMPDIR="$RUN/tmp" python3.12 -W error -B \
  research/rank7-commuting-contractions/verify.py --work "$RUN/native" \
  > "$RUN/result.json"
cmp "$RUN/result.json" research/rank7-commuting-contractions/RESULT.json
TMPDIR="$RUN/tmp" python3.12 -W error -B \
  research/rank7-commuting-contractions/test_contractions.py
```

Without `--work`, diagnostics are disposable under `TMPDIR`. With it, native
programs and logs are retained on success or failure. Each child invocation has
a 90-second limit. `--emit-word base` or `--emit-word extra` prints the actual
composed word only after the complete replay and receipt comparison pass.
Optimized parent execution keeps the checks enabled; compiler children run with
assertions enabled and a fresh bytecode namespace.

```sh
TMPDIR="$RUN/tmp" python3.12 -B scripts/research_package.py \
  --package research/rank7-commuting-contractions
```

`VENDOR.json` pins all 12 frozen inputs to PR3060 commit
`df16ae619b858c5344a797c4424e0bafc2e69f62`, original source paths, Git blobs and
SHA256. The original words are the exact PR3042 exports, not modified source
archives. `SOURCES.json` pins the canonical-main provenance.

## Scope and research decision

Canonical baseline is `d8e0f83f00191df62174b641e9fff055c357f641`, priority revision 6.
This takes PR3065's changed-scalar handoff. PR3065 already closes joint frame-only
reassignment. Bounded shared-update/conjugation probes found no verified lower
recursive bill. The retained compiler-bound improvement is an explicitly labelled
side result from a changed `independent-moment` scope. Those discovery probes
are not a completed census or a new obstruction theorem.

PR3056/3060 already cover the register22/230 restore block. This contribution
changes A instead and credits their disjoint improvement. No optimality, new
supplier, κ improvement or selected-frontier change is claimed. Physical
coefficient-stream lowering, its internal precision/storage and movement costs,
all-size/compiler and inherited analytic/caller hypotheses remain separate.
Evidence is author-checked, with internal independent checks; it is not independent
human or formal-kernel review. Hosted CI is separate.

## Open next questions

Can an actual coefficient-stream lowering retain the lower bound as a physical
instruction saving, with its intermediate magnitudes and cleanup fully charged?
Start from the three pinned emitted streams, especially the new `-3/2`, `-3/4`
and `-3/8` coefficients. This matters because fewer compiler-bound units do not
automatically establish a precision-safe materialized implementation. The missing
instruction recipes and internal-state ledger are the blockers.

A recursive improvement still needs a changed centre/scalar/interface mechanism
that removes paid work. This package offers no new evidence for expanding the
fixed-frame or fixed-inventory searches.

## Credit

Nick Petalas contributed the explicit contractions and source-bound replay.
Credit PR3060 for the inherited optimal restore substitution, tariff and native
replay pattern; PR3056 for cleanup/frame helpers; dcharb78 for PR3042's six skips;
Jeremy Kothe for PR3015 and the rewrite tooling; Marius-Paul Dumitrean for PR2979;
Sagar Thakrar for PR3053; Gareth Davidson for the earlier scoped frame results;
Cinna Davis, icekylinx, Tekalign and the retained native/geometry/owner lineage.
The frozen [credits](vendor/CREDITS.md), [notice](vendor/NOTICE) and PR2226 notices
remain intact. Apache-2.0. Development used substantial automated assistance.
