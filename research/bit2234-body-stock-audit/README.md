# Audit of body-dependent borrowing stock for the proposed BIT caller

The reserve in PR2234 can be chosen from the actual post-borrow body width,
**conditionally on that proposal's complete-row caller and physical contracts**.
For this changed reserve, **245,773 is the least uniform integer fit cutoff**
over the stated prime domain. The original-width reserve has cutoff 311,311
by PR2324; that theorem remains unchanged. This answers its first open question
at the conditional stock/divisibility level, without implementing its caller.

The audit also finds a concrete trap: an equality fixed-point iteration has
**no solution at width 273,158**, although the borrowing inequality is feasible.
Its least witness overborrows by one digit. A monotone inequality search avoids
the trap and retains the logarithmic borrowing charge.

No new multiplication exponent, selected frontier, fourteen-stage stock
identification, or complete supplier admission follows. The scientific base is
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4, OS assignment
seed 60 (adversarial audit). The [claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2209#discussioncomment-18941771)
and [TASK.json](TASK.json) record scope selection and overlap.

## 1. Exact sources and changed reserve

The source contract is Jose Manuel's PR2234 at
`d047ef86fbc5b1614d3d8e2b8d3441413beab73f`,
[PROOF.md sections 1, 6 and 8](sources/pr2234/PROOF.md).
Aakash's PR2324 at `0ec8a26572069b6109decadd488b9770944a4296`
supplies the original-stock theorem and the
[post-borrow-body handoff](sources/pr2324/README.md).
These documents and the inherited notice are retained byte for byte, with
Git-blob and SHA256 identities in [SOURCES.json](SOURCES.json).
No predecessor Python code is imported or executed.

For integer original radix-q width `e>=1` and prime `q>2^80`, fix

```
c=17/10000,  w=ceil(e^c),
M=lcm(28416,28425)=269241600,
K=M |GL_64(F_q)| q^(4096(w-1)),
D(n)=0                         if n<64,
D(n)=1+D(42 floor(n/64))        otherwise.
```

Keep `w` fixed during borrowing and all coarse recursion. For an integer
`0<=k<e/2`, define `n(k)=floor((e-k)/w)` and the **changed** reserve
`S(k)=K^D(n(k))`. The condition is

```
S(k) <= q^k.                                                   (A)
```

PR2234 section 8 instead takes the sufficient stock `K^D(e)` before choosing
k. We change only that sufficient choice; the local packet K and recursive
caller contract remain the same. In particular, K still charges all high
matrix fibres and the lcm of live/physical role counts.

## 2. Conditional complete-row implication

Assume the full section-6 caller contract for every integer row multiplicity:
the weighted endpoint, pointwise row/spectator restoration, closed work,
restored heads, fresh-field access, parking/locality and uniform time. Also
retain its elementary digit operations, complete-range padding and wrapper.
These are substantive physical assumptions, not consequences of our arithmetic.

Given a witness to (A), put `d=D(n(k))`, `S=K^d`, and
`t=ceil(q^k/S)`. Padding the earlier high field gives exactly `tK^d` rows.
Since `S<=q^k`, its volume factor is strictly below two. The stock need not
divide `q^k`; the padded row count supplies the exact divisor.

For `d>=1`, the unchanged row decoding leaves

```
U=t*(M/28416)*K^(d-1)=t*9475*K^(d-1).
```

Every child width `n'<=42 floor(n/64)` has `D(n')<=d-1`, so its required
`K^D(n')` divides U. Rank-one fallback children `f` and `floor(f/2)` also
obey that bound. All high fibres remain complete; parent high fields stay
spectators, rather than becoming the child's fresh stock. At `d=0`, the
retained row-uniform leaf needs `S=1`; `n=0` is the identity.

Handle the fewer-than-w remainder digits by the inherited elementary routine.
On whole-atom bodies the source uses

```
D <- D-H;  F_I;  D <- D+H;  F_I;  D <- H-D.
```

The ADD maps leave rows alone, and each `F_I` restores every row coordinate
pointwise. Thus both calls reuse the same stock. Their completed endpoint is
the body swap on each padded row, independent of its value; the genuine
`[q^k]` subset is invariant there. Remove padding only at that completed
endpoint, then interchange the two high fields by the inherited digit routine.
Aggregate preservation of the row multiset would be insufficient: pointwise
restoration is load-bearing. No divisibility of `e-k` by w is assumed.

All descendants still have generation depth at most `D(e)`; preserve the
source's global depth across constant-expression resets. The old root-coupled
preparation bound remains conservative. The argument is a conditional
composition lemma, not a new proof of those physical invariants.

## 3. Choose an inequality witness, and charge its cost

Let `m=floor((e-1)/2)`. As k increases, `n(k)`, `D(n(k))`, and `S(k)` do
not increase, whereas `q^k` increases. Thus a witness exists iff (A) holds
at `k=m`. This is an existence test, not a prescription to execute near-half
borrowing, which would lose the desired time saving.

Write `P(q)=product_(i=1)^64(1-q^-i)`, so `|GL64(F_q)|=q^4096 P(q)`.
Since `M<2^29`, `q>2^80` and `0<P(q)<1`, the integer upper bound

```
ceil(log_q K^d) <= U_w(d):=4096wd+ceil(29d/80)
```

holds, including d=0. Choose the **least** k in `[0,m]` satisfying
`k>=U_w(D(n(k)))`. This predicate is monotone, so exact integer bisection
finds k or reports no conservative witness. It is sufficient, not necessary
for each individual q. Integer powers compute w without floating point.

Set `Ue=U_w(D(e))`. If `Ue<=m`, k=Ue passes because `n(k)<=e`. Otherwise
every admissible k is below Ue. Hence whenever the guard is feasible,

```
k* <= min(m,Ue) = O(w log(max(2,e))).
```

Under the retained time contract, the completed wrapper is charged
`O(V[n+n^(1-c)w+w+k*])=O(V e^(1-c+c^2))`. The extra selector uses polynomial
control work in `log e` (integer powers, depth iteration and bisection); it
is absorbed by the complete input volume, which is at least `q^(2e)`.
The uniform cutoff below leaves only finitely many widths for elementary
fallback. This preserves the *conditional ordinary-caller* saving
`c(1-c)=169711/100000000`; it is not a multiplication exponent claim.

## 4. Sharp uniform cutoff 245773

The exact inverse depth thresholds are
`b_1=64`, `b_(d+1)=64 ceil(b_d/42)`, with `D(n)>=d` iff `n>=b_d`.
For `245773<=e<2^20`, `w=2` and the smallest possible body is
`n(m)=floor((e+2)/4)`. Consequently:

| Inclusive widths | Depth | U | First width minus 2U |
| --- | ---: | ---: | ---: |
| 245773–300541 | 15 | 122886 | 1 |
| 300542–457981 | 16 | 131078 | 38386 |
| 457982–698109 | 17 | 139271 | 179440 |
| 698110–1048575 | 18 | 147463 | 403184 |

The positive margins give a conservative witness on every interval. Their
boundaries are `4b_d-2`, including both parities; replacing `n(m)` by
`floor(e/4)` would miss the depth increase at e=300542.

For the infinite tail set `j=floor(log2 e)>=20`. The inherited two-level
contraction `2*42^2<64^2` gives `D(n(m))<=D(e)<=2(j+1)`. Also
`w<=2*2^(c(j+1))`. The conservative guard itself satisfies

```
U_w(D(n(m))) <= 4097wD(n(m))+1 <= B_j+1,
B_j=16388(j+1)2^(c(j+1)).
```

Reuse PR2324's smoothed tail argument, now explicitly for this guard.
Since `21c<1/2` and `sqrt(2)<3/2`,
`B_20+1<516223<2^19`. The normalized B ratio is
`((j+2)/(j+1))*2^c/2 < (22/21)*(3/4)=11/14<1`;
the normalized additional 1 contracts by `1/2<=11/14`.
Thus `U<2^(j-1)<=e/2` forever. This covers all later atom-ceiling jumps,
without assuming that a discontinuous stock-to-width ratio is monotone.

For sharpness take

```
e=245772, m=122885, n(m)=61443, D(n(m))=15,
q*=15*2^78+1=4533471823554859405148161 > 2^80.
```

Exact modular exponentiation gives
`11^((q*-1)/2)=-1 (mod q*)`, and `(2^78+1)^2>q*`.
For any prime divisor p of q*, the order of 11 modulo p has 2-adic
valuation 78, so `p>=2^78+1>sqrt(q*)`. This proves primality: a composite
integer must have a prime divisor at most its square root.

Exact integers also certify `2(q*)^5<M^15<(q*)^6` and `30<q*-1`.
The product inequality and Bernoulli give
`P(q*)^15>1-15/(q*-1)>1/2`. Therefore

```
(q*)^5 < M^15 P(q*)^15 < (q*)^6,
ceil(log_(q*) K^15)=8192*15+6=122886 > m.
```

Every allowed k fails by monotonicity. Every smaller proposed uniform cutoff
includes this width. Thus **245773 is the least uniform cutoff for existence
under (A)**, not merely for our sufficient guard. This does not say every
smaller width fails, nor that every possible reserve or caller needs this cutoff.

## 5. Exact counterexample to equality iteration

At `e=273158`, with the same certified q*, w=2. The exact exponent strips
for depths 15 and 16 are respectively 122886 and 131078; the latter follows
from `2(q*)^5<M^16<(q*)^6` and `P(q*)^16>1/2`.

At k=122886, `n(k)=75136=b_16`, so the log ceiling is 131078, larger than k.
At k=122887, `n(k)=75135`, so it is 122886, smaller than k. The exact
log-ceiling function is nonincreasing: all k below the first point have a
larger ceiling, and all k above the second have a smaller one. **No equality
fixed point exists.** Iteration cycles `122886 -> 131078 -> 122886`.
The least feasible k is 122887, one more than the ceiling for its resulting
stock. Padding and the inequality allow this extra digit.

## Reproduction and evidence boundaries

From the repository root, Python 3.12, standard library only:

```sh
python3.12 scripts/research_package.py --package research/bit2234-body-stock-audit
```

Expected markers include `PASS_BIT2234_BODY_STOCK cutoff=245773 boundary=245772
no_fixed_point=273158 no_new_kappa`, `PASS_INDEPENDENT_BODY_STOCK_AUDIT`, passing
normal/optimized tests, and `PASS_REGISTERED_RESEARCH_PACKAGE`.

`verify.py` authenticates consumed sources and checks a stored canonical
receipt; missing or changed receipts fail rather than regenerate.
`--write-receipt NEW_EXTERNAL_PATH` explicitly creates a separate receipt.
`independent_check.py` does not import it: it propagates depth bottom-up and
checks all 1,048,575 positive widths below 2^20, then directly compares the
full integer GL products at depths 15/16, independently of the Bernoulli bound.
Tests cover atom-ceiling boundaries, selection, abstract row reuse, and source,
receipt, strict-fit, rounding, prime and restoration failures. Such abstract
finite checks do not execute the GL64 payload or establish its physical contract.

The all-width theorem rests on the written proof, not finite-search
extrapolation. No full selected cold replay, transition-table compiler,
proof-assistant theorem, independent human review, or hosted-CI result is claimed.
The selected source-binding baseline is checked separately; κ stays unchanged.

## Open next questions

1. Can the joined caller establish the assumed fresh-field, pointwise-row,
   restoration and uniform-time contracts? These block physical admission.
   Start by checking this changed reserve against the PR2234 section-6 caller
   and the PR2310/Discussion2319 preparation/dispatch work; an endpoint or
   macroplan receipt alone is insufficient.
2. Can the stopped row-divisibility and padding-restriction implication be
   formalized with explicit physical contracts? Start with the theorem in
   section 2 and the no-fixed-point witness in section 5. A formal model of
   the row-uniform caller, rather than a stronger arithmetic estimate, is
   the prerequisite. [TASK.json](TASK.json) records the structured handoff.

## Credit

Sagar Thakrar (@thakrarsagar), with substantial OpenAI Codex assistance in
research, proof, implementation and writing, including separate source-contract,
exact-product and test agents. This is not independent human review.
New work is Apache-2.0; retained predecessor documents remain unchanged.

Jose Manuel (@jmbarrancoml) supplied PR2234's caller, K, D and ordinary wrapper;
its [NOTICE](sources/pr2234/NOTICE.md) preserves the selected PR589/PR555,
alephnan, eumemic/source527, Ross Richardson, commdata2338 and routing/parking
lineage. Aakash (@aakashthakkar) supplied PR2324's original-stock sharpness
method, dyadic tail and body-stock handoff. We reuse and credit those tools,
changing the reserve and proving the conditional divisibility/selection result.
Josie Elliston (PR1956/1965), ToikY (PR1990), Adam Gall (PR2084/2097), Nick
Petalas (PR2120) and Sricharan Vagvala (PR2105) supplied the stock/time/producer
distinctions consulted during overlap. Their parent-envelope arithmetic is
not claimed as new.
