# Five-qubit canonical decoder denominators grow at 136 bits per unit of odd width

For the full five-qubit Clifford alphabet, let $D_f$ be the least positive odd integer clearing the coefficients of the raw Moore–Penrose decoder over the Gaussian dyadics. At every odd tensor width $f\ge15$, a rational class-function calculation gives $D_f$ exactly. As the odd widths increase,
$$
\log_2 D_f=136(f-1)+O(1).
$$
The proof identifies 113 distinct degree-ten spectral polynomials whose polynomial LCM has degree 272. It also proves that $D_f$ divided by the absolute value of this polynomial at its prescribed signed power of two is eventually periodic. [Proof](PROOF.md) · [LCM certificate](check_growth.py)

At the first admissible width, $D_{15}$ is the following 115-digit integer. One entry of the inverse Gram matrix at $S^{\otimes4}\otimes I$ certifies all its odd factors, where $S=\mathrm{diag}(1,i)$. An exact left inverse with optimal noise norm can instead have least odd denominator **394,477,183,485**. These results use the width-15 splitting of #7810. [Single-gate certificate](check_phase.py) · [Sharp splitting](https://github.com/apoursh/integer-mult-bounds/blob/9cdeb734ea8d0e6ddf3914dd92b6ced5046a6910/research/clifford-five-qubit-modular-seed/PROOF.md)

~~~text
3893475211724344589772283104450359211356271788394430137298138320180684819953076729962451809990220934288705085671875
~~~

$T_f$ is the odd part of the LCM of the raw Gram eigenvalues. The diagonal deficit is $D_f$ divided by the odd denominator of an inverse Gram diagonal entry. The last column lists all one-based ordinary ATLAS class indices on which a nonzero-trace lift attains the complete denominator in a single inverse Gram entry. The pair consisting of the identity and a one-qubit phase gate attains it at width 23.

| Width | Digits in $D_f$ | $D_f/T_f$ | Diagonal deficit | Single-entry classes |
|---:|---:|---:|---:|---|
| 15 | 115 | 127,575 | 39 | 7, 36, 41, 55 |
| 17 | 198 | 414,315 | 295 | 11, 37, 38 |
| 19 | 280 | 14,175 | 1 | 1 |
| 21 | 340 | 2,168,775 | 121 | 38 |
| 23 | 436 | 23,856,525 | 767 | None |

## Verification

From the repository root run the registered CPython 3.12 checks. The primary program verifies rational character orthogonality, computes the denominator on every class and can print the exact integer at another odd width. A second program uses the separately published #7806 projection and the single involution column for a matching upper and lower bound at 15. A third computes the polynomial LCM over the integers and certifies its 2-adic behavior. The registered replay uses only the Python standard library.

~~~sh
python3.12 -B scripts/research_package.py --package research/clifford-canonical-class-denominators
python3.12 -I -B research/clifford-canonical-class-denominators/verify.py --width 25
~~~

The numerical character packet sums and the one involution column can be regenerated with GAP 4.14.0 and CTblLib 1.3.11. From this package run the following commands. The last calculation independently obtains the fixed-space function from the two actions on quadratic refinements, constructs the nonnegative integral $192\times192$ convolution matrix and solves its rational system with an exact residual check. These optional routines were run during preparation. [Derived packet data](PACKETS.json) · [Group-table reference](https://www.math.rwth-aachen.de/~Thomas.Breuer/ctbllib/ctbltoc/data/S10%282%29.html) · [Archive and predecessor pins](SOURCE-PINS.json)

~~~sh
gap -r -T -A -q -b export_classes.g > /tmp/five-qubit-ordinary-classes.json
python3.12 -I -B verify.py --gap /tmp/five-qubit-ordinary-classes.json
gap -r -T -A -q -b solve_convolution.g
~~~

## Open next questions

What is the least eventual period of $D_f/|P(t_f)|$? The proof bounds the integer gcd by a Bézout constant without computing its minimal value. One can begin by isolating the odd resultant primes at which the short factors have common roots at powers of two, then test the class-kernel numerators at those primes.

Can a physically specified interface use the much smaller noise-optimal denominator? Start with the bottom eigenspace at width 15 and a costed evaluator for one row of an exact left inverse. A common denominator gives neither a division schedule nor an input-acquisition budget.

## Credit

The ordinary table is due to the ATLAS of Finite Groups and distributed in Thomas Breuer's GAP Character Table Library. Its original distribution retains its license. The source line includes Ali Romman's odd-width spectral reduction and Nick Petalas's Clifford character projections, apoursh's five-qubit complex threshold and Gaussian-dyadic splitting, and the prior four-qubit canonical and noise-optimal denominator results. The new central-ring reduction, all-width arithmetic law and width-15 phase-gate certificate were prepared by apoursh with substantial OpenAI Codex assistance under Apache-2.0. The selected integer-multiplication bound is unchanged. [Odd-width spectrum](https://github.com/CrocSwap/integer-mult-bounds/pull/7788) · [Four-qubit canonical predecessor](https://github.com/CrocSwap/integer-mult-bounds/pull/7805) · [Research claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19756122)
