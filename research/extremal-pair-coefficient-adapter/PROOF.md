# Four direct encoded calls produce the selected extremal coefficient tables

## 1. Precise interface and inherited primitive

This is a source-bound adapter, not a new exponential algorithm. It calls the unchanged canonical `research/physical-gaussian-core/gaussian_exponentials.py` at base `e54523517d0f03e58352e647c403a5af3e525a57` (blob `8f0f32d7090554b47c112142e300c88fb8e5db4d`). The scalar contract is the #6085 theorem, retained exactly as `inputs/SCALAR-PROOF.md`, from `research/encoded-gaussian-directed-coefficient-audit/PROOF.md`. Runtime bytes and their nested source archives are pinned in `RUNTIME-PINS.json`.

The adapter borrows six canonical binary `Count` values `(p,alpha,s1,t1,s2,t2)`, each with its head at the canonical origin 1. It admits

    p>=1, alpha>=1, 1<s_l<t_l<2s_l, alpha^2<=4p.          (1)

The final guard ensures polynomial cost in p and input bit lengths even on this broader producer domain. The simplified total-storage and retirement bill below assumes a fresh fixed private scratch cohort, or an explicit O(p+B) entry-history bound on each private role. Reused blank roles retain their earlier history term as specified in section4. Primality and the retained choice of alpha are caller premises for the later A12 specialization, not silently checked by this adapter.

The successful return owns nine distinct `Count` values: precision `P=p+8`, then eight row-major numerator records for two two-by-two tables, each on denominator `2^P`. Its rows are `[2^P,L_(l,+)]` and `[L_(l,-),2^P]`. All six borrowed inputs are unchanged and their heads return to 1. Output heads also return to 1. The caller must keep these nine owners live while using the tables and explicitly retire them afterward; private setup is already closed. No `pool.empty` claim is made before output retirement.

The unchanged scalar theorem states: for integers P,F>=1 and rational `0<=f<=F`, `Exponentials.grid_interval` returns integer endpoints l,u enclosing `exp(-pi f)` on the `2^-P` grid, with `u-l<=2`. `coefficient` returns l with

    0 <= l 2^-P <= exp(-pi f),
    exp(-pi f)-l 2^-P < 2*2^-P.                         (2)

This is a downward approximation, not necessarily the exact irrational floor. Its Machin pi bounds, directed Taylor recurrence, squaring, reciprocal and target rounding are predecessor work. No Axis or ProductionPlan contract is required for an isolated scalar call.

## 2. The four actual arguments and output accuracy

The adapter forms `u=alpha^2`, `delta_l=t_l-s_l`,

    A_l=2delta_l+1, B_l=2s_l-1,
    f_(l,+)=u A_l/s_l, f_(l,-)=u B_l/s_l,
    F=2u, P=p+8.                                       (3)

For integral `1<s<t<2s`, `1<=delta<=s-1`, so `0<A,B<2s`. All four arguments are therefore strictly between zero and F. The code prepares one shared `Exponentials(P,F)` and calls `coefficient(argument,False,None)` exactly four times, in the order plus/minus for axis 1, then plus/minus for axis 2. Thus the sign is decay and the binary scale is zero.

Each rational owns a signed nonnegative numerator `Count.product(u,A)` or `Count.product(u,B)` and a copied denominator `Count(s)`. It explicitly uses the existing `Rational(...,reduce=False)` ABI. No gcd is performed or treated as free. The exact rational representation need not be reduced. The argument is retired after its scalar call; the returned lower endpoint becomes an output owner. Four separately owned `power_two(P)` values supply the exact diagonal ones. A separate `Count(P)` copy supplies the returned grid description.

By (2), every off-diagonal table entry has absolute error

    < 2^(-p-7),                                         (4)

