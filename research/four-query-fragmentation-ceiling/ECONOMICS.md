# Four-query attainability does not improve this complete recursive grammar

Jerry Chen / @CubeJerry, with substantial OpenAI Codex assistance. Apache-2.0.

## Contract and conclusion

Retain the exact native leaves and six-site, two-fragment root of #6726, head `435bbe91fb28cb1d7a569ca70c6c4e9eb302d486`. Allow every binary supplier node to choose either the original three-query macro or a favorable four-query macro with two independent same-orientation auxiliary retirements. Both orientations are allowed independently at every node. Native child contracts, arbitrary independent helper inputs and their productive targets remain unchanged. Each added thin query costs H(1)=1 per port. Every whole idle is paid. All ordinary work is optimistically free in this upper-bound comparison.

For the power tariff H(r)=r^(1-k), the enlarged grammar has the same finite optimum and the same all-size raw ceiling as the ordinary grammar in the retained ranges. The complex ceiling is 0.0033072446849 and the BIT ceiling is 0.0037667234776. These are strict upper bounds on feasible raw moment savings, not newly admitted values. The qualified #6726 values remain 0.00330720 and 0.00376669. No supplier admission or framework assumption is discharged.

The four-query construction can pay locally at huge asymmetry. The proof below uses the complete large-tree tail to exclude those globally losing sizes; it does not claim universal local loss. The checker includes a positive local-gain control at total leaf count 2^400.

## 1. Complete node invoice and fresh inputs

Let s be the native body rank, p the number of ports, and a,b positive child leaf counts. Thus s=8,p=104 for complex and s=7,p=111 for BIT. Put

    i(n)=H(sn+1)-H(sn).

After removing the unchanged child invoices, an ordinary binary node has two productive targets of rank s(a+b)+1, two paid whole idles of rank s(a+b), and one paid thin query. Its signed contribution per port is

    O(a,b)=2i(a+b)-1.

A four-query same-orientation node has four independent productive fields: two of rank sa+1 and two genuinely fresh suffix fields of rank sb. Its paid bill contains two whole idles of rank sa, two whole idles of rank sb, and two thin queries. Consequently

    N(a,b)=2H(sa+1)+2H(sb)-2H(sa)-2H(sb)-2
          =2i(a)-2.

The reverse orientation gives 2i(b)-2. The two plain suffix targets have not been erased from the invoice: their earned moment cancels their equally charged whole idles only after both are counted. The checker keeps the separate target and paid histograms and rejects omitting a suffix idle, omitting fresh productive fields, or omitting the added thin query. A further scope control confirms that making the added query free would break the per-node envelope used below; a cheaper packed-query tariff is therefore not silently included.

The local improvement is 2[i(a)-i(a+b)]-1. It can be positive for huge b. Nevertheless N(a,b)<0 for every a>=1 and 0<k<1, since the strictly concave power increment i(a)<1.

## 2. Complete root and leaf formula

Let ell be the signed native helper moment minus every native paid MOVE, divided by p. The executable independently recounts those ranks from both retained literal native words and their retained frame dimensions. Native semantics and frame validity remain inherited; this is an independent tariff census, not another native physical proof. These are full leaf tariffs, including arbitrary helpers and all source transports; active main outputs are supplied by the assembled caller.

For positive six-child sizes (a,b,c,d,e,f), F=a+b+c+d+e+f, let D(n) be the maximum internal-node contribution over the enlarged binary grammar, excluding native leaves. Then D(1)=0 and

    D(n)=max over a+b=n of D(a)+D(b)
         + max(2i(n)-1, 2i(a)-2, 2i(b)-2).

The complete signed root moment per port is

    F ell + D(a)+D(b)+D(c)+D(d)+D(e)+D(f)
    + H(sF+1) + H(s(a+b+c)+1) + H(s(d+e+f)+1)
    + i(b+c)+i(c)+i(d+e)+i(d)-2.

The verifier extracts the root's target and paid stage subsets from the literal complex and BIT callers. It removes only the explicitly marked binary-node target/idles and their thin queries. Each remaining stage set must be a union of complete child monomials. The resulting formal six-variable signature is checked exactly, including all three root thin queries and six root whole idles. This binds the formula for arbitrary replacement child sizes, rather than merely matching a value at one allocation.

Independently, the checker reconstructs the separate complete histograms at (4,4,1,1,4,4) and matches every retained target and paid count. Complex totals are 13,670 productive fields and 66,852 paid requests; BIT totals are 11,640 and 56,673. It does not import predecessor pricing or optimization functions. The retained rational power-enclosure engine is reused, credited and byte-pinned.

