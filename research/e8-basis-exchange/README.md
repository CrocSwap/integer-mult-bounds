# Paid-aware donor-basis exchange on the E8-backed staged word

**Conditional κ = 80351298055091 / 10^17 = 8.03512980550910 × 10^-4**, an improvement of **0.046793425% over PR354**.

The construction retains PR354's installed staged Design T, twins, target squares, 240 early restorations and ten terminal sinks. It adds a newly selected signed shared-donor kernel and one freshly rebound corrected early cache. PR352's unchanged E8 complex saving is an explicit input. Pricing uses the complete resulting word and bank stock; separate gains are never added.

This upload is frozen on [PR354](https://github.com/CrocSwap/integer-mult-bounds/pull/354) at `3c59b8c8fc8521e8ba4ed87c6c4368457b13c485`. It does not incorporate later PRs or claim the current leaderboard record.

## What is new

A fixed donor basis can hide cheaper exact shared dependencies. We exchange the donor basis using 32 deterministic paid-aware orderings, reconstruct signed integer relations, charge each distinct donor once in the closure selection, and compose the chosen families on the actual installed physical word. This strengthens the freshly rebased fixed-basis witness from 173 to **208 saved rank units**. The separately corrected cache saves 15 more. The stronger basis selection is the new contribution in this round; the kernel and cache identities and integer-lifting technique are credited to prior work.

For a helper r, let T_r be its complete signed response at the targets. Let Q_r be the contribution of its prefix READs, transported through the actual later target operations. Its response after a cold cut is F_r = T_r - Q_r. At a common admissible cap, the selected integer equation is

    Q_p = sum_d alpha[p,d] F_d.

Delete p's initial READs and insert d += alpha[p,d] p at that cut. The removed target contribution and inserted contribution cancel on every scalar input. Restore the donor shears at the final full frame. Cold windows, disjoint pivots/donors, containment in first-use frames and source-bound endpoint checks are required. All selected donors still have T_d = 0: this is not an achieved warm-donor construction.

Prime-field elimination nominates candidates only. Every accepted relation is checked over all 960 integer target coordinates. The successful search records 2304 exchanged bases and 25605 exact rows. Gaussian elimination, basis exchange and weighted closure are established methods; no first-ever invention or global optimality claim is made.

## Literal witness and accounting

The final kernel has **208 pivots, 315 distinct donors and 48 role-disjoint groups**. Its 746 nonzero terms include 74 even-coefficient terms. Integer coefficients are expanded into **820 ordinary signed unit setup ADDs and 820 unit restoration ADDs**. Every ADD is charged; repeating a unit ADD at the same frame creates no extra recursive MOVE child. The rewrite removes 1536 initial READs.

Relative to the actual compact PR354 source, the kernel histogram changes by

    H1:+173, H2:+357, H3:-357, H4:+24, H5:-24.

Its weighted rank change is -208. The independent cache changes H2:+1 and H17:-1, saving another 15. Complete local paid rank mass falls from **169120 to 168897**. The value 173 above is a histogram coefficient, not a pivot count.

| Quantity | Final value |
| --- | ---: |
| Bit coarse saving c | 12564986457081 / 15625000000000000 |
| Inherited complex coarse saving b | 876248285600677 / 10^18 |
| Local helper registers | 7610 |
| Local unit ADDs | 358298 |
| Physical replicas | 300 |
| Banks per stage | 396171 |
| Literal stock / normalized stock | 3132855 / 626571 |
| Finite selector charge | 1806119562000 |
| Counted primitive coefficient bits / payload prefix bits | 57 / 94 |

Final literal word SHA-256:

    3b9488869388a9f78abca616b5d25f25253a26f030b12106b13e8698fbbcc9dc

## Reproduce

Run from the repository root with Python 3.11 or later, a GNU-compatible C++17 compiler and Boost headers:

```sh
python -m pip install -r research/e8-basis-exchange/requirements.txt
python -B research/e8-basis-exchange/verify.py /tmp/e8-basis-exchange-review
```

Use a new output directory outside the package; existing outputs are preserved. Add `--boost-include /path/to/boost/include` if Boost is not on the default path, or `--cxx /path/to/g++` to select the compiler. On Windows use a fresh Windows output path. Keep Python assertions enabled.

The bundle includes the JSON header and only the three unchanged exact pricing modules needed for replay. It contains no executables, response-array caches or machine-specific dependency paths. The manifest pins every file byte, and `.gitattributes` prevents text-conversion damage.

The replay rebuilds the exact kernel and corrected cache, requiring their pinned word hashes. It checks all **9148800 signed input-to-target entries**, every actual clean-source operand span and all **11450 five-stage binary formal columns**, frame/COPY legality, both reflected ledgers, new prime-safe frames, exact changed projector charts and actual bank tiling over 300 replicas. It rejects eight omitted setup/restoration/scatter categories.

A separate signed control deletes one adjacent pair implementing an even coefficient: the F2 scalar operator remains unchanged, but **28 integer target entries change by magnitude two**. Binary replay alone cannot certify this extension. The independent nomination audit additionally checks 199680 integer relation entries and rejects all 746 term omissions and 746 sign flips.

Finally, two exact rational moment engines include the full 10^-16 fallback; all **47 strict outer assembly constraints** pass and the adjacent κ tick is excluded. The finite-cost invoice is recomputed from the actual final word, charts and stock. Unchanged public supplier verification pipelines are not replayed.

## Scope, provenance and future reuse

This is a checked **conditional finite construction and exact assembly bound**. It retains the public compiler, common-chart, row-restoration, selector/routing, prime-supply, precision/recovery and analytic-transfer interfaces. The unchanged E8 coarse certificate is pinned explicit input, not a new verification claim. No unconditional sub-n-log-n multiplication theorem or new Lean certificate is asserted.

`SOURCE.json` identifies the public heads and source hashes. The compact input removes 480 completely untouched FULL-to-FULL helpers and relabels survivors bijectively; no gate or gain is attributed to this normalization. `data/` contains all immutable construction inputs. `code/` performs the fixed-witness replay. `receipts/` preserves the completed development admission, price and invoice. `discovery/` contains native nomination sources, exchanged-basis receipts, witness and exact relation audit; discovery is optional and is not rerun by the fixed-witness verifier.

`notes/CONSTRUCTION.md` and `discovery/SIGNED-BASIS-EXCHANGE-PROOF.md` give the sufficient mechanism, paid ledger and intermediate positive controls. `notes/WARM-SUFFIX-UNUSED.md` preserves the broader sufficient transported endpoint-repair route, its bounded unsuccessful searches and exact restrictions. It contributes no κ gain. Subsequent alternative-basis candidates were not composed or priced and are not part of the claim. Future work can change the actual donor basis, enlarge the admitted coefficient class or rebuild on a later word, but must freshly bind cuts, roles, signed equations, frames, stock and pricing.

See [PR354](https://github.com/CrocSwap/integer-mult-bounds/pull/354), [PR352](https://github.com/CrocSwap/integer-mult-bounds/pull/352), [Jacob Sussman's E8 work](https://github.com/jacobalansussman/wht-power-saving-lean), `NOTICE.md` and `LICENSE`. Prepared with OpenAI Codex assistance.
