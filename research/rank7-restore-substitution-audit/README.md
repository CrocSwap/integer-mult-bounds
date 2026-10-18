# Independent audit of the two literal restore substitutions

This package independently proves the two PR3042 restore identities and recounts
their frame costs without importing any predecessor code. Both providers pass.
The total paid-profile saving is correct. The literal edits differ from the
public description inspected during this session.

The source is dcharb78's [PR3042][3042], exact head
`84cc406ad91ec53fff329a11a445d7effe564a77`, on Marius-Paul Dumitrean's
[PR2979][2979] words. Jeremy Kothe's [PR3015][3015] supplied the declared-edit
interface and first restore skip. Canonical main is
`d8e0f83f00191df62174b641e9fff055c357f641`, priority revision 6.

## Result and description correction

For each provider, the actual source-addressed edits have these effects.

| Literal edit | Original gates | Replacement gates | Registers skipping rank 8 | Local delta |
|---|---:|---:|---|---|
| `R1_E42`, restore `[162:188]` | 26 | 33 | 22, 40, 54, 63 | `-8 H1 + 4 H2` |
| `R2_E7`, restore `[190:203]` | 13 | 15 | 5, 73 | `-4 H1 + 2 H2` |
| Combined | 39 | 48 | All six | `-12 H1 + 6 H2` |

The inspected PR body instead describes 29 and 14 replacement gates, with three
skips per block and register 22 assigned to the second block. The
[description snapshot](evidence/DESCRIPTION-SNAPSHOT.json) preserves the relevant
quotes and observation time. This is a description correction, not a
counterexample to the final word or its total saving. The immutable literal
lists and independently recounted isolated edits establish the table above.

In particular, the first literal edit already contains the temporary aggregation
`X40 -= 2 X54` at their common rank-seven frame. It does not implement the
public body's described carrier-369/carrier-450 construction. Downstream work
should consume the pinned lists rather than reconstructing that narrative.

The combined local profile is

```text
PR2979   {1:2445, 2:706, 3:232, 4:108, 5:18, 8:8}
PR3042   {1:2433, 2:712, 3:232, 4:108, 5:18, 8:8}
```

Each changed register replaces its final `7 -> 8 -> 9` itinerary with a direct
`7 -> 9` transition. No other register's jump histogram changes. The audit
checks every literal A/B/restore frame, the A and B warp boundaries, the center cuts
and all final endpoints. The emitted evidence contains the changed registers'
complete transition histories, not just their sums.

## Exact substitution proof

Let every register hold an independent arbitrary dirty value in a vector space
over the rationals. An ADD replaces row `t` by `row(t) + c row(s)`. A SCALE
multiplies its row by its exact rational coefficient. For each hunk, the checker
starts with the identity matrix on the union of its touched registers and
computes every row before and after substitution. The matrices agree exactly.
Untouched rows remain identity, so this is equality on all 704 input columns,
not merely on target outputs or on a sampled reachable state.

The verifier also checks the complete restore operator and reconstructs the
literal final restore from the two nonoverlapping original-address preimages.
All other word sections except report and inverse cleanup are unchanged.
Therefore the hunk identities substitute into the inherited word for arbitrary
intermediate register values. They preserve the full scalar operator, its
inverse and its dual, even when preceding operations are symbolic linear
operators. This implication does not require a fresh replay of those preceding
operations.

Cleanup is checked separately as the inverse reverse of the actual forward
body, with the same injective renaming of the 91 restored helpers into their
private buffer registers. The larger replacement adds nine restore gates and
nine cleanup gates. The audit does not call those physical operations free.
The native/program cost of their implementation remains a separate obligation.

`frames.py` independently represents each binary frame by its full set of at
most 512 vectors. It uses set containment and cardinalities, not the inherited
Gaussian-elimination routine. The ordered 408 helper widths are unchanged in
both providers, with inventory `{4:26, 5:2, 6:16, 7:52, 8:99, 9:213}`.
The private-buffer namespace is unchanged; all 91 buffers remain charged.

## Complete bill implication

The literal T74 fill, order and dispatch are byte-identical to PR2979's inputs.
[VENDOR.json](VENDOR.json) binds their PR3042 hashes, while
[SOURCES.json](SOURCES.json) binds the working predecessor bytes. Together with
unchanged ordered widths and unchanged call boundaries, this preserves the
baseline geometry problem and idle bill. Baseline legality is a premise here;
this audit does not rerun the geometric owner checker.

