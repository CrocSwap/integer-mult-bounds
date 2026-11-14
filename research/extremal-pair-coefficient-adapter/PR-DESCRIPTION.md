# Produce the selected extremal Gaussian tables through four existing encoded scalar calls

## Result and why it matters

[A12](https://github.com/CubeJerry/integer-mult-bounds/commit/702c7616667c5f4e583eb73687944d148b7a1ccf) gives a quantitative rank margin for two deterministic extremal source pairs but leaves table production as an explicit premise. This package closes that local interface with four calls to the unchanged scalar primitive audited in #6085. It does not implement another exponential backend.

For borrowed binary inputs `(p,alpha,s1,t1,s2,t2)` with `p,alpha>=1`, `1<s_l<t_l<2s_l` and `alpha^2<=4p`, one setup uses `P=p+8,F=2alpha^2`. Four exact rational arguments are `alpha^2(2(t_l-s_l)+1)/s_l` and `alpha^2(2s_l-1)/s_l`. They lie strictly in `(0,F)`, and the returned dyadic factors have off-diagonal error less than `2^(-p-7)` and exact diagonals.

For A12's admitted fine-prime family at `p>=4096`, these are the actual selected source coefficients. With `a=pi alpha^2,w=exp(-2a)`, scalar error and omitted matched periodic aliases each fit `2^-37 w^2`. The emitted factors therefore approximate the selected periodic principal sections within `2^-36 w^2`, meeting A12's contract. Their tensor and its own exact inverse inherit full ordinary Stein displacement rank in all 24 orders. Inversion and taking a section of the full source inverse are not interchanged.

## Complete interface and costs

All six borrowed Count bodies remain unchanged and their canonical heads return to 1. Nine distinct returned owners remain live: precision and eight row-major numerator fields. Private setup closes before return; caller retirement of every returned owner is explicitly paid. Closing those nine outputs does not authorize emptying a pool containing other live leases, including borrowed inputs. Normal domain rejections restore inputs. No malformed-tape, allocation-fault or interruption rollback claim is made.

With fresh private grants, or an explicit O(p+B) entry-history bound per fixed role, the complete local tariff is `O(p^3+(p+B)^2)` bit time and `O(p+B)` storage, where B is maximum input bit length. Reused blank grants retain `sum_tau max(H_tau,C(p+B))` storage and any actual full-history sweep/transport charge. The proof binds the existing precision policy to `R<=257p`, keeps rational input sizes, uses the existing `reduce=False` ABI, and pays argument construction, diagonal values, copies, scalar calls, private histories and output retirement. `O(p^3)` requires a separate `B=O(p)` source bound. This is the retained encoded Count/Rational model, not a new native ROM.

The #6099 ProductionPlan domain is not needed for isolated calls; this does not repair its global admission. Source/primality/alpha admission, index routing, tensor materialization, payload transport, inverse algorithms and a complete Gaussian caller remain separate. No new kappa or selected-certificate change; all five assumptions remain.

## Verification and reproduction

Canonical base `e54523517d0f03e58352e647c403a5af3e525a57`; only a new research package. Exact runtime/source pins are declared. The existing predecessor archives are reused as canonical inputs, not copied into this contribution.

```sh
python3 -I -W error -B research/extremal-pair-coefficient-adapter/verify.py
python3 -I -O -W error -B research/extremal-pair-coefficient-adapter/verify.py
python3 -B scripts/research_package.py --package research/extremal-pair-coefficient-adapter
```

Normal and optimized direct runs produced identical `PASS_EXTREMAL_PAIR_COEFFICIENT_ADAPTER` receipts. The actual encoded packet executes four unchanged calls under sealed constructors/no-decode protection, checks complete scalar intervals against the retained independent-algorithm oracle, binds arguments and precision, checks all nine outputs and history cleanup, and exercises seven guarded invalid inputs. It is a finite semantic check, not a p>=4096 run or a universal proof. The small packet deliberately demonstrates that successful low-precision production does not imply A12 rank admission. The quantified theorem is in PROOF.md. No full supplier replay, human/formal-kernel acceptance or hosted CI is claimed.

## Novelty, credit and remaining work

#6085 supplies the classical scalar algorithm, encoded implementation and tariff; A12 supplies the quantitative margin. The new result is their exact extremal source join, including admission, aliases, ownership and the full local bill. Bounded overlap checks found no identical join and make no worldwide priority claim.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance. The worker identified the existing scalar backend, derived and implemented the adapter; the lead proposed closing the production premise; a separate worker reviewed admission and ownership. Credit JoyboyBrian / #6085 and #6099, Chafik Boukhalfa / #1786, Vlado Vojdanovski / #1673, Jeremy Kothe and the bilateral source lineage, and the retained arithmetic/framework contributors. Original notices and Apache-2.0 terms are preserved.

Next obligations are to bind the selector and owned tables to a complete caller and to prove new margins before extending to arbitrary phases or larger dimensions.
