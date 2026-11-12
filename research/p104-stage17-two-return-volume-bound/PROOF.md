# Exact local action and volume

The retained 4,783-event caller places Type B IDLE_ONE on global role 36
with mask {17} at zero-based clocks 4646 and 4660. The eight Type B ports
are 15, 17, 27, 34, 35, 42, 47 and 55. The 13 interior events are rational
ADD and nonzero SCALE on roles 36, 37, 52 and 53. They are independent
of both the central phase and stage-17 body.

Let $M$ be their exact scalar product, let $E$ project onto role 36
and let $x=D_{17}-I$ act on the address coordinates. The old physical
map on the window is $(I+E\otimes x)(M\otimes I)(I+E\otimes x)$.
Normalize by multiplying on the left by $M^{-1}\otimes I$. With
$F=M^{-1}EM$, the remaining product is $(I+F\otimes x)(I+E\otimes x)$.
The exact matrix product gives $M_{00}=(M^{-1})_{00}=0$.
Consequently $EF=FE=0$, so the normalized required map is
$I+(E+F)\otimes(D_{17}-I)$. The idempotent $P=E+F$ has trace and
rank two. This identity retains the two arbitrary dirty input directions.

The #7113 physical binding allocates eight disjoint stage axes to
each even IDLE_ONE, here zero-based axes 137 through 144. Its literal
binary gate is the symmetric matrix $C$ with diagonal $(1+i)/2$ and
off-diagonal $(1-i)/2$. The Walsh vectors $(1,1)$ and $(1,-1)$ have
eigenvalues 1 and $i$. At column multiplicity $f$, $D_{17}$ acts as
$C^{\otimes 8f}$ on the active axes and identity on all spectators.
At width one with one spectator bit the exact modes per lane are 144,
128, 112 and 128 for $1,i,-1,-i$. There are 368 displaced directions
in each 512-column lane and 736 across the two independent lanes.

For every integer $f\ge1$, the identity class fraction is
$1/4+2^{-4f-1}$. The roots-of-unity filter on the binomial weights gives
$2^{8f-2}+2^{4f-1}$ identity modes among $2^{8f}$, and spectator factors
cancel in the fraction. Thus the required displacement has rank
$2(3/4-2^{-4f-1})V\ge(23/16)V$ for lane dimension $V$, using rank
multiplicativity for $P\otimes(D_{17}-I)$.
This uses the actual body against the fixed erased ordinary window.

## Necessary price

Specify one body-dependent core $K$ on one field of dimension $V'$, with
body-independent linear maps $A,B$ and bypass unchanged on erasure. After
normalizing the old window, setting $K=I$ must give the identity.
The added action is $B(K-I)A$ and has rank at most $V'$, including
if the maps mix dirty lanes or spectator coordinates. Restoration and
ownership requirements can only narrow this class. Therefore
$V'/V\ge23/16$. The capacity bound is valid without a specific
core spectrum.

At the same per-coordinate representation, the conditional tariff
in #7397 charges $8(V'/V)H_{16}$ across the eight ports against
removed charge $16H_8$, with $H_r=r^{1-\kappa}$. The affordability
ratio is $2H_8/H_{16}=2^\kappa$. The exact directed interval at
the old crossing bounds it above by 1.003 and gives the stated raw
delta upper before any ancillary charges. The exclusion extends
throughout the retained BIT ceiling since $\kappa\le0.00376669<1/2$
and $2^{1/2}<23/16$, the latter by squaring. Higher charged ranks
can only increase the price for the same field volume in this range.
The other paid and productive jobs are fixed.

For the additional canonical same-width rank-16 tensor model with a
fourth-root global phase and any signed independent axes, the maximum
core displacement fraction is at most $3/4+2^{-8f-1}$. The smallest
eigenphase class has fraction $1/4-2^{-8f-1}$. Sign reversal and
fourth-root phase only permute the classes. The resulting necessary
ratio is at least $736/385$ for $f\ge1$ and its lower bound tends to
two with $f$. The rank-16 price gate uses the weaker arbitrary-core bound.

A changed erased action, another body-dependent bypass, or a shared
provider with a different charged output dimension or tariff lies
outside these hypotheses. No edited caller or provider is claimed.
