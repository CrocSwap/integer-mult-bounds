# Current scalar SERVICE tables on complete coded fields

Prepared for **@CubeJerry**, with substantial OpenAI assistance. Apache-2.0.
This is a source-bound physical implementation lemma. **No new κ.**

## 1. Exact claim and boundary

For each fixed nonzero rational coefficient q, `tables.compile_scalar` emits a
finite table in the **unchanged** `machine.execute_table` grammar of the
published `compiled-owned-bank-lifecycle` source. The only runtime instructions
are branch on one local symbol, write one local symbol, unit move, goto, halt
and reject. The generator runs before numerical input size varies. No runtime
integer, coordinate, component width, record count or payload callback is
supplied to the resulting table.

For SCALE the ordered public ports are `(target)`. For ADD they are
`(target,source)`, on **distinct physical tapes**. There are two work ports:
protected candidate output and unary rewind guide. Any additional supplied
work and binary-context ports are untouched by the table. The unchanged
`Controller.primitive` supplies entry retirement, `execute_table`, and success
retirement on its complete fixed work inventory.

Each input is a nonempty complete complex field on one common numerical grid.
One complex record has two signed little-endian two's-complement components,
each of width w>=1 followed by virtual delimiter 2. The source and target have
the same complete ordered shape. A virtual symbol occupies the lifecycle's
three nonblank physical bits. The physical blank frontier immediately follows
the last complete component: no coded logical blank or private tail belongs to
the public field. All supplied public, work and context heads begin at their
current origins. Each initially dirty work body is one contiguous raw binary
prefix ending at a physical blank, as required by the inherited `retire`;
there are no hidden live bytes beyond an interior blank. Work and context
segments are distinct from every public field and ancestor segment.

**Theorem (exact success domain).** For every width and record count, the table
succeeds exactly when every component of the requested scalar output is an
integer on that same grid and lies in the original signed width. On success,

* SCALE returns q*x and ADD returns x+q*y, component by component;
* every public field has precisely its original physical extent and delimiter
  positions; the ADD source is unchanged;
* the table performs no target write until the complete field has passed all
  arithmetic/shape checks;
* the original table executor restores all supplied heads, and the original
  primitive wrapper physically erases all work bodies before return;
* fixed-tape time is O_q(V+D+Q), with two used work tapes, where V is one
  complete coded field's physical length, D is the total initially occupied
  current work prefix, and Q is the fixed caller work/context inventory.

The result does not require the product q*y or an implementation-specific
numerator to fit a temporary signed word. It never materializes such a word.
The finite carry belongs to the precompiled control, whose size depends on q
and not on w or the number of records.

The exact current sources instantiate this theorem at all 366,842 original
ADD/SCALE service occurrences of the selected complete caller. Their 42
operation/coefficient pairs use only 31 distinct coefficients. COPY remains
the lifecycle's original addition; two-output SWAP/SIGNED_SWAP and native
phase, movement, Gaussian and recursive services remain separate.

## 2. Integer relation and the finite carry

Write q=a/b in lowest terms, b=2^d*b0, b0 positive odd. The required relation is

    2^d*b0*z = p*x + r*y,

where `(p,r)=(a,0)` for SCALE and `(p,r)=(b,a)` for ADD. In the one-input case
y is the finite constant zero, not an allocated numerical word.

Read the w bits of each input least-significant first and remember their last
bits sx,sy in finite control. Continue with **exactly d sign-extension bits**
sx,sy, even when w<d. Thus the total input digit stream has length n=w+d.

Initially c_0=0. At positions i<d, set u=p*x_i+r*y_i+c_i. Require u even and
put c_(i+1)=u/2. These discarded digits are precisely the low d numerator bits.
At positions i>=d, emit

    z_(i-d) = u mod 2,
    c_(i+1) = (u-b0*z_(i-d))/2.

The division is integral because b0 is odd. Negative carries use the same
integer equalities and nonnegative parity bit; there is no unsigned
reinterpretation of a negative component. Exactly w output bits are emitted:
there are w+d input positions and precisely d discarded positions. For w<d,
the remaining discards occur in the sign-extension stage, then its remaining
positions emit exactly w bits. The last emitted bit is the candidate sign sz.

The bounded interval

    |c_i| <= A,  A=|p|+|r|+b0

is invariant. In the discarded stage,
`|c_(i+1)| <= (|p|+|r|+A)/2 <= A`. In the emitting stage, including either
output bit, the upper bound is
`(|p|+|r|+A+b0)/2=A`. Therefore the table has finitely many carry states. Its
other state components are the discarded-position counter in 0..d, a fixed
sign-extension counter in 0..d, the last input/output bits, component parity,
and a first-component flag. All are independent of runtime width and length.

Let X_n,Y_n be the unsigned values of the n sign-extended input bits, and Z_w
the unsigned value of the w output bits. Summing the digit equations gives

    p*X_n+r*Y_n-2^d*b0*Z_w = 2^n*c_n.                 (1)