There are 666 calls. Replacing their local profiles in the original complete
profile reconstructs the shipped PR3042 profile exactly:

```text
delta = -7992 rank-one children + 3996 rank-two children
profile = {1:1637688, 2:474192, 3:159468, 4:71928,
           5:13716, 8:5328, 48:28190}
rank mass = 4816512 = 74 * 65088
physical stock = 66304 + 408 + 8 + 91 + 2 = 66813
```

For `Hr(b) = r (73/r)^b`, the per-call difference is

```text
6 H2(b) - 12 H1(b) = 12 * 73^b * (2^(-b) - 1) < 0, for every b > 0.
```

Both constructions have the same complete-moment normalization and idle bill.
Thus the complete recursive moment strictly improves at every positive saving,
conditional on the inherited boundary and baseline allocation. This proof uses
no floating-point decision and needs no new numerical root calculation.
It does not certify the reported numerical kappa, bit-side cap or outer transfer.
No new kappa or selected-frontier change is claimed.

## Reproduce

Only Python's standard library is needed. The registered commands check pins,
both providers and semantic failure controls in about two seconds locally.
They do not generate words or logs in the checkout.

```sh
python3.12 -B scripts/research_package.py \
  --package research/rank7-restore-substitution-audit
```

To compare the deterministic result with the retained evidence, write outside
the checkout:

```sh
python3.12 -B research/rank7-restore-substitution-audit/verify.py > "$RUN/result.json"
cmp "$RUN/result.json" research/rank7-restore-substitution-audit/evidence/RESULT.json
```

Thirteen behavioral groups cover positive words, every hunk's dropped gate and
wrong coefficient, arbitrary dirty source restoration, exact preimages,
unlisted changes, illegal/dependent frames, stale and incomplete cleanup,
stale profiles, an unpaid child and changed source bytes. Optimized execution
produces the same receipt because proof checks do not use removable assertions.
See [ENGINEERING.md](ENGINEERING.md) for diagnostics and resource limits.

The initial bounded construction probe combined E45 sources 70/71/72. Their
joined preceding frame already equals the consumer frame, and the tested
rewrites retained the paid histogram. That probe is not a general exclusion;
no unsuccessful candidate is proposed as an improvement.

## Limits

This is a code-disjoint finite scalar/frame audit, not independent human or
formal-kernel review. PR3042's author already supplies forward/dual free-operator
audits and full-release receipts. The new coverage is the standalone rational
substitution proof, independently enumerated frame itineraries, isolated-edit
attribution correction and unchanged-boundary invoice implication.

Native Clifford phases, arbitrary-size compilation, physical backing and
movement, prefix/magnitude and precision/tape costs, recursive callers, analytic
transfer and universal block-energy assumptions are not verified here. Physical
stock arithmetic alone does not establish those contracts. The current selected
record remains unchanged. The live T740 composition claim is separate.

## Open next questions

1. Independently replay PR3042's exact native/admission/outer chain before
   adoption. Start with its declared full reproduction command and fresh
   external outputs; compare actual word and invoice hashes. This needs a
   separate compute budget and scientific review of inherited hypotheses.
2. Correct the mutable source description to match its literal edits, or publish
   a separately bound realization of the described alternative. This matters
   because downstream composition needs the actual gate chronology and extra
   scalar work. The table above and the pinned lists give the first check.

## Credit

Nick Petalas contributed this independent audit and description correction.
Credit dcharb78 for PR3042's two literal rewrites, Jeremy Kothe for PR3015's edit
interface and first restore rewrite, and Marius-Paul Dumitrean for PR2979's words
and allocation. The unchanged [credits](vendor/CREDITS.md) and
[notice](vendor/NOTICE) retain Mason Hale, Jeremy Diviney, Yiyang Lu, Tekalign,
Ross Richardson, Dugongue, icekylinx, themilkman216 and the geometry/native/owner
lineage. Apache-2.0. Development used substantial automated assistance.

[3042]: https://github.com/CrocSwap/integer-mult-bounds/pull/3042
[3015]: https://github.com/CrocSwap/integer-mult-bounds/pull/3015
[2979]: https://github.com/CrocSwap/integer-mult-bounds/pull/2979
