# Independent event invoice and exact price audit

Owner: execution prices lane, 2026-10-24 Australia/Sydney. Construction credit belongs to Ali Romman (#5383), with Dugongue's #5387 compiler-margin refinement; retained native/source and compiler lineage belongs to Cao Yifan, Cinna Davis, zxv, Jacob Alan Sussman and the other credited source contributors. This audit uses substantial OpenAI Codex assistance. It edits only its own package and publishes no external message or selected-record change.

## Scope and inputs

Canonical main is `1ec1119972c9aefe42525172d07b332fcff81cb4`. The selected conditional #4610/#5241 baseline remains `.0030217758`. The literal candidate is #5383 at `4bd6efa51a495a7c7b7754915cf0244e7e60969e`; the separate successor is #5387 at `b1ab650d36f59e5be682a813145b7c67e219e341`. `INVOICE.json` binds exact compressed source and candidate word hashes plus the controller hash. `coordination/SOURCE-READY.json` and the source lane's manifests establish the Git-byte bindings separately.

The checker imports only the Python standard library. It does not import the candidate's `native.py`, `price.py`, interval engines, author `RESULT.json`, or #5384's audit code. Primary literal words and the retained controller are shared evidence; independent implementation does not mean independent construction. No #5384 arithmetic PASS is inherited. Native endpoint/phase/zero/ownership correctness, controller Laurent factorization and physical applicability remain dependencies owned by the corresponding independent audit lanes.

## Invoice from events

The audit reads both candidates' actual `WORD.json.gz`, not just their advertised paid profiles. It reconstructs binary frame bases, checks independence and nested paid-frame inclusions, tracks frames across every scalar/warp/paid/zero-retag event, derives each paid rank from endpoint frame dimensions, and checks final frames. It derives helper ranks from start/final frames, surrendering every owned `L` helper endpoint. The census is conditional on the separate proof that each retained endpoint is an eligible ordinary completed helper and each zero retag is valid.

Whole-controller counts come from every actual `physical_events` entry: 16 backward and two forward LOCALs, 15 query shears, 15 IDLE windows, 90 ADDs and 16 SIGNED_SWAPs. Query volume is the canonical `v=112`; idle volume is `2v`; controller rank step is canonical `h−1=8`. Main completed targets are derived from the controller's diagonal exponents, subject to the separately checked controller identity. Author invoice fields are not used.

Both literal candidates give:

- Paid `P={1:41170,2:7416,3:9180,4:2286,5:720,8:16,16:448,24:448,32:448,40:448,48:448,56:448,64:448,72:224}`.
- Productive `T={4:504,7:126,8:846,9:5740,17:448,25:448,33:448,41:448,49:448,57:448,65:448,73:224,145:224}`.
- 64,148 paid calls, 10,800 productive fields; paid rank mass 237,982, productive rank mass 238,734, surplus 752.
- Actual selected-source delta: paid `−128 H1−128 H8`, productive `−128 H9`. The removed paid rank mass 1,152 is exactly the lost productive rank mass 1,152; job counts decrease by 256 paid and 128 productive.

For `0<C<1`, put `t=1−C`. The moment improvement is exactly `128(1+8^t−9^t)>0`. Strictness follows because `(x+1)^t−x^t` decreases with `x>0` and is strictly less than its value 1 at `x=0`. This cheap direction proof does not establish legal simultaneous preparation or native semantics.

The distinct #5387 literal preparation has pivot 261 where #5383 has pivot 288, so it is checked separately. The independently counted scalar tariff maxima are #5383 **158,744**, #5387 **158,776**, versus source backward **158,168**; both forward words have 158,120. These use the retained dyadic scalar tariff (two real operations per clear/copy and the source's binary scalar realization), calculated from actual scalar events. Route, stock, movement, precision and expanded all-size obligations belong to the physical lane; they are not silently set to zero by this recursive invoice.

## Independent arithmetic method

Every interval endpoint is an integer multiple of `10^-65`. Arithmetic rounds outward using exact Python integers. Natural logs use binary range reduction followed by the rational `2*atanh(z)` series with an explicit geometric remainder (`z<=1/3`); exponentials use positive Taylor terms with an explicit geometric remainder. Negative powers use outward reciprocal intervals. The checker re-derives target/paid raw moments, alpha, the paid higher-moment gamma, target-completion delta, both completion tails and the reserve/rounding bound. No floating-point sign decides acceptance.

It tests both parameter choices separately: #5383 `K=.00302666,C=.00302667,rho=10^-9`; #5387 `K=.003026674765,C=.003026674766,rho=10^-12`. Both use tensor power 1024, cutoff 20, floor 21, higher-moment offset 1/5, tail limits 97/100, and theta 63/64 with logarithmic power 1000. The outer lane independently owns seven-way gaps, finite H/grid predicates, admitted BIT compatibility and all 54 strict plus four functional outer predicates.

The root-serialized run produced `PASS_INDEPENDENT_EVENT_INVOICE_AND_EXACT_PRICES` in `RESULT.json`, bound to checker SHA-256 `e5f828e06b896723da4b58ca8c780609b8b94bde374a2ffeda1cab143323a335`. Both parameter choices pass all listed price/tail/capacity checks. The following values are decimal approximations for reading; the machine receipt retains outward rational intervals.

| Quantity | #5383 | #5387 |
| --- | ---: | ---: |
| Raw moment surplus | 0.001176849586965156 | 0.000000512036327369 |
| Alpha | 0.999999995016963388 | 0.999999999997831927 |
| Paid higher-tail gamma | 0.956968564096059992 | 0.956968566609975897 |
| Target completion delta | 0.951652473261883820 | 0.951652475842024106 |
| Alpha correction budget after reserve | 0.000940678416953355 | 0.000000275865161369 |
| Coarse normalized-completion slack | 0.000001023067628850 | 0.000000000092677424 |
| Capacity eta | 0.000000199495867924 | 0.000000199491021600 |

The unique raw crossing is strictly between `.00302667476807` and `.00302667476808`. Its headroom above #5383's claimed K is `(0.00000001476807,0.00000001476808)`; above #5387's K it is `(0.00000000000307,0.00000000000308)`. Both fixed reserved certificates afford **zero extra H1 calls**. The derivative negation is bounded below by more than 195,473 on `[0,.05]`, and the remaining moment is bounded above by less than −6,820 on `[.05,1]`.

Proving this profile's ceiling or increasing root precision supplies no new native mechanism. #5387 is a compiler-margin refinement on the same paid/target profile, with fresh preparation charges.

## Controls and boundary of the result

The checker rejects one extra unpriced H1 at #5383's tested saving. At #5387's stronger tested saving it separately requires rejection of the predecessor `10^-9` alpha reserve. The coarse sufficient bound with fixed rounding allowance `4/2^32` rejects reserve `10^-13`; this is failure of that stated sufficient certificate, not a universal impossibility for every tail/rounding analysis. Both actual directed tail powers and the stated coarse sufficient bound are checked for the accepted choices.

At `rho=10^-12`, the next tested-saving tick `.003026674767` still passes reserved alpha with positive budget about `2.9046542321*10^-8`; `.003026674768` fails with budget about `−2.1777207673*10^-7`. Therefore #5387's printed endpoint is not established optimal. Passing a later alpha tick does not certify a later outer endpoint; failing an H predecessor only locates the sufficient compiler grid minimum for its declared gap. No global endpoint optimality follows. The exact interval engine checks positivity at `.00302667476807`, negativity at `.00302667476808`, strict decreasing moment on `[0,.05]`, and negative moment on `[.05,1]`; thus the bracket bounds the unique raw crossing for this exact profile on `0<C<1`.

The invoice-only check passed under hard CPU 15 s and address-space 128 MiB (approximately 0.6 s wall after both candidate words were included). Full exact arithmetic completed through the root's serialized guard. Eleven additional cheap exact controls confirmed interval enclosure of integer powers and reciprocal powers. The unearned-128-H9 mutant recomputes its proposed-invoice hash, executes the invoice-consistency validator, and is rejected against the literal event-derived productive census. No heavy/native/Lean/solver run was launched by this lane.

Open next questions: consume the independent native/controller/ownership proofs and fresh physical scalar/routing/stock bounds, then combine this result with the separate compiler/outer audit. A price PASS is one component of conditional admission, never selection or an unconditional multiplication theorem.
