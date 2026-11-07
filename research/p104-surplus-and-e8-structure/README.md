# P104 invoice surplus S = 48k - ports and the E8 structure of the 104 ports (no κ)

**No new κ.** This package re-derives, from the literal words and callers of the current P104 chain, (1) a
three-term accounting of the complete invoice surplus `S = Σ(T−P)·r`, (2) the E8 structure of the 104 ports,
(3) the exact make-up of the 56 units of private-descent mass in the native word, and (4) a bound for mixed
port sets under the #968 copy-cost law. Every number is replayed by `verify.py` (Python 3.12, standard library).

## Results

1. **Surplus accounting** (`PROOF.md` §1–3). For a native word and a caller with `k` native calls on `p = 104` ports:
   * *Native side (proved, any legal word).* Public registers only climb and private (owned) registers only
     descend, so the paid mass of one call is `16p + Σ helper ranks + O`, with `O` the total private-descent drop.
     The native margin is `−(16p + O)` whatever the helper structure.
   * *Caller side (checked on literal callers).* Every native stage is covered by exactly `2p` more target
     incidences than idle incidences, and the outer margin is `p(17k − 1)`: 31720 = 104·305 for #6726 (k = 18),
     33488 = 104·322 for #6348 (k = 19); `305 = 16·18 + 32 − 15`, i.e. 32 odd-rank targets minus 15 thin queries.
   * Hence `S = (k−1)p − kO = k(p − O) − p`. With `O = 56` the local balance is `p − O = 48` and `S = 48k − 104`:
     760 for #6702, #6805 and #6824 on the #6726 caller (k = 18), 808 for the #6348 caller on the #6349 native
     word (k = 19). `S` depends on the native word only through `O`; any edit conserving total rank (the #6805 retime
     and split, the #6824 lift) leaves `S` unchanged. Exactly: `S = κ·D̄`, so `S/D(0) < κ < S/D(κ)` (each bound within 0.7 % of κ).
2. **E8 structure** (§5–6). `Q(e) = wt(e)/2` on `1^⊥ ⊂ F2^9` is an `O+(8,2)` form with 120 nonsingular points, the
   odd vectors of weight 3 or 7. The 104 ports are 70 + 34 of them; the 16 missing lines are two disjoint
   orthoframes (frame pairs fall into 896/336/28 by incidence rows, only the 896 class admits the #968 decoders).
   The port stabiliser has order 384 with orbits 48, 32, 24. In the E8 model `u = e_T − 1/3` (weight 3),
   `e_i − e_j` (weight 7), a pair is odd exactly when the roots are orthogonal. The public block `P` of the word
   vanishes on all 5824 odd pairs; `O = I − P` equals the sign-gauged E8 Gram matrix except in exactly 40 entries,
   all in the rows of ports 69 and 276, and has rank 10 = 8 + 2.
3. **Private-descent mass** (§7). On the literal word the 24 descent hops form exactly 8 components, each a descent
   `8 → … → 1` of mass 7, so `56 = 8·7`. For all 43435 seven-dimensional subspaces `V ⊂ F2^9` the ports outside `V`
   span `R^8`; consequently any realisation of a rank-8 Gram operator by 8 disjoint single-stage chains costs at least 56.
   This is a conditional bound (hypotheses in §7.3); the literal word has rank-10 `O` and attains 56.
4. **Mixed ports** (§4). Under an explicit bookkeeping hypothesis and the #968 floor `max(|A|−48, 56)`,
   `S ≤ 48k − |∪A_j| ≤ 48k − 104`, with equality only for the uniform 104-port set.

## Relation to earlier work (read-only overlap check)

* **#4697 (Matarener, merged)** derived `surplus = (p+2)(H − C + Σ(2b+1)) − P`, i.e. `48·|thick| − ports`, for the
  kernel-era controllers. The shape `S = 48k − ports` is theirs. New here: the split `48 = p − O` with `O` the
  private-descent mass of the native word, the check that the outer law `p(17k−1)` survives the #6348 tree and the
  #6726 fragmentation, the stage balance, and the invariance statement.
* **#968 (themilkman216, merged)** states the E8 root-line model with F2^9 labels (`S9 = ⟨r_i,r_j⟩ + 1 mod 2`, so odd
  pairs are exactly orthogonal roots), `P104 = P120 − F0 − F1`, the census of 1260 frames (896 admit decoders, 364 = 336 + 28
  do not), and the floor `cst ≥ max(72 − p, 56)`. Cited, not claimed. New here: the quadratic-form/O+(8,2) description
  with explicit weights, the identification of the literal ports, the stabiliser and orbits, the O versus Gram comparison,
  and the hop and subspace certificates.
* #6717, #6398 (shortest query contracts) fix the stage counts of the callers; not re-derived.
* No open or merged pull request found by repository search states the surplus decomposition `48 = p − O`, the stabiliser,
  or the O-versus-Gram comparison. Searches are textual and may miss prose.

## Exact checks

| Check | Result |
|---|---|
| native replay (legality, exact endpoint) of the #6702 word and the #6349 word | paid mass 5924 = 1664 + 4204 + 56 and 5946 = 1664 + 4226 + 56 |
| #6805 and #6824 histograms (retained constants) against the replayed #6702 word and the retime witness | deltas `{4:+1,5:+1,9:−1}`, `{1:+1,5:+1,6:−1}`; #6824 vs #6805 rank conserving |
| callers #6726 (final and unretired), #6348 | stage balance 208 = 2p on every stage; outer margin 104(17k−1) |
| complete invoices | S = 760, 760, 760, 808; κ(#6805) = 0.00330814518914…, κ(#6824) = 0.00330823456614… |
| mixed bound | uniform maximiser 104 at k = 18, 19; 20000 random mixtures respect the cap |
| E8 | 120 nonsingular points; ports ⊂ them; 2025 frames, 759 in the ports; two disjoint missing frames; classes 896/336/28; stabiliser 384; orbits 48/32/24 |
| blocks | P = 0 on 5824 odd pairs; 40 differing entries, rows 69 and 276; rank 8 versus 10 |
| private descents | 24 hops, 47 lifetimes, 8 components of mass 7; 43435 subspaces rank 8; 16 hyperplane exceptions = the 16 missing lines |
| controls | missing idle, off-by-one paid mass, illegal public descent, non-nonsingular port, swapped port, half the ports, dropped hop edge, cost below the floor, live set below 96 |

## Reproduce

```sh
python3 -B scripts/research_package.py --package research/p104-surplus-and-e8-structure
```

or directly (about 25 s): `python3 -B research/p104-surplus-and-e8-structure/verify.py`.
Expected markers: `PASS_P104_SURPLUS_AND_E8_STRUCTURE` and `PASS_REGISTERED_RESEARCH_PACKAGE`.
`retained/` holds unmodified copies of the pull-request inputs with pins in `retained/SOURCE-PINS.json`.

## Not established

* The outer law `p(17k−1)` and the stage balance are checked on three literal callers, not proved for every caller.
* The 56-unit lower bound needs the hypotheses of §7.3; the literal word does not satisfy them (rank 10).
* The mixed-port bound rests on the stated bookkeeping hypothesis; no mixed word exists.

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. Apache-2.0.

## Open next questions

* Does the outer law `p(17k − 1)` hold for the final #6716 caller and every later root?
* Can a legal word realise exactly the Gram operator (no defect rows) at private-descent mass 56?
* Is the hypothesis "disjoint single-stage chains" removable from the 56-unit lower bound?
