# Independent verification of PR869's U8 complex word (no new kappa)

**Status: independent verification.** A checker written from the word semantics, sharing no code with
`audit_local.py`, the PR799 verifiers or PR869's builders, accepts PR869's U8 word and PR799's selected X4 word
with exactly their claimed local profiles, and re-derives PR869's κ = 0.001661948695165034 from its PLAN profile.

| word | content sha256 | profile (independently recounted) | result |
|---|---|---|---|
| X4 (PR799, selected) | `1e1d99ba…` | `{1:2548, 2:338, 3:430, 4:194, 5:56, 8:8}` | PASS |
| U8 (PR869) | `090fd574…` | `{1:2548, 2:338, 3:446, 4:162, 5:72, 8:8}` | PASS |

Both have width inventory `{4:80, 5:32, 7:54, 8:122, 9:216}` (3778), 216 entering helpers, 126 low ends and 72 cold ends.
The same checker also accepts the chain's p6n, promo, SW4 and #741-frames words with their README profiles,
and PR645's word with its recorded `report.local_profile`.

## What is checked, and how it differs

| obligation | `audit_local.py` | here (`xcheck.py`) |
|---|---|---|
| exact scalar map | sparse `Fraction` rows, forward and dual | dense residues mod 16 primes plus a rigorous height bound (printed: below 2^91 against a 2^492 limit), so residues fix entries exactly. The dual is the inverse transpose of the forward map, so it is not replayed separately. |
| dirty compensation | propagated from target dirt | **solved**: `Comp = Rest⁻¹·E·Pre⁻¹` must be the identity plus a target←helper block avoiding every entering and low-end helper |
| frame chains, centre paths, paid profile, widths | F2 reduced bases | subspaces held as 512-bit membership sets |
| low-end inverse-row and dirt-column cones | sparse rows | exact nonzero patterns of the prefix and its inverse |
| κ | Mercator and base-two moment engines | `mpmath` interval moment at both grid endpoints, plus the seven-step bootstrap closed form |

`price.py` also checks PLAN = 72 × local + the idle remainder `{1:1, 3:1, 44:1, 48:2396}` (the same remainder as PR799)
and the deficit 2560. As a positive control it reproduces PR799's selected κ and recorded moment residuals
(−6.22e−25 / +2.33e−24). As a negative control it rejects the next grid point `b + 10⁻²⁴` for U8.

## Negative controls

- `controls.py`: six single mutations of U8, each rejected for the intended reason. They negate a scalar, drop a
  B gate, shrink a B frame, move a low-end tail to full cleanup, add a target read of an entering helper's start
  value, and claim a wrong profile.
- All 36 of PR869's mutant words (four mechanisms × global and eight slots) are rejected, and its C0/recipe words
  pass. `donation_after` fails here with "compensation is not a target←helper block": no compensation of the
  allowed form can repair it. That is stronger than `audit_local`'s "nonzero entrance response".

## Reproduce

Build PR869's chain (head `73e86f69bf9a391e3c334999f7bbe3825dc42759`) as in its README, with one correction (below).
Then, from the PR869 checkout:

```sh
PY=python3 bash research/u8-independent-xcheck/verify.sh OUT   # OUT holds x4/ and b0/
# expected last line: PASS_U8_INDEPENDENT_XCHECK   (about 50 s; Python 3.12.13, numpy 2.5.4, sympy 1.14.0, mpmath 1.3.0)
```

`VERIFY.log` is that run's output. Base commit `f567884aeb8851b6e794af1184119a3bfbe1e631`.

**Reproduction note for PR869:** its README runs `reproduce_jx.py --frames-dir /tmp/frames`, but the script only
accepts `--sw4-dir` (it applies #741's frames itself). The working command is
`reproduce_jx.py --main . --pr635 <pr635> --sw4-dir <sw4-out> --out <x4-out>`. With that flag, the rebuilt X4
and U8 words match PR869's pins byte for byte.

## Scope

This checks the finite local obligations of two words and the arithmetic from PLAN profile to κ.
It does **not** check:
- owner admission, hosting, the global invoice or the 47 outer constraints (see #813 for an independent outer check);
- the PR589 bit supplier (c is cited, and it does not bind);
- PR870;
- the parent centre-frame interface (unchanged from X4).

All-size compilation, common-label/mutable-source realization, whole-call hosting, precision/tape and analytic
transfer remain inherited assumptions. This is a finite replay, not a formal proof.

## Credit

Construction: NewBArch/jeremykothe2 (PR869) on PR799 (Jeremy Kothe), PR741 (Chafik Boukhalfa), PR645 (icekylinx)
and their lineage. The modular-CRT-with-height-bound idea parallels PR835's independent check of the #741 backward
endpoint. Assignment seed 80 (track 75–84). Prepared with substantial AI assistance (Claude Code, Anthropic).
Apache-2.0.
