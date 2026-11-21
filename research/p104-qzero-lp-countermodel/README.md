# Q=0 caller-window audit and exact reduced-LP obstruction

## Result and scope

At the pinned #7852 head `41beda1d6435760dc99e38bd7e65f36798aad212`, the k=72 and 73 implications are **assumptions**, not reproduced LP theorems. `CallerHP.lean:256–262` cites `CALLERCUT cc2 / KASYM cert73.log`, states `h72` and `h73` as explicit arguments, and leaves the remaining rows as an arbitrary predicate `Extra`. The pinned `research/p104-lowerbound-toolkit` export contains 489 files; a search for `cert73.log`, `CALLERCUT cc2`, `128.851`, and `128.682` found references only in `README.md` and `CallerHP.lean`. The original LP matrix, costs, dual vectors and logs have therefore **not** been reconstructed or verified. The original author attributes #7852 to DreamingOfClouds with Claude Opus 5.5 via Claude Code; this local audit is an independent construction, not their certificate.

There is a concrete obstruction to discharging those assumptions with only the pinned source's reduced event-data rows. For **every** k >= 3, the event-data frame below satisfies `CallerEv.ev_frame_bound`'s assumptions and attains HP(k). It even satisfies every pair RC2 row, a literal stage matching, exact role masks, and full row rank of both A and B. At k=72 and 73 its invoice is strictly above 128.891 and therefore above the respective quoted 128.851 and 128.682. It is **not** a counterexample to #7852: `Extra` may rule it out, and the witness provably fails the additional signed-product condition `P_k=-I`. It is not a legal word, a complete caller, a κ result, or a universal ceiling.

| k | exact-primal invoice enclosure | certified dual upper bound | status relative to 128.891 |
|---:|---:|---:|---|
| 71 | [129.298201586202, 129.298201586819] | 129.298202334142 | above; nearest unresolved k |
| 72 | [129.119942914294, 129.119942914910] | 129.119943551437 | above |
| 73 | [128.943631864855, 128.943631865472] | 128.943634080880 | above |
| 74 | [128.769229486340, 128.769229486957] | 128.769230479656 | strictly below; control |

The displayed endpoints are rounded outwards; comparisons in the checker are exact rational comparisons. The duals certify **this specified relaxation** only. The integer witness and the source's `HPDual.total_le` together show the relaxation has exact optimum HP(k); the stored duals give independently checkable rational upper approximations.

## Source mapping and conditional dependencies

