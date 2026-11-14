# Complete fixed-contact frame obstruction for the P104 native word

This package proves that **every admissible simultaneous frame change in the
declared fixed-contact class has nonpositive paid-rank saving** on the pinned
native source from #7481. The unchanged assignment attains zero. The result
covers every increasing concave price on ranks 0 through 9, including
`r^(1-kappa)` for `0 < kappa < 1`.

The source's scalar coefficients, operands, chronology, contact equalities,
public entrance/exit frames, INIT/CLEAR frames, owners and lifetimes are fixed.
Every internal contact component may receive its own canonical binary-subspace
frame. Public MOVEs retain ascending containment; owned MOVEs may nest in either
direction. Zero recursive rank is allowed optimistically, while its ordinary
frame map remains an implementation obligation. All five foundational
assumptions remain. **No new kappa, supplier admission or multiplication lower
bound is claimed.**

## Exact result and evidence

The two separate parsers rebuild 76,475 instructions, 1,517 contact components
and 6,279 paid MOVEs. Public paths to frozen boundaries leave 96 variable
components in 77 interaction factors. There are 253 factor assignments and 214
legal assignments. Thirteen edges join growth and shrink variables, so the two
directions are optimized jointly. Both implementations agree on every legal
rank-profile multiset. Every factor has maximum saving zero at each of the
nine integer tariffs `min(r,k)`. These tariffs generate the entire increasing
concave cone by nonnegative linear combination; this is a proof for the stated
class, not extrapolation from a sample of prices.

The wrapper independently reconstructs the actual caller's complete histogram:
17 native invocations, 22,461 productive fields and 110,519 paid jobs. Productive
targets are fixed, so a nonpositive native paid saving cannot improve this
complete invoice. The all-column and whole-job conventions remain inherited;
the finite template certificate does not establish a column-scaling theorem.

## Reproduction

From the repository root:

```sh
python3 -I -W error -B research/complex-contact-recharting-bound/verify.py
python3 -O -I -W error -B research/complex-contact-recharting-bound/verify.py
python3 scripts/research_package.py --package research/complex-contact-recharting-bound
```

Expected status: `PASS_COMPLETE_CONTACT_RECHARTING_INDEPENDENT_REPLAY`.
The scripts use only the Python standard library and bundled inputs, and do not
modify the package. `RESULT.json` contains all legal factor profiles. The
historical positive control runs the **same optimizer** on an older canonical
word and finds exact saving 1 at `min(r,2)`. That change is already present in
#7481 and is not credited as a new gain. Mutated source bytes and a false
ownership flag must be rejected in normal and optimized Python.

## Pins, novelty and scope

Canonical base: `e54523517d0f03e58352e647c403a5af3e525a57`.
Source #7481: `89eaa9d8cae37c1540de98f2d29a3abaabb96a2b`.
Native SHA256: `acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9`.
All source paths, Git blobs and byte hashes are recorded in `SOURCES.json`.
The exact caller export has SHA256
`255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc`.

Earlier #7454, #7458, #7459 and #7453 study restricted common-frame or local
helper domains. This result uses boundary corridors to exhaust all distinct
per-component frame choices, includes main and owned visits, permits both owned
orientations, and proves the full concave-price statement. It retains credit
for the source, caller and all previous improvements, including #7122 and #7277.

## Open next questions

Changed scalar contacts, external productive boundaries, histories, ownership
structure or frame grammar may bypass this obstruction. The next useful step
is an explicit arbitrary-input rewrite with a complete signed budget; another
search inside the exhausted fixed-contact corridors cannot help. Actual source
compression, visit fusion and noncanonical frames are outside this theorem.

## Credit and license

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance in
research, independent algorithmic review and packaging. Independent here means
separate implementations and reasoning, not independent human or formal proof
acceptance. Retain `NOTICE`, `LICENSE` and the original notices in `inputs/`.
The original authors' native, caller, compiler and predecessor work is not
claimed as new. Apache-2.0.
