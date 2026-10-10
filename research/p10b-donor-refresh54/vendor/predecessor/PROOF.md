κ = 7.69684039383334e-4

# Source-bound finite verification

The bit helper is a paired-cube bit word at cube size p = 10: a reversible local word in which all inputs and
dirty registers are formal variables. It is built by the gen5 generator with p = 10 data. Every later stage is
#315's p = 10 port of #285's chain, which is the source527 package's (eumemic). This file states what each stage
checks, what changed relative to #285, and what changed relative to #315.

## What changed from #315

Only the bit word and its pins changed. Every verification file is byte-identical to #315's. That covers
`verify.py`, every `*_check.py`, `code/`, `scalar/`, `bitword/bit` and the vendored checker. The differences are:

- **Data files** in `bitword/producer/data/`. `pm_p10.json` was re-annealed with a debt penalty: 273 additions,
  carrier debt 95 → 92. `local_design_p10.json` was re-searched at p = 10: 24 local additions per cube instead of
  27. `cube_orient_p10.json` is new and gives a balanced cube orientation. `arcs_p10.json` is the new frozen
  carrier matching.
- **Two producers**, which `verify.py` never runs. The generator reads the optional cube orientation and stores
  the symmetric plane entries an oriented cube needs; without the file it uses sorted cubes as before.
  `make_physical.py` chooses the maximum reuse matching by tiered augmentation (see "Physical layer" below).
- **The five pinned word files** in `bitword/selected/bit`, `word-pins.json` and `MANIFEST.json`.

The strict pins changed accordingly. Among them, the entrance census has become {16: 1,200}, and the bank
patterns no longer contain a mixed pattern.

## What changed from p = 12

The five-stage layout is the same at every h. It has m = 5h; idle ranks (2h−2, h−1, 2h+2, 4) at 2v each; h copied
centres of rank h−2, each read by 3v/h targets; and five-stage deficit 4v − 5h(h−2). The complex side already
used this at h = 22 (ranks 42/21/46/4).

At p = 10 (h = 20, v = 960) the layout values are:

- m = 100;
- idle ranks 38, 19, 42 and 4;
- copied centres of rank 18, with 144 scatter reads each;
- deficit 2,040.

`word_pins.shape()` derives every one of these values from p. Where #285 asserted a p = 12 literal, the check
now asserts the formula. Where #285 asserted a word-dependent literal (a register count, a histogram, a digest,
κ), the check calls `word_pins.expect(name, value)`. That call asserts exact equality with the value pinned in
`word-pins.json`, which `MANIFEST.json` pins like every other input. Each check is therefore exactly as strong
as the literal it replaces.

`verify.py` asserts that the pins are strict. `discovery/repin.py` records the pins in a separate process. It
runs the same stage sequence (`verify.replay`), and every structural assertion, exact certificate and control
still has to pass. See `discovery/REPIN.md`.

## The bit word

`bitword/selected/bit` pins five files: the signed graph, the virtual profile, the physical word, the exact
frames and the partner-pair chronology.

**Virtual word.** `virtual_check.py` runs eumemic's PR168-v4 package checker, unmodified, with p = 10. It
checks:

- exact frames (A·Bᵀ = 0, complementary ranks) and the mod-2 decoder with stars and side parts;
- geometry: source lines, side-root common caps, operand nesting and centre star spans;
- role and target chains on node frames, and the partner chronology;
- G-nondegeneracy of every used frame, for G = I − J/9 (nondegenerate on Q²⁰ since 1 − 20/9 ≠ 0);
- a literal F₂ dirty-scratch replay and the independent ledger recount.

All five mutation controls are rejected. The profile is:

- R = 9,060, W = 10,980, m = 3h = 60;
- deficit 840 = 2v − 3h(h−2);
- 12,905 frames and 149,400 children.

**Physical layer.** The same stage runs Chafik Boukhalfa's PR200 classes as PR200's `bit/prove.py` runs them.
`bitword/bit/base_word.py` is unmodified. `bitword/bit/word.py` changes only its input file names: PR200
hard-coded its own p = 12 names, and two lines (plus a comment) now read the cube size from the single pinned
`graph_pP.json`. The frame-loading line also asserts that the graph's p and h agree. `base_word.py` still
contains PR200's unused constant `P = 12`.

The classes check:

- every changed operation frame (1,183) is nondegenerate and contains its node's value span;
- the execution order preserves each role chronology;
- gauges are untouched in phase one, every gauge read precedes its role's first use, and gauge targets equal
  response supports;
- the 960 handoffs are one-to-one between ungauged non-root donors and gauged recipients;
- each donor is dead before its recipient's read, and its last frame lies in the recipient's gauge frame;
- all gate ports are distinct.

The stage also recomputes the physical row:

- phase one is exactly the centre closure;
- every addition's actual operands are checked;
- every physical role chain and the actual target chronology are nested;
- the deficit telescopes, at 840.

It executes the physical word on all 10,020 formal columns over F₂ and on the defining integer decoder. Four
adverse controls are rejected: an omitted compensation, a missing partner delivery, a stale recipient read and a
zero operation frame. `prepare.py` also recomputes the literal adjoint and asserts that it equals PR200's.

