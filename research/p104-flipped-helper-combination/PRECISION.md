# Fresh precision and stock prescription for the combined word

These constants belong to the exact 58-split mixed-port word. They do not
reuse #6916's or #6917's literal event, coefficient or productive-width caps.
They retain the named finite-compiler, numerical, fixed-tape and erasure
contracts explained in the source-pinned compiler proof.

| Quantity | Original caller | Compressed caller |
|---|---:|---:|
| Native public fields | 1,420 | 1,420 |
| Native events | 67,514 | 67,514 |
| Native owned labels / lifetimes / live peak | 51 / 54 / 30 | 51 / 54 / 30 |
| Complete productive fields | 22,504 | 22,504 |
| Complete paid jobs | 119,046 | 119,046 |
| Complete paid rank mass | 317,444 | 317,444 |
| Largest native absolute coefficient | 1,746 | 1,746 |
| Numerator / denominator bit maximum | 13 / 10 | 13 / 10 |
| Native scalar upper | 1,343,940 | 1,343,940 |
| Native logarithmic height charge | 131,577 | 131,577 |
| Type-A caller height per port | 6,514 | 3,480 |
| Type-B caller height per port | 5,508 | 5,508 |
| Whole raw logarithmic height charge | 3,037,794 | 2,746,530 |
| Full ordinary upper, including LAMBDA | 996,089,112 | 836,590,872 |

For each dyadic ADD/COPY coefficient q, charge
\(\lceil\log_2(1+|q|)\rceil+\log_2\operatorname{den}(q)\).
For SCALE use
\(\lceil\log_2\max(1,|q|)\rceil+\log_2\operatorname{den}(q)\).
The caller charges eight per LAMBDA, sixteen per thin query and four per
swap. The fresh whole-caller charge is 18 times the native charge plus
96 times the A and eight times the B caller charge. This conservatively
bounds multiplicative growth and denominator accumulation. Including every
positive Gaussian child, at column width f the respective raw envelopes are
\(2^{3037794+317444f}\) and \(2^{2746530+317444f}\).
This is an ideal arithmetic envelope, not an executed rounding theorem.

Global LAMBDA scratch uses an existing full-shape query bank, returned before
the next port or event. The native's 53 dirty clears require the inherited
erasure contract. Clearing never removes error already propagated into
another field, and COPY means ADD into currently initialized storage.

The complete finite recipe is the chronological power-1920 product, explicit
completion and paid splitting, followed by the ambient-cap compiler with
cap \(153^{1920}\), logarithm power 2300 and H=12,293,300,000,000,000.
Let W be its actual productive width, P its complete rank-one child count,
R its route/normalizer record count, U its raw-caller occurrences and J its
native occurrences. These counts are defined by that finite recipe, not by
substituting the raw counts into the expanded template.

Allocate separate owned banks to different occurrences if no reuse proof is
available. A conservative allocation is
\(O=51J+U+O_{\rm auxiliary}\), with every further compiler/completion/child
bank included in the last term. None receives productive credit. Let
\(G=10^9U+8R+G_{\rm compiler}\), where the last term includes every
additional ordinary compiler operation. The checked raw envelope justifies
the first term. Set

\[
Z=W+O,\quad E_0=64(Z+N+P+G+1)^3,\quad
B_0=P+E_0,\quad C_0=32NB_0^2,\qquad N=2^H.
\]

Use the retained completed-child estimate \(A(e)\le2B_0e\), productive
stock \(\lceil\log_2 W\rceil D(d)\), and the product of the separate BIT
and complex stocks. D(d) remains the input-dependent recursion-depth bound.
The outer choice has \(\epsilon=1-g\), \(\beta=1-3g\), \(g=10^{-11}\).
The actual BIT stock atom is 1/250. Every ordinary operation, ownership
rectangle and control reservation must remain in the corresponding recipe.
Fixed finite constants determine a new eventual threshold before input
length varies; asymptotic slack cannot justify omitting operations.

The external BIT pin and its own physical/ROW/cover/restoration obligations
are retained separately. None is established by this raw coefficient bound.
