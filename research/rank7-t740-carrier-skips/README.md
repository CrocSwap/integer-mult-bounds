# T740 packing with six restore carrier skips

This composes dcharb78's six-skip words in [PR3042][3042] with Nick Petalas's
cap-attaining T740 allocation in [PR3030][3030] and [PR3024][3024]. The exact
complete complex moment root is in

```text
[0.0017297379500642785512428,
 0.0017297379500642785512429].
```

The packing-only gain over PR3042's T74 root is approximately `1.78367636e-9`.
All 2,717,280 helper roles, idle remainders and 91 private buffers remain
charged. The allocation attains the exact fixed-inventory additive-bin cap
at the new root. The selected result is unchanged.

The fresh complete release passed in 1,749 seconds, including a fresh retained
bootstrap, both edited native providers, complete admission and both modern
outer checks. Its released endpoint is

```text
0.001729737950064278551242 - 10^-46 - 10^-70.
```

The exact released gain over PR3042 is `178367636256443 / 10^23`.
[COMPOSITION-RESULT.json](evidence/COMPOSITION-RESULT.json),
[RELEASE-RECEIPT.json](evidence/RELEASE-RECEIPT.json) and the authenticated
stage logs record the execution. This remains conditional finite evidence.

## Exact composition

The scientific base is canonical main
`d8e0f83f00191df62174b641e9fff055c357f641`, priority revision 6.
PR3042 is pinned at `84cc406ad91ec53fff329a11a445d7effe564a77`; PR3030 is pinned
at `78e77d820393c6b8648b47af219e991edfcc54e6`. [VENDOR.json](VENDOR.json) gives
every retained file's origin, Git blob and SHA256. [ADAPTED.json](ADAPTED.json)
identifies the adapted PR3030 files. No frozen predecessor changes.

Both PR3042 words reconstruct exactly from their two declared restore edits.
The new checker compares their rational action on every dirty-input basis
column, then checks the literal inverse cleanup. Source gates, A/B, warps,
source cut, compensation, helper endpoints, entrance frames and every ordered
helper width remain unchanged. Equal width histograms alone would not make
the literal fill compatible.

The actual edit block lengths are `26 -> 33` and `13 -> 15` gates. Some PR3042
prose counts and integer price summaries are stale. The checked invariant is
its literal per-call profile delta `-12 H1 + 6 H2`, not those prose prices.
The fresh source/native chain separately checks the edited frames. The
concurrent [PR3050][3050] gives a separate literal-substitution audit; its
checks complement this full T740 composition and release.

PR3018's preimage-bound 103-row journal acts on the original T74 fill. The
retained PR3024 lift interleaves ten copies and applies its preimage-bound
550-row journal. Materialization streams the exact 6,660-call order, dispatch
and 2,717,280 rows into the actual admission CLI. Relative to PR3030, each
call saves five additional hyperplane stops, for a complete delta of
`-66,600 H1 + 33,300 H2`.

The resulting complete paid profile is

```text
{1:16376940, 2:4741920, 3:1594737, 4:719280,
 5:137085, 8:53280, 48:281903}.
```

Its mass is `48,165,120 = 740 * 65,088`. The idle profile is unchanged at
`{1:173160, 3:49617, 5:17205, 48:281903}`. The finite owner checker verifies
every source window, excluded active family, helper identity, ordered width,
capacity, disjoint mask and compact pending prefix. Physical stock is
`663040 + 408 + 8 + 91 + 2 = 663549`.

## Packing proof and full bill

Write `Hr(b) = r*(73/r)^b`. Subtract ten copies of PR3042's complete T74 bill:

```text
60 H1 + 57 H3 - 75 H5 + 3 H48.
```

After division by `73^b`, this is
`f(b) = 60 + 171*3^(-b) - 375*5^(-b) + 144*48^(-b)`.
Here `f(0)=0`. On `[0,1/100]` its derivative is at most

```text
375 ln(5) - 171 ln(3)/3^(1/100) - 144 ln(48)/48^(1/100) < 0.
```

The verifier bounds that expression with exact rational logarithm and
exponential intervals. Thus the complete normalized moment improves strictly
throughout `0 < b <= 1/100`. The retained interval engine separately brackets
the old and new roots.

The verifier recertifies the unchanged 2,551-pattern cap at the six-skip root:
12 patterns are identically tight and 2,539 have strictly positive reduced
cost. Its primal idle counts times 740 equal the literal idle histogram, so
100% of this fixed-inventory cap is realized. The broader coverage-law
relaxation from `complex-local-word-ceiling/ceiling.py` is also reported in
[FINITE.json](evidence/FINITE.json). It allows idle shapes outside this exact
bin model and supplies a separate, looser ceiling:
`[0.001756958123098, 0.001756958123099]`. The composition realizes about
`98.45072158%` of that broader moment cap, alongside 100% of the exact
fixed-inventory cap.

