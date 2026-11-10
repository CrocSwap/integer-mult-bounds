# Direct root certificates for the complete P104 price

The complete PR6453 price verifier can check its raw-root certificate
without repeating the root search. The candidate keeps both arithmetic
engines, strict endpoint signs, the monotonicity proof, every charged
cost, strictification, compiler checks and all 58 outer predicates.
Its entire price receipt equals the retained source receipt.

For a changed invoice, the package also supplies an exact rational
interval-Newton producer. Four contractions reproduce the source bracket
of width 10^-26. The producer and certificate verifier fail closed on
unresolved signs or invalid derivative intervals. This is the existing
crossing, not a new kappa or another digit claim.

## Evidence and reproduction

Use CPython 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/p104-interval-root-replay
python3.12 -B research/p104-interval-root-replay/benchmark.py --output /tmp/price-benchmark-new.json
```

Expected marker: `PASS_P104_INTERVAL_ROOT_REPLAY`. Both registered modes
check the exact contraction trace, ten rejection controls, and full
baseline/candidate price equality. The source comparison permits only the
replacement of the binary-search block. All later source checks remain.
[BENCHMARK.json](BENCHMARK.json) retains three alternating fresh-process
pairs through the complete price/compiler/outer module, including source
authentication. Its measurements do not include native or caller replay. Median wall
times are 39.81 seconds for the baseline and 29.62 seconds for the candidate.
The ranges overlap (24.93–44.14 and 26.36–41.09 seconds), so these samples
do not establish a reliable runtime improvement. The exact work reduction
is removal of root search from certificate verification.

## Source and credit

Base: main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8,
selected PR6030. The price and full source receipt are from PR6453 at
`b1a3e525793eca35c56324aa7ffd0b714cf606d4`. The unchanged mixed caller is
from PR6398. The two arithmetic engines, BIT receipt and outer ledger come
from the retained main-branch source archive. SOURCES.json binds every
input; input attributes preserve original line endings.
ARCHIVE-PATHS.json records the full nested archive paths for the four
arithmetic/BIT/outer inputs and checks their exact retained bytes.

[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5600#discussioncomment-19363340).
The refreshed overlap cache covers 430 open PRs and 6,399 discussion
records. No matching current-price acceleration was found. The search
cannot cover unpublished work or all historical code. The final scope
includes the complete price module, extending the initial raw-root scope.

Ali Romman with substantial OpenAI Codex assistance, Apache-2.0. Classical
interval Newton is not new. zxv, Cao Yifan, Jacob Alan Sussman and the
retained arithmetic/compiler/outer authors keep their credit. Erwan L.,
Rohan Arun, DreamingOfClouds, Cinna Davis, David Arias, Gareth Davidson and
the retained P104/caller lineage keep their construction credit. The
original source notices are retained. See [PROOF.md](PROOF.md).

## Limitations

The local/native/caller receipts are authenticated inputs. This package
does not regenerate their physical words or establish their assumptions.
No new kappa, selected-frontier change, full native replay, physical tape,
rounded multiplier or independent scientific acceptance is claimed.
Timing depends on the host. All five framework assumptions remain.

## Open next questions

The second arithmetic engine still uses large rational denominators.
Profile its contribution to the complete price replay, then prove an
outward bounded-denominator log interface before changing it. The proof,
two-engine signs and full price/compiler receipt must all survive.
