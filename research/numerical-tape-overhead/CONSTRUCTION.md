# One fixed multiplier at every input length

The input is one tape holding two equally long most-significant-first words separated by one delimiter. Leading zeroes count toward the length. A fresh tape receives exactly $2n$ most-significant-first product bits from position zero. Blank cells outside the result remain blank. The alphabet, tape count and control are fixed. Each transition reads all scanned symbols, writes at each head, and moves each head by at most one. Space is the union of absolute tape positions through halt. [Original model](OAI/Computability/IntegerMultiplication/TMModel.lean) · [Output specification](OAI/Computability/NearSquareRoot/Specification.lean) · [Visited cells](OAI/Computability/NearSquareRoot/VisitedCells.lean)

## From the adaptive rate to the numerical bound

The [adaptive-interchange derivation](proof/adaptive-rate.md) derives the logarithmic overhead from the width recurrence, pays for the selected Walsh layer and substitutes both costs into the integer caller. The calculation below fixes the machine parameters, prices its modular Walsh implementation and covers every input branch.

## Dispatcher and correctness

1. Measure $n$ on the first word and return home. For $n\le2^{48}$ use the 19-state schoolbook multiplier. Its raw input test, arithmetic and fresh output fit $4096n^2$ transitions, including $4096$ at $n=1$. [Rule and bound](proof/schoolbook.md)
2. Otherwise let $d=\lceil\log_2 n\rceil$, $h=\lceil n/d\rceil$, $k=\lceil\log_2(4h)\rceil$, and $N=2^k$. Represent each operand in $h$ base-$2^d$ digits. If $k<2^{4096}$, use two forward dyadic Fourier transforms, a pointwise product in common bit-reversed order, and the reverse schedule for the adjoint. The precision, normalization, carry and readout count all three transforms. [Dyadic word operations](proof/address-dyadic-words.md) · [Caller and accuracy](proof/address-dyadic-caller.md)
3. For $k\ge2^{4096}$, construct the coprime short axes and map digit addresses into their box by CRT. Its cyclic length is at least $2h$, so the linear convolution fits. Apply two normalized forward transforms, the pointwise multiplication, the adjoint, inverse CRT, nearest-integer recovery, carries and readout. The total error at recovery is below $1/4$. For each Walsh layer put $X=\lceil\log_2(k+2)\rceil$. Use integral butterflies below $X=2^{24}$ and the aligned-modulus adaptive program from equality onward. Use root degree $R=240$ for every native interchange. The degree choices, finite search and stopping rules depend on widths. The estimates below are never computed by the machine. [Axis selection](proof/address-axis-window.md) · [Outer layers, precision and readout](proof/outer-layers.md) · [Walsh arithmetic](proof/walsh-node.md) · [Carry on tape](proof/recount-carry.md)

## Time on the three branches

Write $\ell=\log_2n$, $t=\log_2\ell$, $b=\lceil\log_2(2k)\rceil$ and $\Phi(u)=(u^2\log_2(u+2))^{1/3}$. When $n>2^{48}$, the natural-number packing gives $32\le k\le\ell<2k$, $Nk\le8n$, and $b,X\le t+2$. The looser $Nk\le16n$ suffices for the time calculation. [Packing proof](S008/Packing.lean) · [Logarithm and rounding proofs](S008/IntegerBounds.lean)

| Branch | Written bound used by the all-input implication |
|---|---|
| Schoolbook | $T\le4096n^2\le2^{60}n$ |
| Dyadic | $T\le2^{61}nk^2\le n\sqrt\ell\,2^{61+(3/2)t}$ |
| Coprime | $T\le n\sqrt\ell\,2^{182+4\log_2(t+2)+(499/8)\Phi(t+2)}$ |

The native induction charges the actual children, including full reserves and repeated calls. Its three decreasing slopes bound the native contribution by $(433/8)\Phi$. Pricing column maps at their occupied child width $f$, with $f/a\le1/(2m)$ at parent width $a$ and arity $m$, adds $(33/4)\Phi$. The sum is $(499/8)\Phi$. Ordinary work and contracted children fit this bound. The finite catalogue search also fits at the stated guard. [Child volumes](proof/child-volume.md) · [Local cost and return](proof/node-root-parameter.md) · [All-width induction and finite search](proof/address-native-staircase.md)

Here is the whole coprime calculation. There are three transforms of at most $2^{29}b$ layers apiece. A complete selected Walsh layer costs at most $2^{18}A_W bNk\sqrt{k}\,2^{G(X)}$, where $A_W=2^{110}(1+5120)$. The complete permutations, the three CRT maps and phase, pointwise, scaling and output work sum with the Walsh layers to at most $2^{55}A_W b^4Nk\sqrt{k}\,2^{G(X)}$. The additive construction terms are absorbed using $k^{1200}\le2^k$ on this branch. One may take $G(X)=(499/8)\Phi(X)$ for the all-length claim. Bounding $5121<2^{13}$ and $Nk\le16n$ yields $55+110+13+4=182$. [Permutation and CRT costs](proof/routing-outer-permutations.md) · [Remaining arithmetic](proof/outer-layers.md) · [Combined layer bound](proof/routing-refined-walsh.md)

For the middle range $5\le t<4097$, split at $64$ to bound its normalized exponent by $63\Phi(t)$. For the coprime range $t\ge4096$, use $\Phi(t+2)\le\Phi(t)+2$, $4\log_2(t+2)\le\Phi(t)/12$, and $\Phi(t)\ge576$. The slack obeys $(63-499/8-1/12)576\ge182+2(499/8)+1$. On the raw branch $x=\log_2(1+\ell)\ge1$ when $n\ge2$. Taking $L=1+\ell$ and using monotonicity gives $T(n)\le n\sqrt L\,2^{63\Phi(x)}$ across all three branches. The physical branch bounds are the three hypotheses of the formal implication. [Branch arithmetic](S008/ThreeSlope.lean) · [All-input theorem](S008/InputClock63.lean)

## Cumulative space

The raw and dyadic proofs bound fixed marked banks through halt. For the coprime program use separate routing families for outer and Walsh calls, with maximum incoming volumes $1024Nk$ and $100Nk$. Each family uses at most $399969$ cells per unit of its maximum, plus its polynomial control allowance. The remaining banks, stacks, inactive heads and both polynomial allowances fit $2^{22}Nk$. Fixed head origins allow the union over every invocation to be bounded separately on each tape, including when different calls realize different maxima. Thus $S\le[399969(1024+100)+2^{22}]Nk=453759460Nk\le2^{32}n$. The Lean compaction proof establishes this kind of union for the occupied wrappers. The physical intervals of the complete machine are identified in the written space calculation. [Per-head calculation](proof/routing-outer-space.md) · [Repeated calls](S008/CallLedger.lean) · [Final numeric comparison](S008/IntegerBounds.lean)

## Fixed exponents

Tightening the same large-input analysis gives $2T\le n\sqrt\ell\,2^{60\Phi(t)}$ for $t\ge1{,}572{,}864{,}480$. The integer search in the README forces $60\Phi(t)\le t/q$. Its extra factor two pays for replacing $\log_2 n$ by $\ln n$ with leading coefficient one. For $q=1000$, using the true bit length of the labels at each width and retaining the maximum across previous widths gives a smaller cutoff. The winning width is earlier than the input width. Two exact calculations isolate the crossing and a density proof covers every later input, even after further degree changes. [General formula](proof/all-exponents.md) · [Coefficient 60](proof/profile-limit.md) · [Worked cutoff](proof/routing-label-walsh.md)