The physical stock contributes a 1,512-bit reserve under the charged 2,048
bits. The T740 namespaces are centers `[663040,663048)`, helper tableau
`[663048,663456)`, private buffers `[663456,663547)` and coefficient work
`[663547,663549)`. The 18 active layers are per replica. The arbitrary-T
parent has its own stock and rebuilt invoice.

The full wrapper authenticates PR3042's exact source package and changes only
the admission `--fill`, `--order` and `--dispatch` arguments. Both edited native
providers, their new manifest and exact words, the actual fill/order/dispatch,
complete invoice, admission and modern outer release must agree. An R1-only
native receipt cannot satisfy these bindings. The stored checker also binds all
eleven invoice artifacts per provider to the new native receipt, authenticates
the local prefix reports and recomputes the exact global prefix formula.
A stale R1 invoice and understated local/global prefix or stock are rejecting
controls, even when their adjacent payload digest is updated.

## Reproduce

Python 3.12 and the standard library suffice for the registered finite replay:

```sh
uv run --python 3.12 --no-project python -B scripts/research_package.py \
  --package research/rank7-t740-carrier-skips
```

The separate full replay needs the packages pinned in
[requirements-full.txt](requirements-full.txt), a native C++ compiler and the
Git objects listed in [GIT-SOURCES.json](GIT-SOURCES.json). In a full Git
repository, fetch those exact objects, install the pinned packages in a
private Python 3.12 environment, and run:

```sh
python3.12 -c 'import json, subprocess; subprocess.run(["git", "fetch", "origin", *[r["head"] for r in json.load(open("research/rank7-t740-carrier-skips/GIT-SOURCES.json"))]], check=True)'
six_skip_run="$HOME/.cache/integer-mult-bounds-runs/my-six-skip-session"
uv venv --python 3.12 "$six_skip_run/venv"
uv pip install --python "$six_skip_run/venv/bin/python" \
  -r research/rank7-t740-carrier-skips/requirements-full.txt
"$six_skip_run/venv/bin/python" -B research/rank7-t740-carrier-skips/reproduce.py \
  --repo . --work "$six_skip_run/work"
```

The work path must not exist. No network fetch occurs during the replay. The
recipe derives the native providers and complete admission afresh. Exports,
materialized rows, native outputs and logs stay outside the checkout. The
registered command checks the finite construction, behavioral controls and
stored fresh-release relations; it does not repeat the full native chain.
[ENGINEERING.md](ENGINEERING.md) records bounds and retained runtime exceptions.

## Scope

This is a conditional finite composition. Exact child counts, source bindings,
chronological allocation and the supplied finite release are checked. Physical
backing/movement, arbitrary-size/compiler realization, precision/tape, caller,
analytic transfer and universal block-energy hypotheses remain inherited.
Neither the selected result nor other PR dispositions change.
The selected-result cold replay, Lean and Docker are outside this isolated
composition; hosted CI is separate from the recorded local execution.

## Open next questions

The next useful task is an independent source-bound replay and review of this
exact composition before admission. Start from the pinned Git exports and
compare the provider words, literal fill, complete invoice and outer receipt.
The runtime/environment and inherited premises are the blockers. No further
packing search inside the attained fixed-inventory cap is justified here.

## Credit

Nick Petalas. Apache-2.0. Substantial automated assistance was used for the
implementation, checks, internal review and prose; no independent human or
proof-kernel review is claimed.

Credit dcharb78 for PR3042's six carrier/pivot skips; Jeremy Kothe for PR3015's
edit stage and R1 precedent; Marius-Paul Dumitrean for PR2979's joint rank-seven
words, five paired extractions, literal fill and release machinery; Nick
Petalas for PR3018/3024/3030's journals, T740 lift and release wrapper; Mason
Hale, Jeremy Diviney, Yiyang Lu, Tekalign, Ross Richardson, Dugongue, icekylinx,
themilkman216 and the retained geometry/native/owner lineage. The exact copied
notices and credits remain under `vendor/`.

[3042]: https://github.com/CrocSwap/integer-mult-bounds/pull/3042
[3030]: https://github.com/CrocSwap/integer-mult-bounds/pull/3030
[3024]: https://github.com/CrocSwap/integer-mult-bounds/pull/3024
[3050]: https://github.com/CrocSwap/integer-mult-bounds/pull/3050
