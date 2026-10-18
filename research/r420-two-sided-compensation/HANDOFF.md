# Handoff: R420 helper basis with shared target donors

Status: **verified finite circuit construction**, contributed by
**franciscoyne001-svg** with substantial **OpenAI Codex assistance**. No new
kappa, selected-frontier edit, or full multiplication theorem is claimed.

The complete PR543 R420 native word uses **18,504 instead of 26,916 XORs**,
saving **8,412**. D uses 11,510 additions, including 202 helper preparations,
68 target preparations, 10,970 feed terms and all 270 restorations. The 47
target donors are disjoint from 68 receivers, so sharing donors is legal.
All 660 arbitrary-input columns pass, every helper is restored, and the
local payload bound is 103 bits below the 104-bit cap.

Run from the repository root:

```sh
python3 -B research/r420-two-sided-compensation/verify.py
```

Expected:

```text
PASS_R420_TWO_SIDED D=19922->11510 native_ADDs=26916->18504 saved=8412 columns=660 no_new_kappa
```

Fresh unchanged C++ legality and 5/9/11-stage checks passed for the original
and changed words with authenticated Boost 1.85.0 headers. A missing-D
serialized mutation passes legality and fails all three C++ column checks.
The normalized receipts are in `NATIVE-CPP.json`; `VALIDATION.json` records
all completed and unrun checks. The default command also works without Boost.

Historical experiment base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
Only `research/r420-two-sided-compensation/` is added. Source pins retain the
historical PR543 word and consumed checkers; selected-frontier changes are
independent of this finite construction.

The bounded submission overlap refresh reached **PR946**. PR733 combines
helper and disjoint target bases (8,368 saved ADDs); PR742 provides shared
target donors with immutable helpers. This construction combines a helper
basis with shared target donors and includes a fixed-donor assignment proof.
It saves 83 beyond its original disjoint recipe, and 44 more than PR733 on
the historical PR543 baseline. PR817 has D=11,546 with a different helper
basis and disjoint targets, versus 11,510 here; its whole-word count also
includes separate PR681 changes. These are scoped comparisons, not priority
or best-known claims. No code or frozen recipe from those pending packages
is imported. See README.md for the overlap scope and attribution.

Acceptance of the semantic D interface, complete hosted-parent/whole-owner
replay, global precision invoices and changed-word outer assembly remain
integration obligations. The original all-size, common-label/mutable-basis,
hosting, residual, precision/tape and analytic assumptions remain.