The handoffs follow PR200's rule. A recipient is read immediately before its first operation. Recipients are
rank-17 (h − 3) gauges with no strictly larger gauge later on any of their targets, so every target chain stays
nested. The producer's matching is a maximum matching, chosen by tiered augmentation. Donors are admitted in tiers
of decreasing end-frame dimension. Kuhn augmenting paths from the current matching never unmatch a matched donor.
The last tier is the full candidate graph and runs until no augmenting path remains. It matches all 960
candidates. #315's Hopcroft–Karp matching on sorted cubes reached 892, of which it kept 890. The bank width is
already divisible, so no pair is dropped (see `BANK-PROOF.md`). This leaves 960 pairs and 1,200 independent
entrances, all of rank 16. The checks above admit the pinned pairs as they are. They do not depend on how the
producer chose them.

## Unchanged scalar program and empty selections

`scalar/word.py` is the source527 scalar program, byte-identical (sha256 e675d4eb…). It reads h and v from the
word. Its source527 selections are all empty here:

- source loans, early and gauge mixes, retimed prefixes;
- aggregation, rank and echelon groups;
- fresh and paired source reads, terminal sinks.

The program then executes exactly the PR200 physical word:

1. dirty compensation at D0;
2. V injection and the phase-one gates;
3. the 20 copied-centre scatters;
4. gauge reads at their read times, interleaved with the remaining gates;
5. side roots, then partner mixes and deliveries;
6. cleanup, the inverse gates, and V removal.

`scalar_check.py` runs it on all 10,020 formal F₂ columns (960 sources, 960 targets and 8,100 dirty registers)
and in both defining-integer directions with 24-bit packing. The same 11 corruptions of the actual context as in
#285 must each make the unchanged program fail.

## Physical events, parity fusion and global lowering

`code/physical527.py` observes the scalar program and emits the physical frame tags. The emitter is source527's.
Its register count is pinned, and its copied-centre rank, count and reads are h−2, h and 3v/h. The local scalar
projection must equal the independent observer, and every MOVE is checked as an exact frame inclusion.

`parity_transform.py` deletes the 578,560 even-coefficient payload ADDs, which are identities over F₂. It merges
no MOVE chains, so the paid local histogram is unchanged. The independent required-use census rebuilds every path
from the surviving operations and mathematical endpoints, checks both reflected inclusions, and matches the
instruction histogram. The 350,640 surviving payload additions (349,680 of coefficient 1 and 960 of
coefficient 3) and their literal inverse are replayed on every F₂ column. The cancellation-free signed prefix
bounds are 22,071 (forward) and 959,838 (inverse). Its unused-stream census now ranges over the actual 2v + R
streams; #285 had the literal 19,406 there. The proof/PARITY-CONTRACT.md argument applies unchanged.

`code/global_lowering.py` is PR234's lowering, with V, H, M, the idle ranks, the copied-centre constants and the
deficit derived from the cube size, and R and the entrance census pinned. It expands all five stages, the idle
and bridge phases, the 1,200 completions and the terminal exchange. It checks every operand namespace and the
paid five-stage histogram:

- 245,500 calls;
- rank mass 1,191,960;
- deficit 2,040 = 4v − 5h(h−2).

`code/geometry527.py` checks the exact rational h = 20/m = 100 routes, and the eight idle boundary pairs for two
actual ports (gaps 38, 38, 19, 19, 42, 42, 4, 4). For entrances it checks two distinct actual bases of the most
frequent entrance rank and one actual basis of every other rank present. In this word, rank 16 is the only
entrance rank, so it checks two distinct actual rank-16 bases. For each one it checks the completion projector
(trace 5·16 = 80) and the five disjoint windows. It also checks that the two entrance projectors differ, and it
records that they do not commute.

## Primes, banks, moments and finite bill

**Primes.** `prime_check.py` recomputes the cleared-Gram determinant 9·BGBᵀ of every consumed basis: 12,760
distinct bases, at most 97 bits. The stripped small primes are 2, 3 and 11. The factor 11 appears because
det G = (9 − h)/9 = −11/9 at h = 20. Every residual is below 2⁸⁰, so the retained prime range q > 2⁸⁰ is
unchanged.

**Banks.** The independent entrances have 120 distinct bases and residual families of width 4 (rank 16); the
6,900 ungauged roles have width 20. `BANK-PROOF.md` gives the exact 100-coordinate tiling:

- (4²⁵) × 2,880 banks;
- (20⁵) × 82,800 banks.

`bank_check.py` rebuilds the 120 charts (at most 150 factors) from the G⁻¹ residual rows (h − 9)a − Σa, and
enumerates all 2,430,000 role/replica/stage assignments. It checks the callable route map and both endpoint
directions, and removes exactly the 1,200 rank-5a exterior completions.

**Moments.** Literal stock is 658,800. The normalized profile has:

- m = 100, W = 131,760;
- rank mass 13,151,520, deficit 24,480;
- largest child 42.

