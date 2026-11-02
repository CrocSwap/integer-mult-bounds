# Exact finite exponential evaluation

This contribution is produced by Nick Petalas. Independent human and formal
proof-kernel review are unclaimed. Apache-2.0.

## Statement

For every rational x=a/b with b>0 and 0<=x<=1/4, and every integer n>=1,
let

    S_n(x) = sum_(j=0)^n x^j/j!
    E_n(x) = (x^(n+1)/(n+1)!) / (1-x/(n+2)).

The following integer recurrence returns exactly the interval
`(S_n(x), S_n(x)+E_n(x))` used by ToikY's frozen PR6378 primary verifier.
There is no extra rounding, changed degree or shortened series.

    A = D = 1
    for k = n,n-1,...,1:
        D = b*k*D
        A = D+a*A
    lower = A/D
    tail = a^(n+1)*(n+2) / (D*(n+1)*(b*(n+2)-a))
    return lower, lower+tail

The old A appears on the right of the second assignment; D is its updated
value. The executable accepts Fraction inputs with components of at most
4096 bits and degrees 1..64. The written identity has no component-size or
degree-64 restriction. The bound on x is the source's declared interval.

## Algebraic proof

Before the first iteration, A/D=1. At iteration k, the recurrence replaces
the previous ratio T by `1+(x/k)T`. Downward induction therefore gives,
after iteration k,

    A/D = sum_(j=0)^(n-k+1) ((k-1)!/(k+j-1)!) x^j.

For j=0, the factorial ratio is one. At k=1 this is exactly S_n(x).
The denominator starts at one and is multiplied once by every bk, so its
final value is D=b^n n!. Substitution gives

    (x^(n+1)/(n+1)!) / (1-x/(n+2))
      = a^(n+1)*(n+2) / (D*(n+1)*(b*(n+2)-a)).

The denominator is positive because a<=b/4 and n>=1. This also handles a=0,
where the tail is zero and the lower endpoint is one. Fraction construction
reduces exact integers; it introduces no rounding. Both returned endpoints
are consequently identical rational numbers to the predecessor's outputs.
The classical Taylor and geometric-tail argument, including its use as an
exponential enclosure, belongs to the predecessor and standard analysis.
This contribution proves preservation of that particular enclosure.

## Complete caller preservation

`ORIGINS.json` records sixteen byte-exact retained files from PR6378 at
`4cfe905d84f3720c23a7f155f615222401953f95`. The primary script, its fourteen
frozen inputs and its complete retained result are included. Its original
NOTICE and proof files remain unchanged. No foreign Git object or network
access is needed for replay.

`replay.py` checks the manifest hash, every retained byte count/hash and the
primary script's fixed hash before loading it. It compiles the authenticated
script with a private name, so the script defines its original functions but
does not enter its final CLI block. The integer arm changes only the private
`exp_positive` binding. The source degree is checked to be 24. The adapter
then executes the unchanged final CLI block with its original argument list
and main name. Argument restoration occurs in a finally block.

The sixteen fixed source files authenticate the exact CLI boundary and all
its code. The complete original source/profile/coefficient/kernel identities,
endpoint signs, examples and three counterfactual controls still execute.
The original typed JSON and exact-byte retained-result comparisons still
execute. The baseline arm takes the same path with the original binding.
Neither arm executes the predecessor profile producers or independent tariff
oracle. Their source and receipt authentication is retained exactly where the
primary originally performs it. This is one complete primary command, not
a replay or acceleration of all eight predecessor registered commands.

By the interval identity, each reached replacement result equals its original
result. Induction through the remaining unchanged computations preserves all
values, branches, failures and the final result. The bounded conformance run
also records and compares the complete ordered list of 72 Fraction arguments.
Their largest denominator has 171 bits, inside the explicit backend limit.
The source's degree-24 loop thus has exactly 1728 iterations in this caller.
Those per-term Fraction operations become integer operations. The final
rational interval and every later outward rounding remain unchanged.

## Verification boundary

The verifier compares against a direct power/factorial sum on 1449 finite
cases, separately checks all 72 reached arguments, compares the complete
result bytes, and executes both complete CLIs. Fourteen negative controls
exercise domain/degree/size limits, omitted tails, premature rounding,
manifest/source mutation, read limits and invalid arm selection. Both normal
and optimized Python execute these predicates with explicit exceptions.

This is a written scoped preservation proof with finite corroboration and
measured implementation evidence. It supplies no new root, kappa, scientific
audit of PR6378, native operator, supplier admission or multiplication theorem.
