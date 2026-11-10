# Exact endpoints for the fixed 48-step exponential

The retained mixed_target_probe.exp_interval accepts 0<=x<1 and computes

    S = sum_(j=0)^48 x^j/j!,
    F = x^49/49!,
    (low, high) = (S, S + F/(1-x/50)).

This package preserves this exact rational pair. The analytic enclosure
argument belongs to the retained engine. The new claim is arithmetic
implementation equivalence and its complete-caller runtime consequence.

Write x=a/b in reduced form, with b>0, and put n=48. Set

    P(a,b) = sum_(j=0)^n a^j b^(n-j) n!/j!,
    D = n! b^n,
    C = (n+1) ((n+2)b-a).

Then S=P/D. Since 0<=a<b, C is strictly positive. Algebra gives

    F/(1-x/(n+2)) = (n+2) a^(n+1) / (D C).

Consequently the exact endpoints are

    low  = P/D,
    high = (P C + (n+2)a^(n+1)) / (D C).

No floor, ceiling, floating point or different remainder is introduced.
Both Fraction constructors reduce exactly, so the numerator/denominator
representations as well as the rational values agree with the source.

integer_exp.py evaluates P by integer Horner steps. Initially p=d=f=1.
For j=n,n-1,...,1, it updates

    d <- b*d,
    f <- j*f,
    p <- a*p + f*d.

After the last iteration, d=b^n and f=n!. The coefficient inserted when
the loop index is j is b^(n-j+1) n!/(j-1)!. The remaining j-1 Horner
multiplications turn it into a^(j-1)b^(n-j+1)n!/(j-1)!, precisely the
j-1 term of P. The initial one supplies a^n. This proves the formula for
P and both returned endpoints for every accepted rational input. Zero
gives P=D=n! and both endpoints one.

The implementation accepts exact ints and Fraction values, rejects booleans
and floats, and imposes a 16,384-bit numerator/denominator capacity. It uses
48 iterations and exponent 49. Intermediate integer bit lengths are bounded
by approximately 49 times the input bit bound plus factorial and addition
bits. This finite capacity bounds mathematical storage, but Python still
allocates managed objects during execution. No fixed-heap claim is made.

# Complete caller substitution

Cinna Davis's unchanged PR4440 verifier loads the separate rational moment
engine through controller.load. The adapter retains that load and changes
only exp_interval in that freshly loaded engine module. The baseline uses
the original function through the same wrapper. All source matrix products,
logarithms, caches, finite words, native checks, rational tail comparisons,
compiler conditions, outer predicates, mutations and complete RESULT.json
comparison remain in place. No scientific assertion or expected artifact
is filtered, replaced or accepted from a prior run.

The endpoint identity above permits substitution at every call. Therefore
the complete caller has the same return value and decisions on every
invocation whose exponential arguments fit the declared domain. The exact
source invocation additionally compares all ordered input/output tuples,
not only their hashes. The compact trace digest length-prefixes signed
binary numerators and positive denominators, avoiding Python's decimal
integer-string limit without changing that process-wide setting.

Source hashes bind the observed complete read/import closure and predecessor
proof/credit. The package verifier authenticates all declared inputs before
loading the caller. Runtime needs no Git, network, predecessor discovery
search or environment installation. Module substitution is local to a fresh
process. It is not a persistent source edit or a thread-safe library API.

The benchmark times a fresh process from launch through completion, including
imports, the full caller, unchanged receipt comparison, trace hashing and
full scientific output serialization. The parent checks exit status, full
scientific output hash, equal call/step counts and equal exact-trace hashes.
It alternates five complete baseline/candidate pairs. A timing threshold is
never an acceptance condition in registered replay.

# Credit and scope

Credit ywz65's PR2552 for the integer Taylor recurrence, exact-arithmetic
optimization method and the explicit question about other retained engines.
Its original ceiling has a variable stopping index, dyadic rounding, a
smaller range and a different remainder. The present fixed 48-step rational
pair and its geometric tail require the formulas above. No priority is
claimed for common-denominator arithmetic or Horner evaluation.

Cinna Davis and the retained mixed-target, zxv, Jacob Alan Sussman, native,
BIT, compiler and outer contributors retain their scientific credit in the
unchanged pinned source proofs and notices. This package does not audit
those mathematical conclusions, admit a supplier, update the selected
frontier or discharge a framework assumption. Local timing is evidence
for one complete caller and environment, not a universal speed guarantee.
