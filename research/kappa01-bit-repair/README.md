# Bit repair requirements for kappa = 0.1

**Scoped necessary conditions and candidate budgets; no new supplier or
kappa improvement.** The selected result is unchanged.

A target repair within the compressed-window model needs label density
`k/h>0.306330187868...`. Every odd stage count fails at primitive saving
`1/9` when `h/k>=3.264451365238...`, even with helpers and centre charges
free and every remaining idle charge placed at full rank. Every odd stage
count at least five already fails when `h/k>=3`.

This is stronger for the stated family than observing that the selected
PR589 profile costs more than one: it permits arbitrary helper improvements,
copy deletion, and ideal idle placement, while retaining the specific
coverage and active-data-climb laws. Uniform rank scaling preserves the
obstruction. A different global block or coverage law may escape it.

The proof and exact hypotheses are in [PROOF.md](PROOF.md). In particular,
the source's general-rank law is an explicitly stated premise; this package
does not claim that every conceivable rank-k bit network obeys it.

For a three-stage replacement with `(h,k)=(3,1)`, the ideal data-only bill is
`0.985156473147...`, so it survives the density screen. But even granting
free helpers and maximum rank-h copies, its copy-rank charge must satisfy
`C/(v*k)<0.063046005269...`. The corresponding allowances for `(8,3)`,
`(5,2)`, and `(8,4)` are approximately `0.143313`, `0.183912`, and `0.308880`.
These are concrete design budgets, not existing bit decoders.

The positive-definite `(h,k)=(3,1)` label-decoder attempt can also be excluded:
a four-sign-class argument gives copy rank `C/v>=1/4`, already above its
`0.063046...` allowance. This extra argument is specific to positive-definite
rank-one labels and scalar outer-product decoding; it leaves indefinite
geometries and general subspace/circuit replacements open.

Two concrete geometry changes are checked in
[PLANE_REPAIR.md](PLANE_REPAIR.md): an indefinite rational five-cycle and all
80 nondegenerate binary rank-two planes in dimension five. A certificate of
30 independent sets excludes every subset or multiset of the latter geometry
in the scalar full-orthogonality/support-pairing model. Its optimistic
three-stage target bill exceeds `1.016448`; the pressure argument extends the
exclusion to every odd stage under the stated coverage and separate-charge
hypotheses. These are checked repair attempts, not a general circuit barrier.

## Reproduce

Python standard library, from the repository root:

```sh
python3 -I -B research/kappa01-bit-repair/verify.py --check-sources
python3 -I -O -B research/kappa01-bit-repair/verify.py
python3 -I -O -B research/kappa01-bit-repair/plane_search.py
```

The first command verifies exact pinned source bytes from the repository's
Git object database. The second is an independent execution under optimized
Python and proves that acceptance does not rely on `assert`. Both compare
the computed rational receipt to [RESULT.json](RESULT.json).

The verifier checks five integer witnesses in the all-stage proof, enclosures
for the exact algebraic density threshold, ten candidate geometries,
direct-sum invariance, literal tensor-power deterioration, and controls that
preserve passing examples outside the stated obstruction. It also confirms
that removing the active-child rank cap reverses the E8 relaxed verdict.
It is a finite check accompanying the analytic proof, not a formal proof
assistant or supplier replay.

## Open next questions

1. Construct an explicit rational bit port system with density above the
   threshold and a fully charged decoder below (3). For density one-third,
   the very small copy allowance is the immediate obstacle.
2. Exhibit a chronological block that genuinely combines multiple active
   climbs into higher-rank children, and prove its common-frame, dirty-input
   and endpoint identities. This changes the precise cap used here.
3. Derive a different coverage law or an outer transfer that eliminates the
   bit bottleneck. Neither is supplied by improved scalar addition counts.

Source pin: `997e6a9ca7b4f95d50e366f61412fd640d72a88a`.
Credit DreamingOfClouds and the format-limits predecessor chain for the
compressed-window accounting, DreamingOfClouds' PR589 on eumemic's PR555
for the selected bit supplier, and the retained independent projector-ledger
and revision-3 lever audits. The new contribution is the analytic
target-1/9 density obstruction and its repair allowances. Prepared with
substantial OpenAI Codex assistance. Apache-2.0.
