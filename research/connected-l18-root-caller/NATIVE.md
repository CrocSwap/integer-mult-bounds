# Native contract and complete substitution

HOST_Q(x,y,j) must send arbitrary independent inputs simultaneously to
x_out=D_j(x+Qy), y_out=-D_j Q^-1 x, with Q^4=1. This is alpha=1,beta=-1,
t=alpha beta=-1. Sign gauges give the physical endpoint X=x-y,Y=x.
Main transports are X line to full and Y zero to hyperplane. A native must
supply compatible frames and phase maps, restore owned scratch, count every
paid operation and disclose all productive helper targets. No second main
plane or helper is silently discarded. The caller provides none of these
physical obligations. HOST remains an unimplemented supplied macro.

Diagonal gauge sends alpha to r alpha and beta to beta/r, preserving t.
Thus a t=-1/2 native does not become resonant by free scalar rescaling.
Mixing different physical frames also needs a delivered legal word.

| Event | Action on current arbitrary rows | Root price |
|---|---|---|
| ADD d,s,c | r_d += c r_s | ordinary |
| SCALE d,c | r_d *= c | ordinary |
| SWAP d,s | exchange rows | ordinary |
| QUERY d,s,1 | r_d += Q r_s | H1 |
| IDLE_ONE d,[j] | r_d *= D_j | H8 |
| LAMBDA d,s | multiply by ((1+s i)+(1-s i)Q^2)/2 | ordinary, tariff open |
| HOST x,y,j,1,-1 | simultaneous map above | native invoice open |

For p ports, native paid profile Pnative and productive helper profile Thelp,
the full substitution is

    Ttotal = p Troot + 18 Thelp,
    Ptotal = p (181H8+3H1) + 18 Pnative.

H_r contributes r^(1-kappa). Per-port native signed price must be below
(Troot(kappa)-181*8^(1-kappa)-3)/18, before ordinary and outer margins.
COST.json compares selected complex .003125804, pending #6936 .00362701882
and ordinary BIT .00376669. BIT is a benchmark, not automatically a supplier.
At kappa 0 the surplus is 323p-18 mass(Pnative-Thelp).

Direct native bill 2H8+2H1 gives 217H8+39H1: paid mass 1775 versus target 1774.
Target ranks>=9 and paid ranks<=8 imply moment<=-8^(-kappa)<0 for 0<=kappa<1.
This controls that unbundled baseline, not all native constructions.

A second screen is retained F plus an owned rank-one input shear: F sends
X=x,Y=x+y; preceding x<-x-y gives X=x-y,Y=x. It requires owned ascent and
erasure. Source #6833 head 51f54e3c31f2f3a3e056a483b3ed66ae916ad06a,
research/p104-chain-nested-root, retains #6824 native
2a7ca44fbda3abaa4df355b183ed7d7478eef7c1. The #6936 base_invoice profile
prices F+H1 at 17.691442460347425 per port at .00362701882, exceeding the
17.131340902854333 gate. No modified native word is emitted or admitted.

Ordinary caller work is 2,168 events including 80 LAMBDA, with dyadic scalars.
Its coefficient bounds concern this caller and exact HOST only. Native
precision, approximate children, tape, raw tariff and outer margin remain
open. No new κ. No framework assumption or operation admission is removed.

## Scoped limitation of the retained two-plane native

Companion commit93effe2a135bf57b9e484cb630d8dd057159aec9,
`research/shared-wire-split-composition/data/final.json.gz`, has96 type A
ports with endpoint, in order(X1,X2,Y1,Y2),

    M = [[I, diag(0,-1)], [diag(1,0), I]].

Separate exact replay on all1,480 independent public inputs checks this map,
identity helper returns and boundary frames. X1,X2 share one boundary frame;
Y1,Y2 share the other. Allow arbitrary invertible input/output remixes within
each group, a relaxation of actual same-frame operations. The Y-from-Y block
becomes P_Y I Q_Y, hence stays invertible. No nonzero Y output row can become
independent of every Y input. A resonant HOST requires exactly that zero Y
row for its second output, including independence from the unused plane.
Thus these block-diagonal remixes cannot extract the demanded autonomous HOST.

This excludes paid cross-frame operations, helpers, feedback, identified
inputs, cross-port remixes and larger rewrites; it is not a general native
ceiling. The coefficient replay inherits owned-erasure semantics and makes
no new all-width claim. Exact bytes, checker and receipt are retained.
The F-plus-input-shear screen above additionally requires104 dirty erasures,
owned ascent(A6), legal owned lifetimes and ordinary INIT/COPY/ADD/CLEAR work;
its optimistic numerical price omits those ordinary margins.

## Coordinate-role idle merging cannot rescue F+H1

`IDLE-COALESCING.md` fixes the38 coordinate roles and18 masks, allows any two
eligible coordinate hosts per stage, and merges every same-role idle occurrence
for free, even across barriers. Its solver-free exact optimum saves less than
9.707289925176956 per port. The pinned F+H1 profile requires more than
10.08182803487564, leaving a strict gap greater than0.37453810969868 before
ordinary and outer work. This screen excludes arbitrary noncoordinate shared
idle directions, changed encodings, roots, natives or idle counts. In
particular, it does not cover every rotating rank-one basis of E_j-H_j.
