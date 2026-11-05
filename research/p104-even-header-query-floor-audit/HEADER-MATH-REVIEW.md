# Independent written review of the even-control header argument

**Disposition: PASS under the stated formal alphabet; no correction requested.** Reviewed HEADER-PROOF-DRAFT.md SHA256 `a6854cef4966babdd068ccf652d78f3e731405046964288c547f6dc1545c36a6`, SCOUT-PROOF.md SHA256 `21ea13b2177a4588aa645ca07aef950681407ba85d3298067ffd428275a92123`, the source's existing header argument in RESEARCH-NOTES and the exact inert PR6114 proof. Both new engine implementations, their outputs and old/new scientific checkers were off limits and were not read, imported, compiled or executed. This is a written mathematical review, not finite experimental validation or another blind derivation.

## 1. Correct treatment of the zero-divisor ring

Over K=Q(i), E=K[t]/(t^2-1) embeds as the even subalgebra of R=K[q]/(q^4-1) via t=q^2. R is a free E-module with basis(1,q): a purported relation A(t)+qB(t)=0 has a degree-below4 representative whose four K coefficients all vanish. This uses division by a monic polynomial for normal forms, not division by arbitrary nonzero elements. E and R can both have zero divisors without affecting this uniqueness.

After t=theta=+1 or-1, the quotient K[q]/(q^2-theta) likewise has the unique K-basis(1,q), even though it splits over K. A single character q=1,-1,i or-i does not retain that two-dimensional coefficient decomposition. A_theta and B_theta are ordinary field matrices; the proof never assigns a field rank to W over a zero-divisor ring.

The ordinary-control definition is sufficient and precise. O(theta) invertible preserves rank(A_theta) by left multiplication. Invertibility at both theta values is equivalent to invertibility over E by the two central orthogonal idempotents(1+theta*t)/2; no unproved domain cancellation is used. Lambda_plus takes values1,i and lambda_minus takes values1,-i, so both are even units. They are not free odd q factors.

## 2. Universal count, including its first-query qualification

For W=A+qB and a legal distinct-role query I+c(t)qE_ds, direct ordered multiplication gives

```
A' = A+t*c*E_ds*B,
B' = B+c*E_ds*A.
```

E_ds*B has at most one nonzero row, so each sector update of A has rank at most one. The rank can decrease by no more than one; the proof does not require monotone decrease or assume every paid query helps. If a sector coefficient vanishes, the update is zero and counting the query still gives a valid weaker bound.

An invertible even entry has A of full rank N and B=0. Even ordinary factors preserve this property before the first paid odd query. That first query leaves A unchanged exactly, not merely its rank. After M>=1 queries, rank(A_theta_final)>=N-(M-1). A full target with r independent diagonal odd q-times-even-unit entries and N-r even-unit entries has rank(A_theta_final)=N-r. Thus M>=r+1 for r>=1. A zero-query word is separately excluded by full initial even rank; it is not assumed away. For r=0, the empty identity word correctly shows that an added one-query overhead would be false.

This is a necessary lower bound, not a universal sharpness or existence theorem for every r. It does not claim that r+1 queries attain all such targets or that an actual physical realization is available.

## 3. One sector for the bound, both sectors for the application

One sector, including theta=+1, already suffices for the inequality if its final even-part rank defect is r and its ordinary factors satisfy that sector's invertibility condition. The stated complete diagonal supplies the same defect in both sectors. Checking the second sector is not an extra logical premise needed to deduce33 from r=32.

However both sectors, or equivalently all four reconstructed characters, are needed to verify an actual full q^4 endpoint including absolute phase. At theta=+1 the raw source q^-1 equals q, while at theta=-1 it equals-q. A plus-sector rank trace alone cannot certify that distinction. Nor do two final rank numbers certify every matrix entry. The proposed whole34-by34 application must retain all original independent columns, including fresh32 and33, and compare the actual full scalar endpoint. Such computations are separate pending engine evidence, not supplied by this written proof review.

The data closure identifies15 QUERY and18 LOCAL occurrences, with100 ordinary lambda factors, and the raw declared32q^-1+2I endpoint. At D_j=1, each LOCAL is a single q^-1 shear and the stage idles become identity. All other instruction-class/invertibility checks and the actual whole-word equality remain necessary before calling the bound attained by that literal word. Original fresh-body identities, native port action, stage payment and physical storage are not proved by specializing bodies to one.

## 4. Hypothesis and accounting controls

The free-odd-multiplier control is valid: allowing diag(q,1) as ordinary work reaches an r=1 target at zero counted queries, outside the even alphabet. Similarly, at the single character q=i a constant Gaussian diag(i,1) matches a specialized odd target and destroys the formal distinction. Neither is a counterexample to the declared model.

Initializing a nominal odd input to zero removes its independent input column and can make a nominal odd target unobservable. Supplying q*x before entry instead gives initial odd content relative to the named unphased input. The first-query refinement then lacks its B_entry=0 premise. Renaming that prephased input as a new arbitrary variable changes the target contract; it does not provide a counterexample for fixed original inputs. The draft correctly distinguishes these cases.

A multirow or operator-valued paid update can change A by rank greater than one, and an uncharged odd Q_POWER or an odd coefficient hidden in an ordinary boundary changes the legal alphabet. These are model limits, not a classification of every possible escape or an allegation that an actual source instruction violates them. Even ordinary maps may couple many scalar fields; touching several fields alone does not invalidate the proof. Likewise calling these ordinary operations free means uncounted in this specific header-query tally, not physically costless or unpaid in the complete invoice.

## 5. Prior scope, credit and conclusion

Matarener/PR6114 already states the even-part rank tracker, partially twisted-output version and first-shear overhead. Its proof explicitly credits Cinna Davis's prior GLOBAL/parity-header/pruning observation and PR6120's left-boundary/kernel repair. The full target and ordinary output boundaries in the current draft are consistently included; it does not read zero rows before an unaccounted output basis. PR6114's separate UFD/determinant stage-payment argument is not imported into the q^4 quotient, where a domain argument would require separate justification.

zxv/PR6726 already states/proves33-query saturation under its scalar contract. The q-independent-control wording is not evidence of a false source count: its q=+1/-1 comparison encounters the same lambda value1, so it can already be read in the relevant sector. The current contribution is an external exact even-q^2 application qualification and independent actual-word rank/trace bridge, not discovery of33, a new parity method or a new full-invoice theorem.

No counterexample or missing implication was found within the written theorem. Its model limits, r=0 exception and all-column requirement are sound. Actual engine packets, controls and observed traces remain pending at this review; no code/result acceptance is inferred. Native/physical port coupling, pricing/ordinary work, stock/ownership, compiler, precision/tape, recovery and all selected assumptions remain outside. Source/controller/native contributors and substantial OpenAI Codex assistance retain their disclosed credit; this is not human or proof-kernel acceptance.
