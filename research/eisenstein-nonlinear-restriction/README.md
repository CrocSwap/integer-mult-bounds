# A coordinate-restriction obstruction for nonlinear Eisenstein messages

This contribution is produced by Nick Petalas. New work is Apache-2.0.

For the fixed-support nonlinear Eisenstein message model, let N be the
total independent input demand. If fixing h individual input coordinates
to specified constants makes every transmitted bit affine, then the
original additive pairing charge satisfies **C >= N-h**. Consequently

    C >= N-h_* >= N-tau(E),

where h_* is the minimum fixing over all coordinate faces and tau(E) is
the minimum hitting set of the nonlinear monomial supports across every
output bit's algebraic normal form. For zero-valued fixings the minimum
is exactly tau(E). Nonzero faces can give a strictly stronger bound.

This is a scoped proof with finite corroboration. The new step is the
model-preserving restriction of a genuinely nonlinear message map to
Jose Manuel's credited block-linear theorem. It does not settle the
unrestricted nonlinear optimum or give a new kappa.

## Result and relevance

[PROOF.md](PROOF.md) gives the all-width argument and the exact monomial
criterion. A coordinate restriction leaves the unfixed bits independent
within and across ports. The old receivers still recover them. Known
affine constants can be subtracted, so the retained linear floor applies.
Removing inactive supports can only decrease their pairing ranks.

A putative saving d below N therefore requires h_*>=d and tau(E)>=d.
For equal b-bit demands, a proposed charge at most 31b requires at least
9b fixed bits to linearize the message map, under either parameter.
These are necessary conditions, with no assertion that such a cheaper
nonlinear code exists. The inherited unrestricted nonlinear floor 22b
combines with this result as max(22b,40b-h_*).

The new exact fixture uses ports 0,28,29,39, an orthogonal four-frame in
the pinned geometry. Its fourth message is x3+x0*x1*x2, and the first
three messages are their owners' input bits. The fourth receiver has
the other three frame inputs as permitted side information. Thirty-six
direct messages complete the code. Each of its forty message prices is
one, and h_*=tau=1. The new lower bound is 39; the exhibited code costs
40. This is no claim of an attaining cost-39 code.

The strict-face example is x0*x1+x0*x2+x1*x2+x0*x1*x2. Its zero-fixing
minimum is two, while fixing x2=1 leaves x0+x1, so h_*=1.

## Reproduce

From the repository root, using Python 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/eisenstein-nonlinear-restriction
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/eisenstein-nonlinear-restriction/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/eisenstein-nonlinear-restriction/verify.py
```

Another Python 3.12 executable can replace the local interpreter path.
Each registered command has a 120-second limit. Expected final status:

```text
PASS_EISENSTEIN_NONLINEAR_RESTRICTION {"faces":18086,"maps":366,"new_fixture_lower_bound":39,"rejections":9,"semantic_controls":3}
```

The checker enumerates every Boolean function through three variables
and 88 deterministic multibit maps in four and five variables, totaling
366 maps, 18,086 coordinate faces and 164,114 point/output substitution
checks. An independent truth-value affine oracle corroborates symbolic
substitution, including cancellations on nonzero faces. Exact minimizers
are compared with exhaustive face and zero-face scans.

The code fixture checks sixteen frame inputs, 64 receiver observations,
and 72 separate direct-bit component cases, together with all forty
actual rational pairing prices. Its product argument is written in the
proof; the checker does not enumerate 2^40 full inputs. Nine rejected
inputs/contracts and three semantic controls cover malformed ANFs,
search bounds, missing side information, retained nonlinear terms,
cancellation and a deleted cubic term. Explicit checks remain enabled
with Python optimization.

Default replay writes no files. To generate a receipt bound to the new
proof/code and declared source hashes, add `--output NEW_PATH` to a direct
command. Use a scratch path outside the checkout. Existing outputs are
never replaced. No receipt is handwritten or committed.

`restrictions.py` accepts at most forty variables, forty outputs and 256
monomials per output. The exact zero-cut search accepts at most twelve
variables, and the exact arbitrary-face search at most eight. The census
uses at most five. These executable limits do not limit the written proof.
The code has no recursive path; every search is finite. Managed Python
allocations and the fixed rejection-control callbacks are documented
Power of Ten deviations from static allocation and direct-only calls.
The input and iteration caps bound their lifetimes and target sets.
Warning-strict ordinary/optimized replay supplies the available runtime
diagnostics; no new static-analysis dependency is introduced.

## Scope, provenance and credit

[SOURCES.json](SOURCES.json) pins base
624de9dc66858af0945e5f8a0942488d62280d43, priority revision 7. The original
card was `complex-rank-shape-decoder`. [TASK.json](TASK.json) records the
change to a nonlinear interface obstruction, outside the already closed
linear search. The selected metadata orientation passed. The card's
predecessor scientific replay was skipped because this assignment asks
for original work and excludes predecessor re-verification.

Credit Michael Fischler / shiftybitshiftr [#814](https://github.com/CrocSwap/integer-mult-bounds/pull/814)
for the nonlinear fixed-support model and its 22b lower bound, Jose Manuel /
jmbarrancoml [#2017](https://github.com/CrocSwap/integer-mult-bounds/pull/2017)
for good reduction and the block-linear total-demand floor, and Jonathan
Lam [#798](https://github.com/CrocSwap/integer-mult-bounds/pull/798) following
Joel Pulikkan / GamingPuzzled for the geometry and pairing-cost model.
Maximooch's historical #1794 format screen motivates the example target
31b, without supplying a current selected-frontier comparison here.
ywz65's [#2607](https://github.com/CrocSwap/integer-mult-bounds/pull/2607)
is the distinct adaptive public affine-query extension. No predecessor
verifier is imported, executed or independently certified here. Geometry
data is read unchanged to price only the new fixture.

The overlap check covered live PR lists, this account's past-day work,
recent handoffs, main-package searches and the cached task search.
The latter reports 410 open PR records at 23:02:36 UTC and 3,919 Discussion
records at 23:03:21 UTC on October 22. The sparse local-note search was
incomplete, so a separate Git-tree source search was used. Closed-PR
metadata in the cache was older; live merged searches supplemented it.
These are bounded searches, not proof of novelty.

The proof requires exact deterministic decoding, independent product
inputs, fixed supports/widths, orthogonal side information and additive
per-bit prices. Coupled cross-port affine restrictions, correlated inputs,
errors, adaptive/private routing and shared physical tariffs are excluded.
No physical supplier, compiler, hosting, precision or multiplication-theorem
obligation is discharged. Independent human and formal proof-kernel review
are unclaimed. The selected frontier is unchanged.

## Open next questions

- Can an exact genuinely nonlinear code have C<N under the unchanged
  supports and prices? Start with a small complete code and enumerate
  receiver observations; compute an affine-face witness before enlarging
  it. No attaining nonlinear saving is supplied here.
- Can within-port affine changes of input coordinates reveal a larger
  product restriction? Start with one nonlinear block map, preserving
  independence across ports. A proved invariant beyond coordinate faces
  and its bounded search remain open.
