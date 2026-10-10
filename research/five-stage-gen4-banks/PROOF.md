# Concave-descent frame retiming and target-prefix compression on the gen4 five-stage completed banks

**κ = 724098741932703/10^18 = 7.24098741932703e-4**, conditional, with the bit supplier binding: +1.23 × 10⁻⁶ (+0.170 %) over the gen4 package below (7.22869827347495e-4).

This package is DreamingOfClouds' `five-stage-gen4-banks` with two added stages after `parity_transform.py`, neither of which changes the gen4 word's banks, entrances or charts:

1. **`descent_transform.py`** (frozen `descent-selection.json`): local descent on the concave paid-rank objective Σ r·ln(120/r) reassigns 880 ADD frames, running each unborrowed source-pair mix at its rank-22 common delivery frame exactly as PR244 did for source527 (per pair the paid children of ranks 1, 1, 20, 22 become 21, 21, 2; local paid histogram delta {1: −1760, 2: +880, 20: −880, 21: +1760, 22: −880}; 880 local recursive calls disappear at unchanged rank mass 425,742). The transform rebuilds every MOVE from the retimed gate needs and independently checks the byte-identical scalar/COPY projection, nested chains, fixed endpoints, unchanged COPY lifetimes, nondegenerate endpoint bases, both reflected annihilator ledgers and the exact integer source span of every non-target operand inside its new frame.
2. **`target_transform.py`** (eumemic's PR268 exact F₂ target-prefix compression, unchanged apart from the stream count; frozen `target-selection.json`): in each of 220 squares of four targets, every rank-20 entrance helper is read by exactly two of the four, so the dependent target's frame-20 prefix response is the F₂ sum of its three square-mates'. The dependent's 1,100 frame-20 reads are omitted; it receives `t −= p_j` at the zero frame at the cut (record 566,579) and `t += p_j` at the square's common nondegenerate 21-dimensional frame at the close, where all four members are moved (1,320 setup/restore additions). Its chain ZERO →(20)→(1)→ 21 becomes ZERO →(21)→ 21: histogram delta {1: −220, 20: −220, 21: +220}. The transform recomputes every literal prefix dependency from the actual word, rebuilds every MOVE, checks nested chains, endpoints, COPY lifetimes, nondegenerate bases, both all-column replays and an omitted-setup negative control, and rebinds the raw ledger.

Five-stage profile: 482,046 calls, rank mass 2,809,600, deficit 4,400 per replica; per-replica bank call count 479,580; the executed word has 626,580 weighted ADDs. `prime_check` retains the determinant obligation for producer frames the retiming removes (PR244's rule). `bank_check` and `verify.py` require the new counts and κ.

Prepared by Rohan Arun with Anthropic Claude assistance; Apache-2.0. Everything below is the gen4 package's own description.

---

κ = 7.22869827347495e-4

# Source-bound finite verification

The bit helper is the gen4 paired-cube bit word, a reversible local word in which all inputs and dirty
registers are formal variables. Every later stage is the source527 package's (eumemic). This file states
what each stage checks for gen4 and what changed relative to source527.

## The bit word

`gen4bit/selected/bit` pins five files: the signed graph, the virtual profile, the physical word, the exact
frames and the partner-pair chronology.

**Virtual word.** `virtual_check.py` runs eumemic's PR168-v4 package checker, unmodified and vendored in
`gen4bit/references/pr168-v4`. It checks:

- exact frames (A·Bᵀ = 0, complementary ranks) and the mod-2 decoder with stars and side parts;
- geometry: source lines, side-root common caps, operand nesting and centre star spans;
- role and target chains on node frames, and the partner chronology;
- G-nondegeneracy of every used frame;
- a literal F₂ dirty-scratch replay and the independent ledger recount.

All five mutation controls are rejected. The profile is R = 17,904, W = 21,424, m = 72, deficit 1,936,
the same deficit as every PR168-derived word.

**Physical layer.** The same `virtual` stage then runs Chafik Boukhalfa's PR200 classes
(`gen4bit/bit/word.py` and `base_word.py`), also unmodified, exactly as PR200's `bit/prove.py` runs them on
its own word. `prepare.py` builds the verifier context from the same classes. They check:

- every changed operation frame (1,802) is nondegenerate and contains its node's value span;
- the execution order preserves each role chronology;
- gauges are untouched in phase one, every gauge read precedes its role's first use, and gauge targets equal response supports;
- the 1,494 handoffs are one-to-one between ungauged non-root donors and gauged recipients;
- each donor is dead before its recipient's read, and its last frame lies in the recipient's gauge frame;
- all gate ports are distinct.

The stage also recomputes the physical row:

- phase one is exactly the centre closure;
- every addition's actual operands are checked;
- every physical role chain and the actual target chronology are nested;
- the deficit telescopes, at 1,936.

It executes the physical word on all 19,930 formal columns over F₂ and on the defining integer decoder.
Four adverse controls are rejected: an omitted compensation, a missing partner delivery, a stale recipient
read, and a zero operation frame. `prepare.py` also recomputes the literal adjoint and asserts it equals
PR200's.

The handoffs follow PR200's rule. A recipient is read immediately before its first operation. The only
recipients used are rank-21 gauges with no strictly larger gauge later on any of their targets, so every
target chain stays nested. The actual chronology is rechecked by the scalar program.

## Unchanged scalar program and empty selections

`scalar/word.py` is the source527 scalar program, byte-identical (sha256 e675d4eb…). Its source527
selections are all empty for gen4:

- source loans, early and gauge mixes, retimed prefixes;
- aggregation, rank and echelon groups;
- fresh and paired source reads, terminal sinks.

The program then executes exactly the PR200 physical word:

1. dirty compensation at D0;
2. V injection and the phase-one gates;
3. the 24 copied-centre scatters;
4. gauge reads at their read times, interleaved with the remaining gates;
5. side roots, then partner mixes and deliveries;
6. cleanup, the inverse gates, and V removal.

`scalar_check.py` runs it on all 19,930 formal F₂ columns (1,760 sources, 1,760 targets and 16,410 dirty
registers) and in both defining-integer directions with 24-bit packing.

The 25 source527 mutations exercise selections that gen4 does not have. They are replaced by 11
corruptions of the actual gen4 context, each of which must make the unchanged program fail:

- a dropped gauge, dirty or recipient compensation;
- a misrouted gauge response;
- a flipped compensation sign, checked over Z;
- a recipient read before its donor's last write;
- a gauge read after its first use;
- an omitted gate, centre scatter, partner delivery or source injection.

## Physical events, parity fusion and global lowering

`code/physical527.py` observes the scalar program and emits the physical frame tags. The emitter is
source527's, unchanged except the register count. The local scalar projection must equal the independent
observer, and every MOVE is checked as an exact frame inclusion.

`parity_transform.py` deletes the 1,510,656 even-coefficient payload ADDs, which are identities over F₂.
It merges no MOVE chains for gen4, so the paid local histogram is unchanged. The independent
required-use census rebuilds every path from the surviving operations and mathematical endpoints, checks
both reflected inclusions, and matches the instruction histogram. The 626,360 surviving payload additions
and their literal inverse are replayed on every F₂ column, with cancellation-free signed prefix bounds
21,725 (forward) and 1,850,360 (inverse). The proof/PARITY-CONTRACT.md argument applies unchanged.

`code/global_lowering.py` is PR234's lowering with the register count and the entrance census rebound. It
expands all five stages, the idle and bridge phases, the 2,466 completions and the terminal exchange. It
checks every operand namespace and the paid five-stage histogram:

- 487,546 calls;
- rank mass 2,809,600;
- deficit 4,400 = 4v − 5ℓ.

`code/geometry527.py` checks the exact rational h=24/m=120 routes, the eight idle boundary pairs for two
actual ports, and the completion projectors and five disjoint windows. It does so for two actual rank-20
entrance bases and, newly, one actual rank-21 basis.

## Primes, banks, moments and finite bill

**Primes.** `prime_check.py` recomputes the cleared-Gram determinant of every consumed basis: 26,249
distinct bases, at most 118 bits. Only 2, 3 and 5 are stripped, every residual is below 2⁸⁰, and the
retained prime range q > 2⁸⁰ is unchanged.

**Banks.** The independent entrances are 2,200 of rank 20 and 266 of rank 21, with 370 distinct bases.
Their residual families have widths 4 and 3. `BANK-PROOF.md` gives the stage-private banks:

- (3⁴⁰) × 399 banks;
- (4³⁰) × 4,400 banks;
- (24⁵) × 167,328 banks.

`bank_check.py` rebuilds the 370 charts (at most 186 factors) and enumerates all 4,923,000
role/replica/stage assignments, checking the callable route map and both endpoint directions. It removes
exactly the 2,466 rank-5a exterior completions.

**Moments.** Literal stock is 1,283,035. The normalized profile has m = 120, W = 256,607, rank mass
30,740,040, deficit 52,800 and largest child 50. Two independent rational moment engines, including the
complete 10⁻¹⁶ bad-class fallback, give the bit coarse saving 180848186599613/(2.5·10¹⁷). The adjacent
10⁻¹⁸ grid point is rejected.

**Assembly.** The retained complex supplier (PR234/PR193 at m = 110, coarse 747454944651775/10¹⁸) is
rerun. The bit supplier binds. Three completed ordinary-leaf levels feed the unchanged balanced outer
assembly: all 47 strict inequalities and seven margins are positive, and the adjacent final grid point
fails.

**Finite bill.** `finite_check.py` pays every PR234 primitive and router allowance on the literal 60
replicas and stock, and adds all 502,915,820,400 bank selector calls.

## Scope

The proof boundary is unchanged and conditional. The following are inherited interfaces:

- the all-size weighted compiler and common ancestor charts;
- restored rows and completed ordinary leaves;
- selectors, exact-tape routing and prime supply;
- precision/recovery and retained complex symbolic correctness;
- analytic transfer.

These checks establish the stated finite construction under those interfaces. They do not rebuild Lean or
execute a multiplier at all input sizes.
