# Verdict and literal all-depth binding

**No structural proof/code gap found under the fixed known nonadaptive-pair and fresh fair-bit contract.** The literal `make/census/run` controller implements the source's exact independent product law, including phase wrapping, and achieves every depth's fair-bit stopping lower bound. A structural derivation also explains the source's existing 312-state inventory and coarse mean inequalities without an executable catalogue. The sampler, counts and optimum remain zxv/PR6072's results; this is external written review evidence.

Read the full separately authored [derivation](reviews/DERIVATION.md) and [code trace](reviews/CODE.md), sealed before cross-review. They are source-aware AI reviews after original-source exposure, not blind, human or kernel acceptance. No retained source was imported or executed. The [coordinator small-pair bound](reviews/SMALL-BOUND.md) is separately attributed hand arithmetic, not a third blind derivation.

## Domain and the prefix invariant

Fix `a,b` in `1..12` before drawing any bits. For outputs `00,01,10,11`, let

`w=((13-a)(13-b),(13-a)b,a(13-b),ab)`, `D=169`.

The weights are positive units modulo13, sum to169 and give the product of Bernoulli masses `a/13,b/13`. The stream entering this call is independent and unbiased, and initial control is deterministic. Free initial entropy, adaptively replacing the second probability and correlated incoming bits are different contracts.

At completed depth `k>=0`, write `f_i(k)=floor(2^k*w_i/D)`, `r_i(k)=2^k*w_i mod D` and `n_k=2^k-sum_i f_i(k)=sum_i r_i(k)/D`. Every remainder lies in `1..168`, so `1<=n_k<=3` and `n_0=1`. The next digits are `d_i(k+1)=floor(2*r_i(k)/D)`, each zero or one, and

`n_(k+1)=2*n_k-sum_i d_i(k+1)`.

Inductively, the completed output-i cylinders number `f_i(k)`, and the unfinished prefixes are bijectively indexed by `j=0..n_k-1`. Completed cylinders from an earlier leaf are counted with all length-k suffixes. A new bit gives child rank `2*j+bit`; allocating digits in output order consumes the first ranks, and subtracting those digits reindexes all remaining ranks from zero. The source's first-negative subtraction implements this exact allocation. It never overfills a level because the stated recurrence leaves `n_(k+1)>=1` children.

Consequently `Pr(T>k)=n_k/2^k`, and completed output probabilities converge to `w_i/D`. This proves the **full joint law**, rather than only correct marginals. Survival tends to zero, so termination is almost sure. It remains positive at every finite depth, so the finite controller has unbounded stopping.

## Period, root return and the existing resource ledger

The order of2 modulo13 is12: `2^6=-1` and `2^4=3` modulo13 exclude every proper divisor of12. Since `2^12=1+3*13 mod169`, binomial expansion gives `(2^12)^t=1+3*13*t mod169`; thus its exact lifted order is156. It follows that `2^78=-1 mod169`: this is a nontrivial square root of1, and an odd prime square has only the roots±1.

For every parameter pair and phase,

`r_i(k+78)=169-r_i(k)`, hence `n_(k+78)=4-n_k`.

Pairing78 phase pairs proves `sum_(k=0..155)n_k=312`. This is a uniform explanation of the original **selected phase/node controller's** state count, not a new count or a minimal-state theorem. Other representations and the credited shared-bank successor have different inventories.

States are enumerated in phase/node order, so root `(0,0)` is identifier0. After phase155, a surviving child has phase0 and node0 because `n_156=n_0=1`. That is a return to the same control state to continue sampling, **not a stopping condition**. The all-depth prefix invariant remains valid through every wrap. Internal identifiers0..311 and output identifiers312..315 fit nine bits; 624 target entries therefore admit a5616-bit/702-byte logical encoding. This is a payload bound, not measured Python memory, a minimum-storage result or a complete physical table/selector/tape bill.

## Optimal expected draws and bounds checked by hand

The nonnegative tail-sum identity and periodicity give

