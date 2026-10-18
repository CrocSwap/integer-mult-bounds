# Exact identities and cost model

Let `q_0,...,q_111` be the pinned selected labels in `F2^9`. Each has odd weight, so `q_i dot q_i=1`. The certificate partitions their indices into 22 groups of five and one group of two. Every two different labels in a group have dot product zero. Thus each group matrix `A_g` has `A_g^T A_g=I`.

For each group, the verifier stores a binary matrix `M_g`. Direct bit arithmetic checks

```text
sum_g A_g M_g A_g^T = I_9.
```

It then writes each `M_g` as a sum of rank-one matrices `u v^T`. For each such term, let `l=sum_{r:u_r=1} q_{g_r}` and `r=sum_{s:v_s=1} q_{g_s}`. Its action on port `(i,j)` is `(q_i dot l)(q_j dot r)`. Summing terms gives

```text
sum_g sum_(u,v) (q_i dot l)(q_j dot r)
  = q_i^T (sum_g A_g M_g A_g^T) q_j
  = q_i dot q_j.
```

The full 112-by-112 port identity is therefore exact, including every forbidden zero entry. The actual source support is `{i:q_i dot l=1}` and target support is `{j:q_j dot r=1}`. The charged rank is the F2 rank of their selected label-pairing matrix. The certificate histogram is `{7:10,8:6}`, giving `10*7+6*8=118`.

For the local address correction, `X_q` translates an address basis state `e_s` to `e_(s xor q)`, and

```text
C_q = ((1+i)I + (1-i)X_q)/2.
```

Expansion gives `C_q^2=X_q`. Every `X_q` is a translation, so the `C_q` commute. For every block `g`,

```text
C_g^2 = product_(q in g) X_q = X_(xor_(q in g) q).
```

The verifier checks this equality exactly with Gaussian-integer numerators and common denominator `2^(2|g|)` on every one of the 512 address basis states for all 23 blocks. The decoder and correction identities accept arbitrary dirty source and target values; the finite endpoint controls check all 112 source basis vectors against three dirty-target patterns, plus zero-source preservation.

## Conditional moment calculation

The pinned selected word has profile `{1:2412,2:418,3:432,4:142,5:82,8:8}`. Replacing the eight rank-8 centre children by the 16 decoder terms yields `{1:2412,2:418,3:432,4:142,5:82,7:10,8:6}`. Its paid mass is 5,640 and its centre charge is 118.

The exact pinned `ceiling.py` relaxation is evaluated at width `m=73`, `families=896`, `stages=9`, `unpaid=5`, and `a=1/99`. It uses the halving cap `R=51` and assigns all residual mass to rank 51, which is favorable to the proposed profile. The resulting interval is strictly below one at the target. The ceiling bracket and exact target interval are stored in `CANDIDATE.json`.

To bound aggregate implementation overhead, the verifier adds each extra unit as a rank-1 child and increases the centre charge by the same amount. This conservative rank shape passes through total charge 275 and fails at 276. It is a price allowance for all unmodeled costs, not evidence that those operations can be supplied for that price. The exact 23 block translations can be provisionally charged one unit each, leaving 134 units; native routing, chart changes, hosting, restoration and precision still need a complete implementation and price.