Two independent rational moment engines, including the complete 10⁻¹⁶ bad-class fallback, give the bit's certified
root c = 385138454781521/(5·10¹⁷) ≈ 7.70276910 × 10⁻⁴. The adjacent 10⁻¹⁸ grid point is rejected.

**Complex program.** The complex stage first checks the pinned gcert/1 program itself (`code/complex_gx.py`).
It runs Jacob Sussman's reference checker `gx.check1` with `scalar=True`: labels, blocks, N, the exact scalar
identity E5 (every x role restored, every target receives exactly its source) and Q2. It also runs his `gxcore`
Python mirror of the two Lean checks, whose block histogram must equal the program's. Both are vendored
byte-identical from wht-power-saving-lean at f010392c and sha-checked. One flipped scalar sign must be rejected
by both on E5. This is a Python check; no Lean check of this program is pinned here. The inherited label, scalar,
splice and finite-guard checks of PR234/#296 then run unchanged.

**Lean (run locally; not pinned here).** With Jacob Sussman's wht-power-saving-lean at f010392c (Lean v4.34.1,
Mathlib d13f23b) and his unchanged generator `tools/gx/regen_check.py`, the exact gcert pinned here (sha256
bb0499ab342aee3594904fc1cd72b9ff496cdb315d0840f4cdd5ba64ef794d34) was compiled to Lean and kernel-checked:
`OAI.PowerSaving.WHT.wht_main_block_B2Gcc27x`, the Walsh–Hadamard corollary at exponent 1 − 7727140/10¹⁰.
`tools/Compare.lean` passed against a challenge file that differs from Sussman's ChallengeB2Gp193x only in the
exponent and names; the axioms are propext, Classical.choice and Quot.sound. The official comparator and a clean
build from nothing were not run. This covers only the complex program's Walsh–Hadamard saving, not the bit word,
the bootstrap, the κ assembly or the retained integer-multiplication interfaces. Because the bit binds, κ is
unchanged if b is replaced by the Lean exponent.

**Assembly.** The complex supplier of this variant is #315's centre-sharing complex program, unchanged (see
`inputs/complex/centre-mw/NOTICE`). Its coarse b is certified like the bit's: with the 10⁻¹⁶ bad-class fallback,
by both rational moment engines, with the adjacent 10⁻¹⁸ grid point rejected. This gives
b = 772714351296671/10¹⁸. The inherited PR234/PR193 convention priced the complex side without the fallback
(772714354722691/10¹⁸). That root is re-certified and recorded, but not used.

The bit root c is below the complex leaf cap (1 − β)·b with β = 10⁻⁹ (by 0.32%), so **the bit supplier binds**.
The assembly is fed s = min(c, ⌊(1 − β)·b − 10⁻¹⁸⌋₁₀⁻¹⁸) = c, and the path is #285's. Three completed
ordinary-leaf levels from c feed the unchanged balanced outer assembly. All 47 strict inequalities and the seven
margins are positive, and the adjacent final grid point of κ fails. This gives
κ = 384842019691667/(5·10¹⁷) ≈ 7.69684039383334 × 10⁻⁴. (When c exceeds the cap, `math_check.py` instead feeds
the largest 10⁻¹⁸ grid point at or below the cap to the bootstrap, re-checks the bit moment there, and checks that
the assembly at the cap itself fails. This package does not exercise that path.)

**Finite bill.** `finite_check.py` pays every PR234 primitive and router allowance on the literal 60 replicas and
stock, and adds all 170,009,279,400 bank selector calls. It uses:

- the actual 40-dimensional rational route (163 additions, 36 swaps, 23 scalings; denominators {1, 2, 3, 6});
- d = m² = 10,000, so B(q) < q^10,001;
- h = 20 copied-centre temporaries and 5h = 100 copy/erase episodes per replica.

The data route families stay 20v + 4v (five stages of 4v data families plus the final exchange). The
finite-bill moment and bootstrap use the fed saving, here s = c.

## Inherited texts

The files in `proof/`, `UPSTREAM-PR234-PROOF.md` and the notices are inherited verbatim. Their numbers describe
the source527 p = 12 instance (for example m = 120, the 48-dimensional route and the determinant exclusions
{2, 3, 5, 7}). For this package, the actual p = 10 values are those listed here, recomputed in `finite.json`,
`banks.json` and `primes.json` of every verification run.

The inherited complex texts (`UPSTREAM-PR234-PROOF.md`, `proof/INTEGRATED_PROOF.md` §6 and the pinned `P193*.lean`
sources) describe PR193's complex program and its scalar identities hAi, hBi, hx, hy and hid. They do not cover
the centre-sharing program used here. That program's scalar identity is checked in every run by `gx.check1`
and the `gxcore` mirror (above).

## Scope

The proof boundary is unchanged and conditional. The following are inherited interfaces:

- the all-size weighted compiler and common ancestor charts;
- restored rows and completed ordinary leaves;
- selectors, exact-tape routing and prime supply;
- precision/recovery and retained complex symbolic correctness;
- analytic transfer.

These checks establish the stated finite construction under those interfaces. They do not rebuild Lean or
execute a multiplier at all input sizes.
