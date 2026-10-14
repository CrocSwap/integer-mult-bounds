# Parity defect in the PR1479/PR1485 finer-constant Mercator engine

**Adversarial audit / exact counterexample; no new bound and no change to any
claimed κ.**

## Result

PR [#1479](https://github.com/CrocSwap/integer-mult-bounds/pull/1479)
(`0a211a4608d2c3d295f8bb94b12ca446714186ab`) adds `code/fine_mercator.py`, a
“finer-constant copy” of the retained Mercator moment engine, and PR
[#1485](https://github.com/CrocSwap/integer-mult-bounds/pull/1485)
(`da38a09c5b2c2418d405773ac398378ab92ccf54`) carries the byte-identical file
(Git blob `29699092d4e66677d50d400a89e4763e476ef7e1`). Both use it to certify
their 10⁻¹²⁰ complex endpoint brackets.

The retained engine (`research/complex-allcold/engines/moment.py`, and every
other Mercator engine on main) sums `n = 1..224`: an **even** alternating partial
sum, which lies below `log(1+z)`, so `(s, s + z^225/225)` is a valid enclosure.
The fine copy changes the loop to `range(1, LOGN)` with `LOGN = 800`, so it sums
`n = 1..799`: an **odd** partial sum, which lies *above* `log(1+z)`. It still
returns `(s, s + z^800/800)`, i.e. an upper bound as the lower end. The true
value is in `[s − z^800/800, s]`.

Exact consequences, checked with `fractions.Fraction` against a separately
written `2·atanh` oracle whose enclosures have width below `2^-1500`:

1. The inner sum at `z = 1/2` (the shared `log(3/2)` constant) exceeds
   `log(3/2)` by about `0.00083·2^-800` before rounding.
2. The exported `logarithm(x)` returns a **false lower bound** after its
   `2^-800` outward floor for `x = 43, 189, 352` (the first three integers ≥ 2).
3. For every input the pinned T74 check actually uses — `log(73/r)` for
   `0 < r < 73` and the surcharge `log(73)` — the floor happens to absorb the
   error: all 73 lower ends are valid, with least margin about `0.029·2^-800`.
   The companion `fine_moment.py` (atanh) engine and the retained engine are
   valid on all these inputs and on the counterexamples.
4. Setting `LOGN = 801` (sum through the even term `n = 800`, keep the
   next-term tail) gives a valid enclosure on every input above.

### Downstream effect

Both PRs' `check_moment` accepts only when *both* engines' upper ends are below
one, and rejects only when *both* lower ends exceed one
(`assert (u<1 and uu<1) if accept else (l>1 and ll>1)`, `code/assemble.py`
line 198 in each). Upper ends from `fine_mercator` remain valid, and the
`fine_moment` lower ends are sound, so the reported accept/reject decisions are
still certified by at least one sound engine. Item 3 additionally shows that the
fine Mercator lower ends on the actual inputs are valid. **No claimed κ or
bracket is refuted.** What fails is the stated property of the vendored engine:
it is not an outward enclosure in general, so the “two engines both certify the
reject” redundancy rests on luck at these inputs, and further reuse of the file
(it has already been copied once) could certify a false rejection. Recommended
repair: `LOGN = 801`, or return `(s − t/LOGN, s)` for even `LOGN`.

## Reproduce

From the repository root (about 40 s, standard library only):

```sh
python3 -B research/fine-mercator-parity-audit/verify.py
python3 -B research/fine-mercator-parity-audit/verify.py --search   # also rediscovers 43, 189, 352
python3 scripts/research_package.py --package research/fine-mercator-parity-audit --check-only
python3.12 scripts/research_package.py --package research/fine-mercator-parity-audit
```

The verifier checks SHA256 pins of the two vendored files (exact bytes from
both PR heads) and of the retained main engine, the inner-sum inequality, the
three counterexamples, all 73 pinned inputs for all three engines, the
`LOGN = 801` repair, and an oracle control that must detect a deliberately
raised lower end. Any mismatch exits nonzero.

## Not checked

- No moment-level false certificate is constructed: the logarithm error is
  about `2^-809` and is multiplied by the saving `a < 1/10` before the
  exponential and the outer floor; no attempt was made to find a profile where
  it changes a reported moment bound.
- Neither PR's full finite admission, native providers or outer witness was
  replayed. This audits one arithmetic file only.
- Other numerical files in those packages were not audited.

## Open next questions

- **Do the 10⁻¹²⁰ endpoint certificates still hold with the repaired engine?**
  It matters because the PR claims two-engine certification. First step: rerun
  each PR's `check_moment` for the native and conservative complex sides with
  `LOGN = 801`. Blocked by: nothing beyond the PR packages' own replay time; the
  PR authors are best placed to do it.
- **Should certified-arithmetic copies carry a parity/tail self-test?** A
  one-line assertion (`LOGN` odd, or a check against an independent oracle at
  `x = 3/2`) would have caught this. First step: add it to new engine copies.
  Blocked by: frozen packages must not be retrofitted; applies to new work only.

## Credit

Audited code: finer-constant engines by Jeremy Kothe (jeremykothe2, PR1479)
with oh-my-pi assistance, reused in PR1485 by Rohan Arun (rohanarun); the
retained Mercator engine and its range-reduction design come from the
complex-allcold lineage on main. The vendored files are unchanged copies under
the repository's Apache-2.0 license. Audit by Philippe Van Velzen with
substantial Claude (Anthropic) assistance. New work is Apache-2.0.
