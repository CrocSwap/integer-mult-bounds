# Optimal scalar recursion power within the frozen depth-coarse family

This companion concerns the finite family of 64 complete interchange profiles
obtained by choosing one word in `{c,r}^3` for each of the two axes, h=23 and
h=25. Those letters select row/column regrouping at the **first three internal
weighted-exclusion construction levels**, uniformly across the axis's common
points; deeper levels use columns. This happens before a fixed word is compiled.
It is not arbitrary internal per-node row/column assignment, nor a change to
unit completion or carry exchange. The letters do not represent choices made
at recursion depths of a growing-width interchange invocation. The latter
choices are the subject of the theorem below.

The scalar regrouping comes from eumemic's PR69; the anchored split and paid
compiler come from PR71 and its credited predecessors. This companion proves
a mathematical limitation of adaptive selection among the supplied complete
profiles. It does not claim a record multiplication bound, worldwide novelty,
an unconditional all-size theorem, or optimality over other circuits.

## Fixed profiles and exact selection

For profile j let m=575, W_j be its total physical role divisor, and n_{j,t}
its **complete** positive child multiplicity, including all endpoint copies,
exterior banks, data corners, physical growth and actual axis-profile children.
Every child width satisfies 1<=t<=529<m. An invocation of width e>=m produces
children with width t floor(e/m), each at relative logical volume 1/W_j.
Define

    M_j(alpha) = sum_t (n_{j,t}/W_j)(t/m)^alpha.

These n/W coefficients are relative-volume weights, not probabilities.
In this family M_j(0)>1 and M_j(1)=1-1846900/(575 W_j)<1. Each M_j is strictly
decreasing and has one root alpha_j in (0,1). Write

    alpha_* = min_j alpha_j,       a_* = 1-alpha_*.

The independent arithmetic receipt checks the selected `rcr`/`rrr` profile
below one at its accepted rational saving a, its next saving grid point above
one, and every one of the other 63 profiles above one at a by **lower**
moment bounds. Thus the selected profile has the unique smallest alpha_j.
This certifies the strongest scalar characteristic within this frozen family;
it does not follow merely from comparing W or rank mass.

## A floor-exact adaptive barrier

Assume the inherited complete interchange interfaces for all profiles. Consider
any finite charged recursive tree which chooses one of them at each node,
according to width, depth, orientation, role, previous choices or a random
choice. Each occurrence retains its own relative volume; nonrecursive charges
are nonnegative. At any elementary leaf assume work at least c_0 V e for one
fixed c_0>0. A fixed bounded-width elementary implementation meets this
condition after choosing its fixed constant c_0.

**Theorem.** Every such complete-tree accounting has work at least

    [c_0/(1+D)^alpha_*] V(e+D)^alpha_*,    D=13225/2.

Consequently adaptive profile switching cannot improve the scalar recursion
power beyond the best standalone root in this family.

**Proof.** More generally take D=max_{j,t} tm_j/(m_j-t) for any finite menu.
Here t<=529 and m=575, so D=529*575/(575-529)=13225/2 suffices. For every
legal recursive width,

    t floor(e/m)+D >= (t/m)(e+D),

because floor(e/m)>=e/m-1 and D(1-t/m)>=t. Since alpha_* is positive and
M_j(alpha_*)>=M_j(alpha_j)=1,

    sum_t (n_{j,t}/W_j)[t floor(e/m)+D]^alpha_*
       >= (e+D)^alpha_* M_j(alpha_*) >= (e+D)^alpha_*.

The function e/(e+D)^alpha_* increases on e>0, so for e>=1,

    e >= (e+D)^alpha_* /(1+D)^alpha_*.

This supplies the elementary-leaf lower charge. Every recursive child has
strictly smaller positive integer width. Strong induction, multiplying each
child charge by its actual V/W_j and summing its multiplicity, proves the
bound. Node overhead only adds work. The proof is pointwise for each realized
tree, so randomized selection does not evade it. QED.

This is a bound on the explicit recursive work functional. An upper recurrence
by itself never implies a lower bound on an arbitrary machine's actual runtime.
An algorithm sharing computations between child occurrences, exploiting a
stronger restricted child contract, choosing unbounded input-dependent new
networks, or changing the leaf cost model is outside the theorem.

## Sharpness of this scalar power

For the selected profile alone, the unshifted potential V e^alpha_* does not
increase at a recursive expansion: floors only decrease child widths and its
characteristic equals one. Therefore total elementary-leaf volume is at most
V e^alpha_*, since every positive leaf width is at least one. Let
B_0=sum_t n_t/W>1. Summing volume identities over the whole selected tree gives

    leaf volume = root volume + (B_0-1) total internal-node volume.

Hence the total internal volume is O(V e^alpha_*). Elementary leaves have
width below the fixed m and cost O(their volume). If the nonrecursive charge
of a node is O(its volume times a common polylogarithmic factor), the selected
tree has work O(V e^alpha_* times that factor). Separate setup and tape costs
remain separately charged. Under these hypotheses the optimal scalar power
for this complete-profile family is exactly alpha_*.

Finite tensor compositions have characteristic equal to the product of their
constituent characteristics, so every factor is at least one at alpha_*.
Expanding any such macro into its complete tree gives the same obstruction.
The result does not extend to new unbounded network families.

## Typed recursion and the balanced assembly ceiling

Merely adding orientation tags cannot improve the root if every type has this
same complete child histogram. Its nonnegative matrix characteristic then has
constant row sum M(alpha), so its spectral radius is exactly M(alpha), by the
all-ones eigenvector and the ordinary sup norm. A genuine multitype improvement
needs independently proved cheaper child-operation contracts, with a positive
vector v satisfying A(alpha)v<v; the existing generic contract does not supply
that improvement automatically.

The inherited balanced assembly requires kappa<min(1-epsilon,epsilon q) and
q<a_b. Balancing the two expressions at epsilon=1/(1+q) gives the existing
strict scoped ceiling kappa<a_b/(1+a_b). Substituting the independently bounded
selected root therefore bounds the complete remaining analytic/parameter
headroom for this finite family. The receipt supplies the exact numerical
enclosure; this ceiling is inherited and is not claimed as a new assembly.

For the frozen selected profile the independently enclosed saving root is
strictly between 0.0000516459365535807612 and 0.0000516459365535807613. Thus this
family's unchanged balanced assembly has strict ceiling

    kappa < 516459365535807613/10000516459365535807613.

Its published finite witness is kappa=5164326938841/100000000000000000.
The entire remaining analytic/parameter headroom within these hypotheses is
less than 1.565e-16 in absolute saving. This says nothing about a stronger
construction outside the frozen 64-profile family.

The all-size residual compiler, row/remainder handling, finite-alphabet tape
simulation, analytic transfer, routing, address primes, setup, precision and
exact-recovery contracts remain explicit hypotheses. Finite word/profile replay
and the rational comparisons establish their respective finite layers, not
these complete all-size theorem dependencies.