`E[T]=sum_(k>=0)n_k/2^k = (sum_(k=0..155)n_k/2^k)/(1-2^-156)`.

The root term is included. For any exact fair-bit procedure in the same no-free-initial-entropy model, completed mass for output i at depth k is an integer multiple of `2^-k` and cannot exceed `w_i/D`. It therefore completes at most `f_i(k)` such cylinders. Its survival is at least `n_k/2^k` at every depth; summing proves expected-bit optimality even against nonperiodic or infinite-state procedures. The argument does not optimize physical transitions or controller storage.

Since `n_k>=1`, the expectation is at least2; `n_78=3` makes it strictly greater. Since `n_0=1`, `n_1<=2` and every later count is at most3, the expectation is at most7/2; `n_156=1` makes that inequality strict. This supports the source's existing general bounds analytically, without recataloguing144 configurations.

For `(1,1)` the hand-derived unfinished counts at depths0..5 are `(1,1,1,2,1,1)`. Their tail-sum contribution is67/32; bounding every count from depth6 onward by3 adds at most3/32. Thus `E[T]<=35/16<9/4`, a convenient nonsharp hand proof of the source's existing small-pair inequality. The original large exact fraction, finite catalogue extrema and literal tape receipts were not recomputed or executed. This bound does not claim a new exact mean or additional physical saving.

Separate standalone non-dyadic Bernoulli calls, without a shared entropy reservoir, each leave an unfinished prefix at every depth and require at least two expected draws. Their sum is at least four. The joint decision tree changes that call boundary while preserving independence of its two outputs; it does not contradict the standalone or worst-case theorem.

## Exact code association and trusted API boundary

Line numbers refer to the inert original [verify.py](inputs/verify.py), blob `eda448fbda7b6a78f340086fcaac6e7556bf1383`.

| Lines | Audited association |
| --- | --- |
| 18–28 | Positive genuine integer parameters, product weights, exact phase remainders and unfinished counts; uniform inventory proof justifies the hardcoded312. |
| 29–41 | Phase/node identifiers, next-bit digits, first-negative output allocation and surviving child with `(phase+1)%156`; phase k stores values before bit k+1. |
| 42 | Exact Fraction tail formula with n0 and the geometric denominator. |
| 46–59 | `done` doubles old terminal cylinders before adding new leaves; active states represent only unfinished prefixes. The finite census assertions match the all-depth invariant, but were not run. |
| 62–68 | Start at root0; stop only at a target>=312, returning label0..3 and consumed depth. Root revisits continue. An exhausted finite binary sequence returns unresolved, not a forced sampled output. |
| 77–118 | Source hash checks, order scan,144-case certificate, literal tapes and negative controls remain original evidence; this audit does not execute or newly certify that suite. |

The lower-level `run` trusts a valid source-built table and binary input; it is not a malformed-table/bit validator. Finite unresolved inputs need a length-bearing sequence for its final `len(bits)` branch. The mathematical infinite fair-stream process and finite-prefix API are distinguished. Counterless reversible cleanup, tape restoration/freshness and ordinary/native realization are separate successor contracts.

Written adversarial controls in the code note distinguish off-by-one digits, root-revisit stopping, omitted root cost, incorrect output labels, correct marginals with wrong joint law, free initial entropy and malformed inputs. They are deductions about altered premises/code, not executed mutation outcomes. See VALIDATION for review chronology, source/byte custody and actual later verification receipts.

## Limits and predecessor credit

No source formula/code correction is requested. Original formal/kernel acceptance remains unmet under changed written-review scope. Source6072 and classical dyadic-tree/depth-count methods retain priority. JoyboyBrian6096 already resolves actual `/52` residue/availability questions and6546 provides a complete numerical caller; this audit does not describe those results as absent. Their exact physical realization, table access, random-tape movement, owned stopping/cleanup, complete invoice and all selected framework assumptions are separate. No physical supplier, runtime improvement, full multiplication theorem, κ/frontier/adoption change or merge follows.
