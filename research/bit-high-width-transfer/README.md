# Five-call high-endpoint bound at every scalar width

**Written width reduction plus an inherited finite census; no new kappa.**
Every exact five-call binary scalar-idempotent word with torsion-free
abelian addresses, nonzero frames, a whole diagonal monomial endpoint and
at most two independent frame relations has **at most two high registers**,
at every finite scalar width. Here high means the endpoint address is neither
zero nor a signed individual frame. Repeated high addresses count separately.
Arbitrary nonidentity diagonal auxiliary outputs are allowed.

The new result combines PR #6055's finite census with the inherited
active/dirty image restriction of Nick Petalas's PR #2900. Retain every
nonidentity output and remove irrelevant scalar dimensions. Every k-call diagonal word has an equivalent word on at
most k registers with the same ordered frames and nonidentity endpoints.
The source's call-image span gives a direct proof; no new width method is claimed. PR #6760's paired-helper theorem
also gives the sharper width t+floor((k-t)/2), where t counts **all** nonidentity
outputs. Applying the unchanged W<=5 census of PR #6055 gives the result.
This is not a purely symbolic replacement for that census.

[PROOF.md](PROOF.md) includes both width arguments, complete endpoint and
class preservation, width-zero/one cases, and a rational rank-one sharpness
example. Five coordinate calls give diag([I_2],[I_2],[E12]), exactly two high
registers, with frame span three and relation rank two.

## What changed in the task

The original assignment asked for the four-register five-call case for three
invertible rational 2-by-2 targets. The targeted overlap check found that this
case was already closed, more generally with arbitrary diagonal dirty outputs,
by JoyboyBrian's merged PR #5481. Josie Elliston's merged PR #6055 independently
corroborated it at W<=5 and explicitly requested an arbitrary-width extension
of its stronger high-endpoint census.

The open-question prose in the frozen span-four note and PR #6760 was stale
with respect to #5481/#6055. Their mathematical results are unchanged. This
package retains those sources and does not claim the six-call rank-two target
floor as new. It instead removes #6055's width restriction. Its conceptual
request for a wholly symbolic explanation of the finite classification remains
open; the theorem here has a finite exhaustive dependency.

Live searches of PR titles/bodies for `five-call`, `restored helper`, `6055`
and `high registers` were checked on 2026-11-06. They found the above successors
and no further relevant successor within the returned bounded coverage.
That is not a complete historical or unpublished-work audit.

## Evidence and reproduction

The new stdlib checker uses a separate coefficient-matrix expansion of the
whole formal endpoint. It checks two different scalar reductions: the retained
paired-rank constructor and a new direct image-space restriction. All original
nonidentity addresses, scalar pairings, frame order and high multiplicities
are checked. Forty-two fixtures include scattered active coordinates, arbitrary
mixed dirty vectors, identity-only words, W'=1 padding, promotion of a
nonidentity dirty output, a necessary W'=5 example, and genuine rank-one
rational sharpness. Four rejection controls cover a nondiagonal dirty block,
zero frame, illegal scalar projector and failed restoration. Six calls really
produce three high registers, so the five-call scope is tested.

```sh
python3.12 -I -B research/bit-high-width-transfer/verify.py
python3.12 -I -O -B research/bit-high-width-transfer/verify.py
```

Expected: `PASS_DIAGONAL_WIDTH_TRANSFER`. These fast checks authenticate the
14 retained source files and inspect all eight finite-census rows. They do
**not** rerun the census. To replay its complete W<=5 classification and all
three unpruned checks:

```sh
python3.12 -I -B research/bit-high-width-transfer/verify.py --full-census
```

The complete finite replay is much slower; the predecessor reported about
17 minutes on its own environment. The complete unchanged `--long` replay passed all eleven rows with zero
unreplayed rows. Its log window was 1,971.616 seconds on CPython 3.12.14;
this is not a performance comparison. Exact command, output, timestamps and
source hashes are recorded in [REPLAY.json](REPLAY.json).
The finite base is exactly the original PR #6055 program, not a new search.

## Limits

No native physical operation count, recursive invoice, supplier admission,
selected-record update or new kappa is supplied. All five selected assumptions
remain. This does not cover nondiagonal auxiliary endpoints, correctness only
on zero-initialized inputs, torsion address groups, larger scalar fields, or
the five-call theorem beyond relation rank two. No human or proof-kernel
acceptance is claimed.

## Open next questions

1. Give a purely symbolic proof of the at-most-two-high finite classification.
   Width is now bounded by five; classify the remaining pattern/lattice types.
2. Apply width transfer to a named eight-call, span-five/six relation class,
   after checking successor overlap. It limits scalar width to eight but does
   not remove the much larger relation and word search.
3. Determine whether endpoint information yields a smaller cutoff than k
   for other formal diagonal-word properties without changing their frame
   list or nonidentity endpoint multiset.

## Sources and credit

Scientific base: canonical main 7c49fe32c55de02c2c873655c804b16e4c3fef0a.
Source pins and Git/SHA256 authentication are in [ORIGINS.json](ORIGINS.json).
The seven-file PR #6055 package and PR #2900's image-restriction proof are
retained byte-for-byte, as are the relevant
PR #6760 proof/constructor and PR #5481 prior-result notes.

Credit Nick Petalas and Tuafo for the inherited image restriction;
Josie Elliston and Claude for PR #6055's finite census and cube-lattice
reduction; @CubeJerry and OpenAI Codex for PR #6760's sharper helper bound;
JoyboyBrian and OpenAI Codex for PR #5481's prior floor; and Ali Romman,
eumemic, waynenilsen, David Govea, unpaidmoon, Hanson Sun, woklerx and huxint
for retained model, scalar-image, rank, relation and pattern methods. The
classical image-span restriction is not claimed as a new linear-algebra fact.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. New work is
Apache-2.0. Frozen sources retain their original notices.

## Registered replay and provenance

From the repository root, run `python3.12 -B scripts/research_package.py --package research/bit-high-width-transfer`. The registered fast checks authenticate frozen inputs and test the width transfer in normal and optimized modes; the completed long inherited census has its separate command above. `SOURCES.json` binds the originating catalogue and merged source provenance. Pending #6760 copies are authenticated by `ORIGINS.json` and the local checker, and are not generic Git-history dependencies. The primary width argument and finite base use merged sources. The packaging change from the worker receipt is the source-manifest filename and repository-root command spelling; frozen scientific bytes are unchanged. See `REVIEW.md` for source-aware lead review. No selected-frontier cold replay or complete-history preflight is claimed.