The sign of the right side matters. An early draft had the opposite final
sign; the first most-negative physical fixture rejected it. The corrected
equation above is checked by a retained wrong-sign mutation control.

Since sign extension preserves the signed inputs,

    X_n=x+2^n*sx,  Y_n=y+2^n*sy,  Z_w=z+2^w*sz.

Substituting in (1) proves that the requested signed relation holds **if and
only if**

    c_n = p*sx+r*sy-b0*sz.                             (2)

This is the final finite-state guard. It simultaneously checks divisibility
by the odd denominator and signed output fit. No guessed bound or floating
point comparison is involved.

### Completeness, including negative and boundary values

Suppose the requested signed output is integral and lies in
`[-2^(w-1),2^(w-1)-1]`. Its numerator is divisible by 2^d, so all d discarded
digits are zero. At each remaining position, oddness of b0 uniquely determines
the next quotient bit from the relation modulo the next power of two. The
emitted w-bit word is therefore this output's two's-complement word. Equation
(2) follows from (1), and the table accepts. Conversely, acceptance of (2)
proves the exact signed relation for the emitted w-bit value, which is by
definition in the original signed range. Thus neither a nonintegral value nor
an out-of-range value can be accepted.

Zero has the ordinary all-zero signed word and satisfies the same proof.
Equal **values** on distinct ADD tapes are allowed; the physical alias x=y is
excluded by the ordered-port contract and rejected by source binding. The
proof has no probabilistic independence or uncorrelated-input premise.

For example, at w=4, SCALE(-1/2) maps -8 to +4. A recipe which first computes
NEG(-8) in four signed bits rejects an intermediate +8. This table accepts the
representable final value without creating that intermediate word. Similarly
ADD(2) sends `(x,y)=(-7,7)` to +7 although 2*y alone does not fit four bits.
These are weaker **arithmetic admission conditions** at the new interface;
they are not a claim that an older literal recipe's rejection policy changed.

The proof works for every fixed rational q. The concrete selected catalogue is
dyadic. For an odd-denominator successor such as q=1/3, the table still requires
the exact integer-grid relation; it does not prove that a proposed caller's
inputs or recursive microstates meet that condition.

## 3. Whole-field staging, movement and ownership

The arithmetic stream writes candidate bits to a separate output port. A work
guide starts with virtual marker 5 and appends one virtual 1 for every consumed
input bit or component delimiter. Each component is checked before its output
delimiter is emitted. A parity state requires an even positive number of
components at the field frontier. ADD verifies source and target bits,
delimiters and final frontiers in lockstep.

Once the **whole** field is accepted, output and input have equal virtual
length L. The guide has one marker followed by L ones. Starting at its blank
frontier, move it left once and inspect. For each one, move every public input
and the output left once. On reaching marker 5, those heads have moved exactly
L places and are at their current origins. No head-position query or decoded
length controls the movement. The marker terminates the guide before an extra
left move of a public tape could cross its origin.

The guide is then read forward. Each one copies one candidate output symbol to
the target and advances both ports once. Its end coincides with the unchanged
target and output frontiers. Every copied symbol is 0,1 or delimiter 2. This
preserves the complete numerical format and extent. The ADD source is never
written. The original executor's final raw-origin loops restore every supplied
head, including untouched read-only contexts.

Work is encoded, so writing virtual blank 4 would leave nonblank physical
codewords. The implementation therefore uses the original primitive wrapper's
literal `retire` after table success. Its raw binary scan erases every code bit,
including the guide marker, and restores current origins. No ancestor marker
is touched. It uses the same charged entry retirement if work was initially
dirty. Retained visited backing is not confused with live contents.

On an arithmetic rejection of otherwise well-formed inputs, the target and
source **contents** are still unchanged, including when a late component
fails. Rejection may leave heads advanced and work occupied: the inherited
executor raises immediately and has no success retirement on that path. This
package does not claim rejection rollback or interruption recovery. The
all-success source composition uses the explicit exact-grid/range premises.

## 4. Complete cost and retained backing

Let B be the number of data bits, c the number of components and L=B+c the
virtual field length, so V=3L physical bits. The first pass processes B actual
data digits and exactly d*c constant-control extension steps. It also writes
c delimiters and L guide marks. Since each component is nonempty, c<=L and
this is O_q(L). Rewind and installation each make L guided iterations. Every
virtual symbol read/write/unit-move expands to at most 13 physical cell
actions under the unchanged `CodedPort`; each iteration uses a fixed bounded
number of table rows. The executor's final origin loops and both raw work
retirements are linear in the complete occupied prefixes, not merely the
number of output values.

A conservative ceiling for initially blank two-port work is

    physical cell actions + table-row steps
        <= 1024*(d+2)*(L+1).

It follows by charging at most 128 actions/rows per actual input symbol,
32 per extension step, 64 per rewind symbol, 96 per install symbol, 64 per
symbol for final head restoration and retirement, and fixed entry/exit work
below 256. These deliberately loose terms fit the displayed ceiling for
d>=0 and L>=1. Extra untouched fixed ports cost O(Q); a dirty initial raw work
prefix of D cells costs O(D) to erase. These positive terms are retained.

