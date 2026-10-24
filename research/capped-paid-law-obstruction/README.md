# The true capped paid law still fails the fixed degree-23 certificate

**A scoped analytic obstruction, certified with directed rational arithmetic. No new κ or uniform rank.** For the fixed `native-concentrated-balanced` witness, replacing the uncapped first moment by the exact capped iid260 first moment cannot satisfy the highest degree-23 coefficient. A second-moment tail bound already proves this, so higher capped moments and product histograms are unnecessary.

## Fixed source and changed premise

Use canonical base `4c0a359d88f22f05189d51f48387750b801a45d4`, priority revision 7. [SOURCES.json](SOURCES.json) binds the raw paid inventory, exact witness, interval arithmetic and compiler. The independent-moment card is refined to the cap question explicitly left open by [PR5042](https://github.com/CrocSwap/integer-mult-bounds/pull/5042), head `7d09263f63f8a05537a659045dbd7e98ae7237c6`. Its [original README](predecessor/PR5042-README.md) is retained verbatim with attribution and SHA256; its results and executable code are not calculation inputs here. All calculation inputs resolve on the canonical base. The public claim is [discussion5013/comment19140792](https://github.com/CrocSwap/integer-mult-bounds/discussions/5013#discussioncomment-19140792).

The fixed parameters are `C=90037/30000000`, `t=1-C`, `v=260`, `c=20`, `b=21`, `u=171/1000`, `h=3900`, candidate `p=23`, `beta=127/125`, and paid excess bound `epsilon=1/100000`. The original source uses degree24. In particular, beta remains the source's rational lower bound on normalized productive log rank; this result does not optimize beta or claim failure for a different certificate. The selected conditional `κ=0.00302015` is provenance, not this benchmark's `κ=0.00300120` and not a new result.

## Stop-loss lemma and true capped mean

For a real random variable `X` of finite second moment, mean `mu<1` and variance `s²`,

```text
a = 1-mu > 0
(x-1)+ <= (x-mu)²/(4a)
E[(X-1)+] <= s²/(4(1-mu)).
```

For `x<=1` the left side is zero. For `x>1`, put `z=x-1>0`; the inequality is `4az <= (z+a)²`, equivalent to `(z-a)²>=0`. Taking expectations proves the lemma. It bounds the tail expectation, not merely the tail probability.

For the source paid inventory, define `P_t=sum_r P_r*r^t`, `Pr(Y=ln(r)/ln(c))=P_r*r^t/P_t`, and `X_raw=(Y_1+...+Y_260)/260` for independent copies. Compute only `mu=E[Y]` and `b2=E[Y²]`; independence gives `Var(X_raw)=(b2-mu²)/260`. The true capped mean satisfies the exact identity

```text
m1 = E[min(X_raw,1)] = mu - E[(X_raw-1)+].
```

The pinned outward rational logarithm/exponential engine encloses the weights and both moments. If `mu in [l,u]` and `Var(X_raw)<=V`, then `u<1` and the stop-loss correction is at most `V/(4*(1-u))`; hence `m1>=l-V/(4*(1-u))`. All reported decimal endpoints are rounded outwards; [RESULT.json](RESULT.json) retains exact rational endpoints.

| Quantity | Certified enclosure or bound |
|---|---|
| Raw mean `mu` | `[0.860093849703915655837465865147, 0.860093849703915655837465865148]` |
| iid260 variance | `[0.001201338820469136078612316931, 0.001201338820469136078612316932]` |
| Cap correction | `0 <= E[(X_raw-1)+] < 0.002146686936075959677703581106` |
| True capped mean | `m1 > 0.857947162767839696159762284042` |
| Required cap correction | `> 0.003093849703915655837465865147` |
| Optimistic highest-coefficient ratio | `> 0.020466198952243698400567704338` |
| Source complement capacity | `< 0.019675906372710418424472814350` |

## Necessary coefficient and paid normalization

In the source Bell coefficient formula, the top index `j=p` leaves only `i=p`, `Shift(0)=1`, `Bell(p,p)=mu_1^p`, and `S(p,p)=1`. Consequently `C_p/D_p=(mu_1/beta)^p`, independently of every higher moment, shift and ambient constant. The unchanged capacity is `eta=t*(153^260)^(t-1)`.

Avoid root approximation by the exact rational barrier `q=857/1000`. Directed arithmetic proves `(q/beta)^23>eta`, so satisfying the highest coefficient requires `mu_1<q`. Even using the exact capped mean with **zero** paid excess would require `m1<q`, equivalently a cap correction strictly greater than `mu-q`. Its certified lower bound is more than 0.003093849703915, but the stop-loss upper bound is below 0.002146686936076. This is a strict obstruction, not an inconclusive interval comparison.

The retained capped-reference theorem bounds the completed paid mean by `(m1+x)/(1+x)`, where `x=(Q_t-P_t^260)/P_t^260>=0` includes original splitting excess **plus full completion paid mass**. Its proved upper bound is

```text
x <= (original_splitting_tax + 2*delta^260)/alpha^260
  < 0.000001447491518642763738467578 < epsilon.
```

For `m1<=1`, the majorant `(m1+epsilon)/(1+epsilon)` is at least `m1`; therefore no nonnegative refinement of the excess bound can repair this capped-reference certificate. With the fixed epsilon its first-moment majorant is enclosed by `[0.857948583282006876091001374028, 0.860095248751428141556050304645]` and still fails the necessary coefficient.

**Scope boundary:** the lower bound here is on the true capped **raw reference** and therefore on the numerical majorant this certificate would use. It is not a lower bound on the actual completed paid law: splitting can reduce actual log ranks, and the source gives only an upper majorant. Direct analysis of that actual law, a stronger beta, another exit argument, changed witness or changed native construction remains outside this result. Failure of this sufficient certificate is not impossibility of the compiler or multiplication theorem.

## Replay and controls

```sh
python3.12 -I -B research/capped-paid-law-obstruction/verify.py
python3.12 -I -O -B research/capped-paid-law-obstruction/verify.py
python3.12 -B scripts/research_package.py --package research/capped-paid-law-obstruction
```

Local validation on 3.12.14 (Darwin arm64) passed: direct normal generation 0.36s, direct optimized replay 0.74s, metadata/pins 0.38s, and registered normal plus optimized replay 0.74s. Timings include the serial wrapper and are observations, not runtime bounds. The verifier authenticates exact source bytes before executing pinned source modules, avoiding preexisting bytecode caches. All guards use explicit exceptions and survive `-O`. It retains source net-tax, shift, ambient, minimum-rank, mean, support and full paid-excess checks; the original degree24 chord certificate passes as a positive control. Only the necessary degree23 coefficient is tested. No degree23 higher-moment list, base-range/final-rank proposal, full native/outer replay or selected-frontier change is made.

An independent exact two-point law `Pr(Y=0)=3/4`, `Pr(Y=3)=1/4`, averaged over two copies, has mean `3/4`, variance `27/32`, capped mean `7/16`, and cap correction `5/16`. It checks the stop-loss bound and cap-after-average identity. Mutants cap before averaging, subtract tail probability instead of tail expectation, omit full completion paid mass, or invert normalization; each differs from the independently enumerated answer. A completion of relative mass 1/2 placed at normalized rank 1 gives completed mean 5/8 exactly. Paid-versus-target normalization is rejected by disjoint source mass intervals. Small exact capped moment lists and the source p24 coefficient bind the highest-coefficient identity; directed rounding has an off-grid rational control.

Test-authoring rationale: the protected contracts are cap-after-average, tail expectation, and full-paid normalization; the named mutants are the regressions. PR5042 did not compute the true cap or certify this tail bound, so these are the primary controls for the new implication. They call the package's actual stop-loss/completion functions and the unchanged source coefficient function without production test seams.

## Open next questions

A changed exit certificate or a direct treatment of the actual completed law could escape this scoped obstruction. First specify the changed premise and its complete paid bill; further raw/capped high-moment precision alone cannot alter the fixed top-coefficient decision. [TASK.json](TASK.json) records that handoff and its scope boundary. No automatic parameter search or downstream construction is justified by this negative result.

## Credit

Retain zxv's net-tax compiler, capped-reference theorem, logarithmic certificate and directed interval engine; Jacob Alan Sussman's integer compiler; PR4411/4414/4416/4433 product, completion and splitting lineage; Cinna Davis's native contributions and the retained native, stock, ownership, precision, analytic and recovery contributors. JoyboyBrian's PR5042 identifies the uncapped first-moment obstruction and explicitly leaves the true cap open. This package adds the analytic true-cap obstruction for that fixed witness. Prepared for JoyboyBrian with substantial OpenAI Codex assistance. New work and retained PR5042 material are Apache-2.0. No formal-kernel or independent human acceptance is asserted.