All references are to [#7852 at 41beda1](https://github.com/CrocSwap/integer-mult-bounds/tree/41beda1d6435760dc99e38bd7e65f36798aad212/research/p104-lowerbound-toolkit), with byte-identical copies of the main relevant files in `source/` and hashes in `SOURCE.sha256`.

* `lean/Nov15/CallerEv.lean:28–36` defines `EvData`; `:42–46` states the pair inequality; `:201–205` states its averaged row; `:221–227` defines `Match`; `:310–317` derives a match given event data and per-stage counts. The invoice is defined at `:324–326`.
* `CallerEv.lean:398–404` assumes event data, invertible off-diagonal `Ghat` blocks, role/event counts, n+2 <= 2k, degree >=2, and >=2k singleton events. It proves the HP upper bound for that model. It does not require `P_k=-I` directly.
* `CallerAsm.lean:234–280` derives these event hypotheses for an appropriate legal, odd-target, tight Q=0 schema word with the named lambda condition; that implication uses the **full signed-product structure**. `CallerTightDeg.lean` derives degree >=2 with its stated Q=0 hypotheses. These are additional conditions, not established by the witness below.
* `CallerHP.lean:176–186` defines the weaker `Cfg.Reduced` rows, and `:256–262` quantifies `Extra` and assumes h72/h73. `HPDual.lean` gives the reduced closed-form bound. `SchemaCostB.lean:342–345` gives the event-invoice/repo identity only with its declared surrounding hypotheses; `SchemaCostC.lean:110–120` states the type-B grammar-form cost bound with its conditions. The link to a complete κ application is outside this audit.

## Explicit event-data witness

Let n=2k−2. Use two hub roles `h_0,h_1`, active at every stage. On the path of k−2 edges `{0,1},{1,2},...,{k−3,k−2}`, put two low roles `l_{e,0},l_{e,1}` for each edge, active exactly at its endpoints. Stage k−1 is isolated. At every stage and for each coordinate j, the hub row in A and B is the jth standard row. At each endpoint of edge e, the row for `l_{e,j}` in both A and B is minus that jth row; it is zero elsewhere. Thus A=B, every displayed mask is exact, the off-diagonal block `B_s^T A_t` is I (nonadjacent) or 2I (adjacent path stages), and the row ranks of A and B are both n. To see the rank, select the isolated-stage column and columns at stages 0..k−3 for each coordinate: the hub is isolated by the first column, and the remaining path incidence block is upper triangular with diagonal −1.

For every stage s, introduce two singleton events `(s,j)` and, for every edge and j, one event with support exactly e. Set

* `x_(s,j)=h_j`, `y_(s,j)=h_j − sum_(e incident s) l_(e,j)`;
* `x_(e,j)=h_j+l_(e,j)`, `y_(e,j)=l_(e,j)`.

Here symbols are coordinate basis vectors. Each x is supported on roles whose masks contain its event support; each edge x is killed by both B blocks on that edge; intersecting event pairs are biorthogonal. Per stage, match the two singleton events to hubs and each incident edge event to its corresponding low role. Thus the event assumptions, degree, exact count, mains, and pair rows all hold. `witness_event_frame.py` verifies the explicit objects and all pair rows for k=71..74; a corrupted vector is rejected.

The two hubs contribute `2(8k+1)^s`, the 2k−4 low roles contribute `(2k−4)17^s`, and the events subtract `2k 8^s + (2k−4)16^s`, with s=99/100. Multiplication by 104/k is precisely the source's `HP(k)`. This is a constructive abstract event-data witness, not just a numerical LP primal.

It cannot satisfy the signed-product condition: `CallerSGram.lean` defines each stage as `I + A_s B_s^T`. Here `A=B` and Sylvester's determinant identity gives stage determinant `(2+deg(s))^2`. The product is `324*16^(k−3)>1`, whereas `det(-I_n)=1` because n is even. Full A/B row rank and off-diagonal block invertibility therefore do **not** substitute for `P_k=-I`. Any proposed `Extra` that is meant to derive the k=72/73 bounds must exclude this witness using an additional valid source hypothesis; its concrete form remains to be obtained.

## Exact LP, directions, and check

The independent LP uses nonnegative role counts `r_d` for d=2..k and event counts `e_a` for a=1..k. Its objective is maximization of

`(104/k) * (sum_d r_d (8d+1)^(99/100) - sum_a e_a (8a)^(99/100))`.

The rows are:

1. `sum r_d = 2k−2` and `sum d r_d = sum a e_a` (tight count and incidence equality).
2. `e_1 >= 2k` (MAINS).
3. For each l=2..k, `sum d*w_l(d) r_d - sum_(a>=2) a*w_l(a) e_a >= 2k(k−1)`, where `w_l(u)=k−1` for `u>=l` and `u−1` otherwise (`CallerEv.ev_avg`).
4. For each l=2..k, `sum_(d>=l) d r_d >= sum_(a>=l) a e_a`. This follows by summing the per-stage injective `Match`: any event of size >=l is matched at each of its stages to a role with at least that many stages. It is an added necessary condition, not a claim that all such counts realize a signed frame.

The integer primal is `r_2=2k−4, r_k=2, e_1=2k, e_2=2k−4`, all other entries zero; it is realized by the event-data witness above. In the solver, every inequality is oriented `A x <= b`, and its maximization dual multiplier is nonnegative; the two equality multipliers are free. Each rationalized dual in `k71.json`–`k74.json` is checked column-by-column against an **upper** rational objective coefficient. The upper coefficient uses an upper enclosure for positive role costs and a lower enclosure for the subtracted event costs. `verify_independent.py` reconstructs rows, signs, objective and dual dot product independently of the generator. It verifies each rpow enclosure using the integer inequalities `q^100 <= base^99 * 10^1200 < (q+1)^100`, so floating point supplies only a candidate, never the verdict. Exact `Fraction` arithmetic checks every inequality and strict comparison.

The independent checker also rejects a negative inequality multiplier, an insufficient role-column multiplier, a changed dual objective, and a perturbed primal. It checks that equality to 128.891 is **not** strict. `witness_event_frame.py` checks a separate corrupted event-vector control. None of these checks replays the inaccessible original full-LP certificates or proves the legal-word bridge.

## Reproduce

Python 3 standard library suffices to check the saved certificates and construct the witness. This run used Python 3.12.3; lp_solve reports version 5.5.2.5:

```sh
python3 ./verify_independent.py
python3 ./witness_event_frame.py
cd ./source && sha256sum -c ../SOURCE.sha256
```

For rediscovery, this machine's `liblpsolve55.so` was used through ctypes with a 90-second process cap, one thread, and nice priority. The generated primal/dual suggestions are untrusted until the checks above pass:

```sh
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 timeout 90s nice -n 10 \
  python3 ./lpsolve_probe.py 71 72 73 74
python3 ./verify_independent.py
```

`lp_probe.py` also contains a SciPy alternative; on the shared loaded host SciPy import did not finish within a 90-second cap, so no SciPy result is claimed. The default verifier does not import it or require lp_solve.

Next step: obtain the exact CALLERCUT/KASYM row definitions, costs, original certificates and claimed logs from their source, verify all their signs and dot products and prove that each additional row follows from the intended signed-word hypotheses. Then retest 71 under that **same** full model. The saved reduced-model witness supplies a regression test that a purported additional row must exclude, or explain why it does not apply to, this event-data construction.

## Open next questions

Obtain cc2 and cert73.log, then derive their Extra rows from the signed product.

Clear1nsight prepared this contribution with substantial OpenAI Codex assistance. Credit DreamingOfClouds for the pinned P104 toolkit and its predecessor sources. Copied Apache-2.0 sources retain their notices.
