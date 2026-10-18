# Capacity and packing proof

## 1. Quantized observations

Let X be a finite input set and T_p:X -> R^m any deterministic map. Neither
linearity, continuity nor a computational bound is assumed. Each component
belongs to2^-(p+g) Z and has absolute value at most R*2^-p, for integers p,g>=0
and R>=0. A separate record h_p(x) has at most D states. The decoder receives
only(T_p(x),h_p(x)) and input-independent parameters including p.

Each component's integer numerator lies in[-R*2^g,R*2^g], so has at most
K=2 floor(R*2^g)+1 values. The complete record has at most C=D*K^m states,
regardless of dependencies. Branch-dependent use of a fixed tuple is allowed
if the branch is counted in h and absent slots are padded with0. No uncounted
branch information or extra source observation is free.

If the demanded real quantity a(x) has N distinct values, exact reconstruction
requires C>=N by pigeonhole. If N inputs have pairwise demands more than
2 epsilon apart, recovery within epsilon on every input also requires C>=N:
two equal transcripts produce the same decoder output, which cannot belong
to both disjoint closed epsilon balls. This applies to arbitrary nonlinear
decoders under deterministic worst-case correctness. Randomized average-error
guarantees are not claimed. The same proof permits p-dependent m,R,g,D.

## 2. Actual bounded dyadic line

Use PR2384's exact four-pair QQ16 model, owner action and66-port set. Put
f_b(d)=bit_0(db), which is0 or1 at every owner. Its ordinary witness has
h44=-f25, h49=-f145, h58=-f4, h70=f4, with every other component0.
Let H=B0 h and P_A be the actual selected injection R_A^T/4 including its
owner routes. Define w by X_U=h,Y_U=0,X_A=-P_A H,Y_A=P_A H, all other fields0.
The pinned proof establishes H!=0, B_s h=0 for s=1..8, and the complete zero
observation trace for the fixed19events. Function-dictionary cancellation
proves identities at every owner without assuming bit-function independence.
Payload-constant fields remove translation dependence at any fixed depth.

Set v=2w. The verifier derives its original selected X_A components as

    f145-f4, f145-f25, f4-f25, 0,
    f145-f4, f25-f145, f25-f4, 0.

Y_A is their negative; ordinary nonzero components are twice signed bit
functions. Hence v is integer-valued and ||v||_infinity<=2. At the identity
owner the first original X_A component is1. The granted exact observations
of tv vanish for every real t by linearity of the retained logical schedule.
Homogeneous selected controllers also receive zero exact fields. The rounded
claim still requires their whole retained transcript to obey the stated error
and capacity contract; unbounded internal state is not free.

For p>=1, take t_k=k*2^-p,0<=k<=2^(p-1). All x_k=t_k v are p-grid inputs
in the unit box. Their demanded coordinate is t_k, giving
N_exact=2^(p-1)+1 distinct values. For p>=3 restrict k to multiples of4.
This gives N_ulp=2^(p-3)+1 inputs with demand spacing4*2^-p>2*2^-p.
One-ulp approximate recovery therefore requires N_ulp transcript states;
exact recovery requires N_exact.

## 3. The entire declared tuple

Let W be the finite number of owner/payload points at the chosen depth. No
estimate of W is required because the source identities hold at every point.
The initial S values are zero: h is supported on four unread ports. They
contribute4*2*66=528 complex slots per point. After each of19events, all
4*2*16=128 selected A/T values and all528 S values vanish. After event1(B1)
through event18, all4*96=384 completed-X ordinary descendants vanish at18cuts.
At terminal event18 the completed-X side becomes Y, so that side is observed;
former-Y final X is excluded. All five eight-component forward histories are
zero, adding40slots. The overgranted tuple thus has
(528+19*656+18*384+40)W=19944W complex, or m=39888W real components.
Duplicated slots can only decrease its capacity.

Let T_p be any rounded/nonlinear implementation of this tuple whose components
are on the(p+g(p))-grid and differ from their ideals by at most R(p)*2^-p.
Include every other retained scalar/metadata value in these components or a
record with at most D_p states. The ideal tuple is zero on our line, so
section1 proves the README inequalities. The conclusion is independent of
the arithmetic that produces the residues. This is a necessary interface
condition, not proof of any particular implementation's R,g,D bounds.

## 4. Eventual failure and deliberate escapes

For fixed W, polynomial R(p), g(p)=O(log p) and log2(D_p)=o(p), we have
log2(C_p)=o(p), while log2(N_ulp)>=p-3. Eventually C_p<N_ulp. More generally
the sufficient obstruction is exactly

    log2(D_p)+m(p)*log2(2 floor(R(p)*2^g(p))+1) < log2(N_ulp).

There is no inference when this inequality fails. Fixed-depth asymptotics
alone do not reject a coupled depth=depth(p), and no useful small-p threshold
is claimed.

Finer quantization is a real escape: F_p(t)=2^-p*t is injective on our line
and belongs to the2p-grid, although |F_p(t)|<=2^-p/2 relative to ideal0.
Here g=p supplies enough states. Likewise T_p=0 plus h_p(t_k)=k is injective
when D_p is large enough. Early original-A observation detects t directly.
These controls demonstrate why small absolute error or an exact kernel alone
does not establish this conclusion. No physical cost is claimed for escapes.
