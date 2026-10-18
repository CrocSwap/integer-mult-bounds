# Six restore skips composed with the T740 packing cap

**Finite checks and the complete composed release pass.** This package composes
dcharb78's PR3042 literal circuit with Nick Petalas's PR3024/3030 T740 allocation.
The finite moment gives the conditional candidate

```
kappa = 0.001729737950064278551242 - 10^-46 - 10^-70
gain over pinned PR3042 = 178367636256443 / 10^23
                       ≈ 1.78367636256443e-9
```

This is an integration of two existing constructions. Jeremy Diviney, with
substantial OpenAI Codex assistance, supplies the exact source/word/allocation
binding, completed-profile checks and composed release workflow. There is no new
scalar rewrite or allocation search in this package. No selected-frontier change
or independent human/formal-kernel review is claimed.

## Concurrent work

A pre-submission refresh found Petalas's [live claim for the same composition](https://github.com/CrocSwap/integer-mult-bounds/discussions/2612#discussioncomment-18982402),
posted during this local run, and [PR3050](https://github.com/CrocSwap/integer-mult-bounds/pull/3050)'s
separate code-disjoint substitution/frame audit. This package claims neither
priority nor a unique composition idea. Its additional evidence is a separately
executed complete release and explicit bindings from the checked words and
literal allocation to that release. It reuses credited scientific engines;
separate execution is not code-disjoint verification of those engines.

## Exact sources and contribution

| Source | Exact head | Contribution retained |
|---|---|---|
| [PR3042](https://github.com/CrocSwap/integer-mult-bounds/pull/3042), dcharb78 | `84cc406ad91ec53fff329a11a445d7effe564a77` | Both six-skip literal words, declared edits and complete source recipe |
| [PR3030](https://github.com/CrocSwap/integer-mult-bounds/pull/3030), Nick Petalas | `78e77d820393c6b8648b47af219e991edfcc54e6` | PR3024 T740 cap allocation, PR3018 journal, materialization and composition pattern |
| [PR2979](https://github.com/CrocSwap/integer-mult-bounds/pull/2979), Marius-Paul Dumitrean | `be191346391661f4d35fc0d1508d0a6029572576` | Joint rank-seven frames, five paired extractions, native/owner/outer chain |

Live predecessor files are pinned at main
`d8e0f83f00191df62174b641e9fff055c357f641`, priority revision 6. The selected
conditional result at that checkpoint remains 0.001672660197076918.
`SOURCES.json`, `SOURCE-PINS.json` and `VENDOR.json` identify every retained input.

The two new source words differ from PR2979 only in `restore`, its derived
inverse cleanup and the paid-profile report. Both complete 123-variable restore
matrices agree exactly with PR2979; the full forward/dual operator auditor checks
all 632 independent inputs. Each of the 408 helper widths is checked in its
original order, not merely through a histogram. The 91 restored endpoints and
their private cleanup buffers remain charged.

The literal `PR3042-EDITS.json` is the source of the circuit: its two blocks have
26 → 33 and 13 → 15 gates. Some prose in the pinned upstream description gives
different carriers and block lengths; those statements are not used as evidence
here. The retained literal gates pass exact matrix, frame and operator checks.

## Complete bill and cap

The per-call local bill is `{1:2433, 2:712, 3:232, 4:108, 5:18, 8:8}`.
The unchanged ordered widths allow the literal T740 allocation to be used with
these words. The source journal and ten-copy lift produce 2,717,280 helper roles
across 6,660 calls. The retained owner checker rechecks every role, chronological
window, physical-family collision, mask and capacity.

The complete profile is

```
{1:16376940, 2:4741920, 3:1594737, 4:719280,
 5:137085, 8:53280, 48:281903}
```

For each rank this equals `6660 * local + idle`, where
`idle = {1:173160, 3:49617, 5:17205, 48:281903}`. Its rank mass is
`65088 * 740`. Directed rational arithmetic gives the root bracket

```
[0.0017297379500642785512428, 0.0017297379500642785512429].
```

Petalas's retained cap checker recertifies all 2,551 feasible patterns at this
changed local tariff: 12 are identically tight and 2,539 strictly positive.
The literal idle counts equal 740 times the optimal fractional counts, so this
construction attains **100% of its fixed-word packing cap**. This is the
appropriate bound for this fixed-capacity inventory model, not a global ceiling
over other circuits or supplier contracts.

Physical stock is `896*740 + 408 + 8 + 91 + 2 = 663549`. The stock norm uses
1,324 bits; the conservative reserve is 1,512 within the charged 2,048-bit
payload. The completed strict replay rebuilt the precision, physical and outer
invoice: the actual prefix requirement is 1,479 bits, within 2,048. This uses
about ten times PR3042's fixed physical stock (663,549 versus 66,813); the
larger inventory is fully charged, and the exponent gain is small.

## Reproduction and evidence

Bounded registered replay (Python 3.12 standard library):

```sh
python3.12 -B scripts/research_package.py --package research/rank7-six-skip-cap-release
```

`verify.py` recomputes both literal word checks, all ordered widths, full owner
geometry, the complete moment and packing cap. It hashes the reconstructed fill
payload, order and dispatch to bind the finite witness to the actual release.
`verify_release.py` checks stored full-run receipts and their input bindings;
that check does not rerun the native/outer computation. Eight finite controls and
ten receipt/invoice controls target coefficient, width-order, journal, paid-cost,
buffer, payload, source, native and release failures.

Full replay requires POSIX process groups, the exact source commits in `FETCH.txt` to be
available locally, and Python with NumPy, SciPy, SymPy and mpmath as required by
the retained recipes:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
python3.12 -B research/rank7-six-skip-cap-release/reproduce.py \
  --repo . --work /tmp/six-skip-cap-fresh --jobs 2
```

The reproducer exports the exact upstream packages, uses PR3030's unchanged
materializer and PR3042's unchanged recipe, and changes exactly its three
complete-admission allocation arguments: fill, order and dispatch. Source
recipes, native checks and admission controls remain intact. `--dry-run` checks
exports/materialization/recipe only. `--retained DIR` explicitly reuses an
authenticated retained cache; both current providers still run fresh.
Regenerated gzip inputs are compared by their complete decompressed payload;
committed source files retain exact byte hashes.

The recorded run uses authenticated retained evidence from the prior session
and two fresh current five-stage native chains. It must not be described as a
fresh retained bootstrap. The 11 composed source stages passed in 31.3
minutes with two low-priority single-thread audit workers. Exact logs and raw
receipts are under `evidence/`; `RUN.json` records commands and reuse scope.
The public exporter/materializer/recipe dry run passed separately. A full run
with a freshly bootstrapped retained parent was not performed in this session.

## Scope

All inherited all-size/compiler, physical backing and movement, precision/tape,
caller, analytic and universal block-energy hypotheses remain. This is a
conditional finite certificate, not an unconditional integer-multiplication
theorem. Archive merge and scientific admission are distinct.

## Open next questions

The next useful task is an independent replay of this exact composition and an
audit of a named remaining admission implication. The fixed-word packing cap
is attained; a further gain in this model requires changing the word, inventory
or coverage contract. See `TASK.json` for the scoped handoff.

## Credit

Credit dcharb78/PR3042 for the six-skip word; Jeremy Kothe/PR3015 and PR2957 for
literal edit tooling and predecessor rewrites; Nick Petalas/PR3018, PR3024 and
PR3030 for packing and composition; Marius-Paul Dumitrean/PR2979 and PR2942 for
joint frames and extractions; Mason Hale/PR2917; Jeremy Diviney/PR2908 for paired
extraction; Yiyang Lu, Tekalign, Ross Richardson, Dugongue, icekylinx,
themilkman216, and the retained geometry/native/owner lineage. Original notices
are preserved. New work is Apache-2.0; substantial OpenAI Codex assistance was
used, with no independent human review claimed.