relative to `exp(-pi alpha^2 A_l/s_l)` or `exp(-pi alpha^2 B_l/s_l)`. The diagonals are exact. The alpha square, denominator, phase numerator, sign, scalar scale, table order and target grid are all bound to the actual calls, rather than inferred only from the final numerical values.

## 3. Composition with the actual extremal source pair

The published A12 theorem is pinned at `702c7616667c5f4e583eb73687944d148b7a1ccf`, proof `03da374ebde2644b883b2398e80112989719c2a0edb7394cc43b2abd26fa447c`, retained as `inputs/A12-PROOF.md`. Its source hypotheses are `p>=4096`, distinct odd `s_l>=p^4`, dyadic targets in the retained fine interval, and

    alpha=ceil(sqrt((4/pi)ln(16p))), a=pi alpha^2.

At the unique centered source phase `s_l beta_i=-(s_l-1)/2`, the literal unrounded, alias-deleted, already column-normalized coefficient pair is exactly the two-by-two matrix from (3). Its nonwrapping index is the paid A12 modular-inverse selector; this adapter produces its coefficient tables, not payload routing or source-index traversal.

A12 proves `a<=9ln(16p)<=9p/8`, so `alpha^2<4p`: the producer guard (1) adds no restriction to the admitted A12 family. Set `w=exp(-2a)`. Since `w^2>=(16p)^-36`, for `p>=4096`,

    2^(-p-7) <= 2^-37 w^2.                              (5)

Indeed it suffices that `p>=30+36log2(16p)`, true at4096 and increasing thereafter by the same elementary logarithm bound used in A12. Thus the emitted tables meet the alias-deleted factor error premise with ample room.

The exact matched periodic source is `N_source(j,k)=sum_m G_(j,k+ms)`, as defined in `BILATERAL-LDU.md`, section4. For the selected adjacent pair, A12 bounds the omitted aliases by `4exp(-a t^2/8)`. The same proof gives the slightly stronger constant

    4exp(-a t^2/8) <= 2^-37 w^2,                         (6)

because `t>=32`, `a>=1` and `a(t^2/8-4)>=124>39ln2`. No aliases are computed. Equations (4)-(6) prove that the produced factor tables differ from the selected principal sections of this exact `N_source` by **less than `2^-36 w^2` per entry**, including their diagonals. The alias error is included, not discarded.

This is exactly A12's sufficient further-table-error contract for the matched periodic sections. Hence the tensor of the produced tables and its own exact inverse have full ordinary Stein displacement rank in every one of the24 vertex orders, with A12's retained quantitative margins. It is not a principal section of the full source inverse. A separate inversion algorithm, tensor materialization, application to payloads, transport and complete caller are not supplied for free.

The production theorem #6099 is not used: its incompatible fine-gap admission guards are bypassed only by these four direct scalar calls, not repaired globally. The new result closes the named entry-table production premise at this deterministic fixed two-axis interface, conditional on the retained scalar theorem and encoded arithmetic contract. It does not create a full Gaussian producer or discharge all analytic-recovery assumptions.

## 4. Complete polynomial bit and storage bill

Let B be the maximum bit length of the six input integers. It cannot be removed merely from A12's lower bound `s_l>=p^4`. Before the guard, computing `alpha^2` costs `O(B^2)` schoolbook bit work and `O(B)` bits. On accepted inputs, `u<=4p`, and each rational numerator in (3) has at most `2B+3` bits; the denominator has at most B bits. Thus the scalar argument length `B_f` is `O(B+log p)`, in particular `O(B)` with this definition of B.

The unchanged scalar policy is

    X=4F, k=ceil(log2(8(X+1))), H0=P+X+k+16,
    c=ceil(log2 H0), R=P+4X+4k+2c+64.                    (7)

Since `F=2u<=8p`, we have `X<=32p`, `k<=ceil(log2p)+9`, `H0<=67p`, and `c<=ceil(log2p)+7`. Therefore

    R <=129p+6ceil(log2p)+122 <=257p.                    (8)

