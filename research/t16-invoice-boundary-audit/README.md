# Selected T16 invoice input boundaries

This package follows [Josie Elliston's PR1959](https://github.com/CrocSwap/integer-mult-bounds/pull/1959)
and its [invoice handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18926858).
It tests the **inputs** of the unchanged PR1087 `code/invoice_allcold.py` used by selected
#1094. It then passes every invoice survivor through the actual `assemble()` function,
including the JSON serialization boundary used in production. For selected template
mutations it also invokes the original upstream controller audit.

The result is a bounded acceptance-boundary audit, not a new construction, a cold replay,
or a reported acceptance bug in the complete selected chain. No selected source or κ changes.

## Result

The honest invoice reproduces every field of the archived selected invoice. Honest assembly
reproduces the archived assembly, including all exact moment and outer witnesses; only the
fresh invoice's file hash is normalized after checking it against the actual regenerated file.
This accounts for JSON newline conventions. The original controller also reproduces its
archived receipt except for the two fields recording whether its shipped mutations were run.

| Real-file cases | Invoice rejects | Invoice accepts | Assembly rejects survivors | Assembly accepts survivors |
|---|---:|---:|---:|---:|
| 54 | 28 | 26 | 16 | 10 |

Each case starts from the honest fixture. Changed hashes are rebound to **actual changed bytes**,
except for four explicitly labeled stale-link controls. Checkers and their globals are not patched.
The invoice's returned in-memory dictionaries are not passed directly to assembly: profile keys
become strings at the real JSON boundary. The positive assembly check guards against confusing
such a harness error with a semantic rejection.

`EXPECTED.json` records each outcome, the exact frozen rejecting statement, changed invoice
fields and finite quantities. All observed rejections are `AssertionError`s. This is a selected
set of input cases, not exhaustive statement or predicate coverage.

## Finite gates exercised through their producer

These cases reach the real invoice calculation, without editing its output flags.

| Gate | Input construction | Actual result |
|---|---|---|
| Prefix | Insert inverse dyadic scales on one data register before the original forward program; rebind program hashes and claimed local accounting | 511 bits accepted by invoice; 512 and 513 rejected at line 288, with all nine finite checks true |
| Row | Increase physical/live counts, rank mass and parent reserve coherently around the exact stock bit threshold | Row 20159 accepted by invoice; 20161 rejected at line 284 with only `row` false |
| Logical | Choose retained allowance around `floor((2^6050 - 65)/group) - fresh_parent_price` | The last admissible logical value passes; the next allowance is rejected with only `logical` false |
| Halving | Replace 52 rank-one children by one rank-52 child, preserving mass | Rejected at line 284 with only `halving` false |

The prefix pair multiplies by `2^p` and immediately by `2^-p`; its exact endpoint is unchanged
and its forced intermediate magnitude is `2^p`. Powers 181, 182 and 183 give invoice prefixes
511, 512 and 513. Claimed local receipts are deliberately adjusted adversarial inputs;
**this package does not rerun the independent native supplier replay for those changed programs**.
The 511-bit case is rejected by assembly's fixed provider contract. The altered row geometry is
also rejected by assembly's fixed selected rank mass. These accepted invoice cases do not become
admissible selected suppliers.

The original selected prefix is 397 bits and row coefficient is 16469. No resource-unbounded
input intended to exceed the local primitive-count gate was constructed. The original provider
word, wrappers and scalar semantics are not exhaustively mutation-tested here.

## Why five finite checks are implied under explicit hypotheses

Let `S` be physical stock, `M` streamed rank mass and `L` logical work. Assume integers
`S >= 1`, `0 <= M < 73 S`, `0 <= L < 2^6050`, the fixed compiler `C = 64 * 74^3`, and
the retained row condition `2 bit_length(S) + 11185 < 20161`. These hypotheses imply:

1. `bit_length(S) <= 4487`, so `S < 2^4487` and `M < 2^4494`.
2. `C < 2^25`, `L + 1 <= 2^6050` and `S + 1 <= 2^4487` give
   `C (L + 1) (S + 1)^2 < 2^15049 < 2^30000` (router).
3. The literal expression `2 * 2^30000 S^2 + 8M + 4S + 4 + 32 * 73`
   is less than `2^38976 < 2^100000`.
4. With `T = M + 2^100000`, `T < 2^100001` (mass),
   `32 * 73 * T^2 < 2^200014 < 2^210000` (precision), and
   `2T + 18 < 2^100003 < 2^210000` (tape).

Thus those five guards cannot fail alone while the stated hypotheses hold. `verify.py`
checks each maximal integer bound exactly. The inequalities are monotone over the stated
nonnegative domain, which supplies the quantified implication rather than merely sampling it.
For the honest geometry, `M < 73S` follows from
`rank_mass = 73 * live - 5120`, `physical = live + helpers + 10`, and positive helpers.
**Nonnegativity is an explicit hypothesis, not a claim that the invoice enforces every valid
profile/receipt condition on arbitrary forged inputs.** Negative-count cases are separately
rejected by assembly. This implication concerns these finite expressions only; it proves no
all-size precision, tape or multiplication theorem.

## Where invoice survivors are excluded

- **Four altered templates pass invoice and assembly:** helper/data-owner aliasing, omitted idle
  children, a bridge coefficient sign flip, and a bridge coefficient `2^513` exceeding the charged
  512-bit payload. The real upstream `audit()` rejects them at lines 152, 181, 111 and 111 respectively.
  In the strict driver, this audit runs before invoice and assembly. The bridge case shows why
  the invoice's 397-bit arithmetic certificate alone is not a checker of arbitrary bridge coefficients.
  It assumes the controller-established unit bridge factors.
- **Two changed controller control-run fields pass invoice and assembly.** The original assertion
  at `verify_t16.py:103` rejects both. The harness executes that one extracted, unchanged assertion
  against each changed receipt, with an honest positive control. This is an isolated final-binding
  predicate check, not execution of the whole driver.
- **Two controller metadata changes pass both:** `status='FAIL'` and inconsistent `rank_mass`.
  These fields do not affect this invoice or assembly. The latter consumes owner rank mass instead;
  the real controller regenerates its receipt. This is not evidence of changed arithmetic or of a
  forged receipt surviving the complete source-bound replay.
- **Two changed retained allowances pass both:** a smaller positive extra allowance and the last
  allowance below the logical gate. Both still add the complete fresh parent price. They preserve κ.
  The original retained input is explicitly pinned by the frozen `data/UPSTREAM-PINS.json`, checked
  by `verify_t16.py:34-35`; the harness confirms its pin and that these changed bytes violate it.
  They are not new selected-source prices or demonstrated undercharges.
- **Sixteen other invoice survivors are rejected by actual assembly.** These cover owner/charts/idle
  receipts, a stale controller link, reordered calls, parent reserve undercounts, zero or negative
  retained allowances, changed or negative rank counts, coherent live-stock undercounts, and the
  just-below row/prefix cases. Parent idle and bank-stock changes reach assembly's independent
  parent-envelope recount at line 149, rather than an unrelated stale-hash guard.

The shipped 69 admission controls mutate already-produced invoice/owner objects. Some checks
overlap this suite (profiles, call order and parent price); the new evidence is that the invoice
producer itself accepts or rejects these actual changed inputs, with tight prefix/row/logical
boundary pairs and an explicit upstream/assembly classification. The controller rejection
behavior is credited to the existing checker and PR1959, not presented as a new controller bug.

## Reproduce and scope

```sh
python3 -B research/t16-invoice-boundary-audit/verify.py
python3 scripts/research_package.py --package research/t16-invoice-boundary-audit
```

Checked with native Windows CPython 3.12.9 and Ubuntu 24.04 CPython 3.12.3, with identical
receipts. The registered Linux replay used one CPU, took 2m22s and peaked at about 0.90 GiB RSS
on the donor machine; these are observations, not portable resource guarantees.

Python 3.12, standard library only. The verifier extracts its hash-pinned archives into a fresh
temporary directory, applies the selected stage's three frozen data overlays, and restores original
input bytes after every case. Source and fixture archives, the retained invoice and three moment/
outer engine files are declared in `SOURCES.json` and `VERIFY.json`. `--write` regenerates the receipt.
The fixture is selected #1094 at source head `0fc329d0bec93ca7cd288eaea1295172e8789810`;
the catalogue and selected record at task selection are pinned as historical provenance.

No entire cold chain, other historical supplier, arbitrary multi-provider case, or all-size transfer
obligation is verified by this package. It does not install a hardening wrapper or change a frozen
stage. A separate donor-session cold replay is not required by, or silently included in, this receipt.

## Open next questions

1. **Test the local-provider input boundary more fully.** Why: the finite input suite does not enumerate
   `recount_provider()`'s wrapper, scalar/Horner and receipt-binding predicates. First step: retain
   this positive control and mutate actual provider files with correctly rebound references, separating
   independent native replay rejection from invoice rejection. Blocker: a bounded meaningful case set
   and a fresh native replay for any claimed valid changed program.
2. **Should a successor wrapper bind controller and retained artifacts explicitly at its public entry?**
   Why: invoice plus assembly are insufficient as a standalone admission API. First step: specify an
   entry contract and test the four controller-rejected template cases and changed retained inputs through
   it. Blocker: maintainer decision; frozen predecessor code must remain unchanged.
3. **Trace conditional finite hypotheses to all-size statements.** Why: the five implications above
   are finite and require positivity and fixed compiler/row constants. First step: identify one exact
   retained precision or tape lemma and quantify its inputs before attempting a proof. Blocker: this
   package provides no all-size realization argument.

## Credit

Prepared by Tairitsu-Aya with substantial OpenAI Codex assistance in source inspection, experiments,
implementation and writing; no independent human review is claimed. Josie Elliston's PR1959 supplied
the explicit handoff and the model for reporting acceptance separately from complete-chain validity.
Its use of `marshal` for JSON-data copies follows jackmgaller's PR1939 observation; equality is checked
before use. The frozen invoice retains its PR558 → PR552 → PR531 scalar/Horner and finite-cost lineage,
the exact moment/outer lineage, and the T16 controller credits to Hao Yan (@FanPUYen) and the selected
construction contributors, including Jeremy Kothe and Rohan Arun. All frozen notices are preserved;
this new package is Apache-2.0.