## 3. All-size envelope survives every four-query choice

Set A=2i(2)-1. Throughout the checked ranges A>0. Every ordinary node contributes at most A because i decreases. Every new four-query node contributes less than zero, hence also at most A. A forest of six binary trees with F leaves has F-6 internal nodes, regardless of their choices. Therefore

    sum D(child) <= (F-6)A.

The four root increments are at most 4i(1). Jensen's inequality bounds the two three-child aggregate targets by 2H(sF/2+1). Thus every complete enlarged-grammar invoice is bounded above by

    B(F)=F ell+(F-6)A+4i(1)+H(sF+1)+2H(sF/2+1)-2.

For fixed k this is concave in real F. At the lower endpoints of the ranges, exact outward intervals give:

| Source | k lower | B(50), upper | B'(50), upper |
|---|---:|---:|---:|
| Complex | 0.0033 | -0.859142825481485098976435921006 | -0.050091759861444400601946626349 |
| BIT | 0.0037 | -0.517331251783714291626183397416 | -0.042267506150883358778296073314 |

At the lower endpoint, consequently B(F,lower)<=B(50,lower)+(F-50)B'(50,lower)<0 for every F>=50. The checker also encloses ell's derivative as strictly negative on each whole interval ending at k=0.004. The power moments H(r), r>=1, and increments i(n) decrease with k. Every coefficient in B(F) multiplying those terms is nonnegative for F>=50, so termwise B(F,k)<=B(F,lower). No monotonicity of the F-derivative in k is asserted or required. The negative tail is uniform on [.0033,.004] for complex and [.0037,.004] for BIT.

This is the all-size step. It remains valid even when a very asymmetric four-query node improves its local predecessor, since that node still lies below A and all sufficiently large complete invoices already lose.

## 4. Finite trees and ceilings

For F<50, every child size and node size is below 50. Monotonicity in n and k gives the uniform replacement bound

    2[i(a)-i(a+b)]-1
      <= 2 i_lower(1)-2 i_cap(49)-1 < 0.

The exact upper bounds are -0.965599236356202079922260967058 for complex and -0.968206939832390688762028399831 for BIT. Replacing any four-query node by its ordinary counterpart, with the same children, strictly improves the complete invoice. Repeating removes every such node. Thus the finite enlarged-grammar optimum equals the ordinary optimum; no finite search over the new grammar is being substituted for a proof.

The verifier then performs outward rational interval dynamic programming over every ordered binary split and every positive six-child allocation for F=6 through 49. The exact complete maximum is attained at F=18. At the stated raw ceilings, its upper bounds per port are:

| Source | Raw ceiling | Maximum upper bound |
|---|---:|---:|
| Complex | 0.0033072446849 | -0.000000000101790666829957164467 |
| BIT | 0.0037667234776 | -0.000000000057961037857195053072 |

The negative tail and finite bounds together exclude every size. Monotonicity of ell and the remaining root/node moments extends these exclusions through 0.004. The finite counts alone are not the theorem.

## 5. Limits and inherited obligations

The conclusion grants algebraic legality of the four-query node and even grants its ordinary implementation free. It therefore remains an upper bound if actual routing, phases, adapters, storage, compiler or outer jobs add cost. A raw nonpositive paid/productive margin cannot become a positive margin by retaining those additional charges. No new all-column, compiler, precision-tape or analytic-recovery theorem is asserted. The five assumptions remain `native_all_columns`, `owned_erasure`, `compiler`, `precision_tape`, `analytic_recovery`.

The proof fixes the native leaf contracts and root's formal stage/target signature. It does not cover a changed root, a new native leaf, an additional independent productive target, a cheaper packed-query tariff, sharing that removes billed jobs, nonlocal coupled retirements, or a different nonlinear/operator-valued provider. Those changes require a new complete invoice. The local positive-control regime is preserved expressly so this source-relative economic obstruction is not mistaken for a universal four-query prohibition.

Predecessor credit: #6726 supplies the retained source, two-fragment root, complete invoices and ordinary-tree tail method; #6764 supplies the earlier carefully scoped header/price analysis and the equal-orientation limitation. The contribution here is the complete mixed-grammar dominance/tail proof, independent literal tariff binding, and corresponding BIT all-size application. The new four-query realization is established in [CONSTRUCTION.md](CONSTRUCTION.md), with an independent reverse-functional replay.