The candidate output occupies at most V cells and the guide at most V+3.
Two used work tapes therefore suffice with current-call backing at most
`2V+3+O(1)`, plus the public inputs and any separate caller inventory. For
reuse histories each tape retains its maximum reached coordinate. A smaller
later call begins at a blank current origin and scans its own new body, not
an old erased high-water interval. This gives the coordinatewise maximum bound
`max(previous backing, current extent)`; no deletion of visited cells is assumed.
When these ports are parked by the existing lifecycle, its original ancestor
and allocation theorem remains the explicit composition premise.

For a fixed compiled template with arithmetic services E, the complete added
bill is the positive sum of these per-service bounds, using each actual
field length V_e and initial dirt D_e. Finite source compilation, tables and
coefficient constants are independent of input size. Thus these services cost
linear current volume per ordinary node and do not alter paid recursive
histograms or productive targets. This does not certify the historical raw
`10^9` numerical allowance: exact machine constants, other providers and the
outer admission must still be joined and priced.

## 5. Binding to actual current source events

`SOURCES.json` pins canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, its selected #6030 word and the
complete P104 controller. `DEPENDENCIES.json` pins byte-identical published
lifecycle machine and `source_ir` exports at
`ab239cb6ee884e7a900dd9101c34448077fad0b0`. Those source bytes are unchanged.

The original lowerer supplies the exact local operands and caller field maps.
It preserves local instruction tokens under chronological products, caller
occurrences and the finite compiler's `unit-fragment` remapping. The new
`source_literal` follows the exact source remapping wrapper grammar to the
active original token, authenticating its exact source instruction, operation,
coefficient and arity. In `product-right`, the separate issuing PAID token is
provenance; only the last member is the active instruction. Searching all
nested tuples would confuse these two roles. It uses the emitted
ordered fields as the actual ports, rather than replacing them by the old
local role numbers. Duplicate binary ports are rejected.

Boundary ADD/SCALE instructions are authenticated against their actual source
program; physical outer ADDs against their exact site; query additions against
the actual forward QUERY_SHEAR record. No whole-job normalizer, two-output
swap or native/paid event is reinterpreted as a scalar. The complete source
partition is:

| Covered original scalar service | Occurrences |
| --- | ---: |
| 18 copies of the local ADD/SCALE word | 346,770 |
| Outer scalar ADDs | 9,360 |
| Left boundary ADD/SCALE | 6,240 |
| Right boundary ADD/SCALE | 2,912 |
| Forward query accumulation ADD | 1,560 |
| Total | 366,842 |

The 18,404 local ADDs, 861 SCALEs and 23 separate COPYs agree with the source;
the 31-coefficient/denominator-16 census is already reported by #6928 and is
credited rather than claimed anew. The contribution is the actual executable
table binding, its exact success domain and complete tape accounting.

Assume the source occurrence/geometry theorem gives each scalar its actual
aligned complete operands, and the current ideal precision theorem supplies
exact integer-grid outputs and the common signed range at these cuts. The
theorem above then discharges the physical scalar-table premise for every
covered service, including arbitrarily correlated values and all spectators.
Induction through its actual chronological service sites preserves their
endpoints without a scalar numerical callback. This substitution does not
prove those geometry or precision premises, native returns, row dispatch,
recursive termination, global ownership, or analytic recovery.

## 6. Novelty, evidence and open obligations

PR #3098 (`physical-scalar-stream`, Jose Manuel/jmbarrancoml) already proves
linear sequential execution of inherited scalar recipes on aligned packets,
with finite local word roles and explicit lifecycle. It leaves actual caller
alignment and owner binding open. It credits Nick Petalas's #3078/#3090,
Sagar Thakrar's #696, James Chang's #1869 and #3091. Their arithmetic and
ownership contributions are retained. This package supplies the current
coded ABI and actual finite-table/source join. The endpoint-complete fused
transducer also avoids recipe-specific temporary-word rejection conditions.
It does not rerun or replace their whole-provider theorem.

The exact Fraction oracle checks small full signed domains and complete wider
fields through the original physical table executor. The actual Controller
fixture executes the uninterrupted current scalar block at source events
1..9895 on 799 borrowed fields after the source's INIT(778) boundary; it starts
that owned operand at zero and compares every returned component. This is a
source prefix, not a complete native caller. The complete 642,410-event source
scan binds the covered services and leaves every other opcode untouched.
Finite evidence is not the quantified proof in Sections 1–5.

Open next questions are the current Gaussian/phase and recursive numerical
providers, complete compiler/row/lifecycle composition, and the successful
whole-caller precision/cost join. The optional odd-denominator primitive does
not discharge the new rational-grid obligation in #6932/#6934. All five
selected assumptions remain in force; the selected κ stays 0.003125804.
