# Compact saturation audit: exact agreement and invariant repair

Status: **mathematical audit / research note; no new kappa**.

For the unchanged earlier-source compact-control word, saturated temporary
digits are sometimes safe. This package proves the exact full-map agreement
criterion and the largest subset of it invariant under the intended XOR.
Agreement at one address alone is unsafe as a current-address repair guard.
The retained construction and previous sufficient guards remain correct.

At n=2,K=6,G=2, the invariant good fraction increases from Hanson Sun /
bbMisk's PR1219 `567/1024` to **`1499/2048`**. The full agreement fraction is
`6841/8192`, but that larger set is not invariant. Two exact 2-by-2 transfer
matrices count the agreement set and invariant set for every n>=1, G>=1,
K>=G+1 and 0<=rho<K. The [proof](PROOF.md) distinguishes the all-n argument
from finite evidence and retains every operation and repair charge.

## Reproduce

From a full checkout, Python 3.10+ and the standard library:

```sh
python3 -I -O -B research/compact-saturation-audit-seed69/verify.py
```

Expected:

```text
PASS_COMPACT_SATURATION_AUDIT states=1196544 physical=1536 controls=7 headline=1499/2048 no_new_kappa
```

The optional bounded CI hook uses the repository's existing runner:

```sh
python3.12 -B scripts/research_package.py --package research/compact-saturation-audit-seed69
```

It also checks Git provenance and prints
`PASS_REGISTERED_RESEARCH_PACKAGE research/compact-saturation-audit-seed69 outcome=completed`.
This wrapper needs the pinned Git history; the direct command needs only
this package and the six declared live input files at their repository paths.

The verifier checks six SHA256/Git-blob source pins, compares its deterministic
result with [RESULT.json](RESULT.json), enumerates 38,080 local transition
cases, and visits all **1,196,544 quotient states** in six complete domains.
Every target bit at or above rho remains in each quotient. All temporary
digits and selected source bits are enumerated. Unused source bits, low
target bits and the back field are spectators in the written argument.

Every finite raw map is checked for bijectivity and inverse equality. The
carry criterion is compared with the full output (including the temporary).
The invariant predicate is independently compared with `E intersect T(E)`;
the checker validates every sorted exceptional-repair destination and unique
payload. Seven named controls cover lost dirty state, saturation, unsafe
agreement-only repair, carry propagation and harmless final carries.
An additional 1,536 seed-69 full physical states compare the separate integer
implementation with the original swap/rotation interpreter, including
arbitrary dirty back fields, inverses, repair and highest-bit completion.
Half those samples explicitly force one saturated temporary digit.

This is a fixed domain audit, not a candidate search. The finite domains and
completed counts are in RESULT.json; the stopping rule was to complete those
domains and the proof, then verify and hand off. Sample seed 69 is separate
from the exhaustive coverage. No universal claim rests on random samples.

## Sources, scope and credit

Exact research base: `410026dc5513b87db92ae98571d1d5984c69a983`.
The selected result at that base is conditional
`kappa=836330098538459/500000000000000000`; its complex supplier binds.
[SOURCES.json](SOURCES.json) pins the six execution/test inputs and records
the selected certificate as historical context. It does not require the
selected frontier to remain unchanged in future checkouts.

Credit Douglas Colkitt for the compact-control construction, movement note,
physical simulator and repair interface; OpenAI for the original framework;
Hanson Sun / bbMisk [PR1219](https://github.com/CrocSwap/integer-mult-bounds/pull/1219)
at `dfb453c88b03868d346014867a091d36e7b16589` for the nonsaturated multi-digit
criterion; and @martinxxx9
[PR1108](https://github.com/CrocSwap/integer-mult-bounds/pull/1108) at
`b76bb2853be4e7001508582b10913e32ad7aba9f` for the one-digit boundary law.
The new result changes the nonsaturation hypothesis, accounts for compact
carry propagation across multiple digits, and proves the maximal invariant
guard with exact correlated densities. No pending code is imported.
The later-source sufficient guard in
[PR1247](https://github.com/CrocSwap/integer-mult-bounds/pull/1247), pinned in
SOURCES.json, addresses a different composition and is not assumed here.

All additions are confined to this directory. The source word, production
guards, selected result, frozen evidence and upstream/ are unchanged.
The [claim](CLAIM.md) records the OS-random track assignment, three candidate
tasks, overlap coverage, budget and handoff. [VALIDATION.json](VALIDATION.json)
records executed checks and their limits.

Prepared by **Sagar Thakrar**, with substantial **OpenAI Codex assistance** in
derivation, implementation, checking and writing. Apache-2.0 under the
repository license; retained source notices apply. One agent, no independent
human or proof-assistant review. Finite success is not formal verification of
the multiplication theorem. No full supplier replay or physical/tape/hosting,
precision or analytic admission is claimed. There is no practical runtime
measurement and no kappa change.

## Open next questions

- **Later-source invariant core:** does composing the two raw earlier-source
  calls admit a comparable exact maximal guard, including cancellations that
  PR1247's individually safe subcall guard excludes? This could further reduce
  the repair envelope. Start from that pinned physical interpreter, keep all
  source-load carries, and test full dirty-state restoration. It needs a new
  proof; this earlier-source guard cannot be substituted blindly.
- **Production adoption:** does the broader predicate improve an actual
  complete implementation after predicate scanning, address recovery and
  sorting costs? Start with the unchanged repair pipeline and benchmark the
  same complete input under both predicates. This needs a physical realization
  and maintainer review, not just the density improvement proved here.
