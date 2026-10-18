# Attribution, license and assistance disclosure

Contribution attributed to **William Lawyer**. Substantial OpenAI Codex
assistance was used for task selection, derivation, code, tests, review and
writing. No independent human mathematical review is claimed.

Chafik Boukhalfa / chafreaky's PR628
(`0768f97d06c623b8211e651543c66135796b62bf`) supplies the audited interval
implementation, dyadic factor nominations, stable-factor model, scan bounds
and coefficient-to-operator perturbation context. Its radix-4 and radix-8
algebraic crosschecks are acknowledged predecessors of this radix-9 audit.
The original interval code, factor file and notices are preserved unchanged
under `vendor/`.

Ali Romman / aliromman's incorporated PR621
(`520774462b19b29af41554b74def31f9d01e997e`) supplies prime-power circle
nonvanishing and the uniform inverse-conditioning context. OpenAI's pinned
exact-DFT preprint (`adc7f1241b42e322a6451854ab7e4b4c146bf78a`), classical
q-Pochhammer/Newton factorization, Alexey Kuznetsov's cited q-calculus work,
Pan's approximate-factorization theorem as presented by Mehlhorn, Sagraloff
and Wang, and Brent's elementary-function algorithms retain the specific
credits recorded in `vendor/NOTICE.md` and `vendor/SOURCE.json`. The new
independent enclosure code does not implement those numerical algorithms.

Concurrent related work is credited without being imported or treated as
accepted: PR663 audits nonlinear restoration; PR692 checks weighted-stride
inverses; PR764 sharpens cyclic-scan rounding; PR666 supplies composite
Bezout certificates; PR668 checks resultants with CRT; PR736 improves the
incorporated resultant replay. This contribution isolates a different
coefficient-enclosure dependency and imports none of those implementations.

The final overlap refresh also found Hao Yan / FanPUYen's PR796
(`22902155c7875139e43e4fdf15723142d6709bdd`), which derives nonarchimedean
root valuations and independently reconstructs cyclotomic coefficients.
That related exact arithmetic work is credited; it does not audit PR628's
complex coefficient rectangles or the two dyadic factor residuals checked here.
No PR796 implementation or result is a dependency of this package.

The publication refresh found Rafael Guevara / alephnan's PR803
(`d213ac12d4a1ab8f717d942e844df318ceb395fb`), a degree-controlled complex
inverse-norm bound, and navinor's PR804
(`1f387e7090359165a0df046183eb8fa16c246d7d`), integral-divisibility
verification of the p-adic valuations with additional radix-81 coverage.
Both are related context, with different obligations from this finite
radix-9 interval-containment and submitted-factor audit. Neither is imported
or used to change the inherited execution-error formulas.

The cubic/cyclotomic identities, bisection, rational interval arithmetic and
finite geometric inverse identity are standard. No literature-priority claim
is made. "Independent" describes a separate arithmetic implementation and
algebraic derivation; it does not mean independent human authorship, formal
verification, maintainer acceptance, or a new multiplication exponent.

New code and documents are provided under the repository's Apache-2.0
license. The unchanged predecessor files retain their original notices.