The predecessor's paid preparation/application tariff is `O(R^3+(R+B_f)^2)` for sigma0. It includes the directed scalar arithmetic and scans; there is no unbounded final binary shift here. One shared setup and four applications give only a constant multiple of that bound. Argument products, input copies/comparisons, exact denominator copies and table construction add `O((p+B)^2)`; no gcd is hidden. Four diagonal fields and four coefficient fields contain `O(P)=O(p)` numerical output bits, plus the precision record.

Numerical carriers in the scalar routine have `O(R+B_f)` bits, including argument/pi products, directed Taylor endpoints, squaring products and Machin powers. There are only constantly many live carriers at each step; earlier term carriers are closed. The nine returned carriers remain live. On a fresh fixed private cohort, every physical role starts with only its LEFT marker. Its complete history during this invocation is therefore `O(R+B)`; role reuse does not multiply that maximum by the number of iterations. Complete private setup retirement and later caller output retirement or full-history transport are charged at `O(R+B)` per constant-number owner, not merely by a shorter final payload. All fixed bookkeeping and argument formation fit the displayed bound.

For an arbitrary reused blank cohort, let `H_tau` be each role's entry history. Retained physical storage instead keeps the explicit sum `sum_tau max(H_tau,C(R+B))` for a fixed sufficient C. The unchanged `Tape.clear` clears the current nonblank prefix up to the first BLANK, then rewinds; it does not erase the existence of a longer already-blank tail. A caller requiring a full-history sweep or transport must pay its actual history length. No H-free total-storage or full-history retirement bound is asserted for arbitrary reused grants. The numerical/source-error contract and successful blank-prefix restoration remain the same.

With fresh private grants (or the stated bounded-entry-history premise), the complete local bill is therefore

    time O(p^3+(p+B)^2), storage O(p+B),                  (9)

including returned outputs and ordinary owner-history costs. The caller's input storage is read-only. If the separate full fine-source interface supplies `B=O(p)`, one may simplify time to `O(p^3)`; that upper bound on B is not inferred from the local lower-size guard. This is the retained encoded Count/Rational setup model with elementary bit tariffs, not a newly compiled native ROM or a leading complete-multiplication cost.

## 5. State, verification and remaining boundaries

All input Count heads enter at1 and return there. The code never decodes a payload integer into the host: only fixed program literals1,2,4,8, fixed two-axis iteration and retained encoded operations are used. The input bodies remain unchanged. Private F/P and scalar fields stay alive until all calls finish; scalar fields close before their borrowed F/P. The returned precision is a separate owned copy. `Tables.close` retires those nine outputs; `pool.empty` is legal only after every other live lease in that pool has also been released by its owner. Borrowed inputs may remain live in the same pool and are preserved. Normal guard rejections after valid input construction close private carriers and preserve inputs. No arbitrary malformed-tape, allocation-fault or asynchronous-interruption rollback contract is claimed.

The bounded replay creates its six borrowed inputs outside the installed private pool; its observation of exactly nine live pool owners is specific to that fixture. It uses the unchanged source loaders and exact archives under `sealed_constructors` and `no_decode`. Observer snapshots are decoded only after protected calls return. A retained independent-algorithm oracle uses arcsine pi and alternating decay rather than the source Machin/positive-Taylor path. It must be entirely enclosed by each actual scalar interval. The replay also checks all four argument records, the complete row-major outputs, nine distinct live output owners, borrowed bytes/head returns, post-retirement blank history and domain-guard controls. This is corroboration of the quantified proof, not a claim to have run the p>=4096 instance.

The small admitted producer packet deliberately does not meet A12's asymptotic margin domain: some correctly approximated small coefficients round to zero. Its production success is not a rank certificate. Primality, exact retained alpha admission, actual index routing, arbitrary phases, larger dimensions, source inverse sections, complete supplier integration and all five foundational assumptions remain separately scoped. No new kappa is claimed.
