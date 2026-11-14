# Independent source counts and meter partition for the combined current arithmetic join

Status: PASS for the original-source obligations below. Final source/binder/cost close is recorded in REVIEW.md and JOIN-RESULT.json against proof3167e192. C independently reviews graph semantics and ownership.

## Exact original source

The checker imports only the four pinned original files: current producer88dab4ca…, inverse producer6acdebee…, Words5c37f577… and records0c9c4b23…. It does not import B12 arithmetic, binder, interpreter, primary checker or oracle. Each producer has exactly16 raw call sites, with method alphabet compare/add/subtract_exact/divmod. The finite subtract_exact wrapper delegates to subtract. After replacing divmod, shift_add_bit and its nested compare/subtract calls are no longer a live provider path. No Ring, times_small or increment_in_place is called by this producer's reached methods. Fault-only source paths are excluded by fault=None.

## Universal workload derivation

Each modular addition uses one raw add, one compare and at most one subtract. Each modular subtraction uses one compare and either one subtract or one add followed by one subtract. Both cost at most3 nondivision raw calls. A modular multiplication executes P doublings and at most P conditional additions, so at most6P. A full product executes P doublings and at most P conditional raw additions, so at most2P.

Let E be the total Euclidean loop count, m/t the left/right record counts and v the valid right-coordinate count. Every Euclidean iteration adds one modular multiplication and one modular subtraction, at most6P+3 calls, and two divisions: r0/r1 and quotient/modulus. The inverse's terminal unit comparison is counted per record.

A left record adds admit/value/unit comparisons3, the scaled modular multiply6P, adjustment subtraction3, two full products4P and reconstruction add1. This is10P+7. A right record adds admit/unit/value comparisons3, offset multiplication6P, its valid coordinate add/subtract3 and one full product2P. This is8P+6. Short-circuit invalid-left and padded-right paths can only reduce the count. Therefore

    H <= (6P+3)E + m(10P+7) + t(8P+6).
    J = 3m+2t+v+2E.

Every two Euclidean steps reduce the larger positive remainder by more than a factor2; all remainders are below the initial modulus<2^(P-1). The retained loose e_i<=2P+1 bound therefore holds. Since each modulus>=2 and the complete product<2^(P-1), m+t<=P-2. Substitution gives H <=(P-2)(12P²+22P+10)<12(P+2)^3 and J <=(P-2)(4P+5).

A literal simple-call bound must still be proved from the final graph. If the declared conservative8192(P+2) bound holds, the new subset costs at most89+J(930P²+1395P+14322)+8192(P+2)H. For P>=4, the division polynomial is at most1024(P+2)^2, and J<4(P+2)^2. Hence this is less than2^17(P+2)^4, in particular the proposed2^18 and2^20 ceilings. This arithmetic does not absorb remaining source/controller/payload/grant units into literal instructions.

## Exact outermost meter theorem

Instrument the original providers compare/add/subtract/divmod by a nesting stack. A provider interval belongs in the removed bill exactly when it starts at stack depth0. Such intervals are disjoint, and every source Word read/write/move with nonzero provider depth belongs to exactly one of them. Therefore their interval sum equals the action-by-action inside-provider count. Subtracting all inclusive intervals is wrong: original divmod invokes compare and subtract internally.

The independent checker uses a second measurement surface: it instruments each original Word.read/write/step and labels that individual action by the current provider depth. This is separate from the interval-delta measurement around raw methods. On all14 forward/inverse source runs, these two measurements agree exactly. They cover6,189 outer provider calls and4,519,473 original Word actions. The proper removed total is3,946,547; summing every nested provider interval instead gives4,639,829, exceeding even the aggregate original producer work. This is an explicit double-counting control.

Returned add/subtract/division values remain owned after their primitive. Their later source free is retained work. For a restored P-bit Word, exact Word.erase costs5P+8 read/write/move actions: the initial rewind3, digit loop3P, terminator read/write2 and final rewind2P+3. The checker retires the returned lower/product only after the producer and verifies the extra2(5P+8) actions remain outside all removed intervals. The eight protected dirty Words, including deliberately displaced unrelated heads, remain identical; all56 owned bodies end blank and restored.

## Evidence and remaining join

Run from a repository/package tree containing the pinned original source files:

    python3 -I -W error -B independent_source_check.py --source-root PATH
    python3 -I -O -W error -B independent_source_check.py --source-root PATH

Both modes produced identical SOURCE-RESULT.json SHA2569ee37a5773be6bf80f06f022681db8c86dc491eb2e55f6f5349c284d68e694a0. Seven fixtures in both directions cover P4/5, nonleaf left/right groups, initial/final unit Euclidean divisors, zero coordinates, invalid left coordinates, padded right coordinates, aliased doubling and distinct inputs. A direct integer current-coordinate oracle is derived from prefix inverses and checked against all output values and records. Dropping the quotient-reduction division from J fails every fixture.

The final combined source and its frozen receipt, reviewed in REVIEW.md, supply: the new literal graph supplies all raw calls with no fallback; source residual equals old total minus the outermost provider total; numeric R/W/M is charged only through arena.meter and selector R/W/M only through its marker owner; those overlaps are removed once before literal instructions are included once; finite allocation/dispatch/flag control and physical grants remain separate; actual owner histories are recomputed. The separate final review records the precise completed join and remaining model boundary.
