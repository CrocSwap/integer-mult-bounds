# Changed circuit, ownership and conditional exponent

The adopted supplier is PR2312 head
`fb76f799ccf078f51780076ebed3fd26b1db11c0`, manifest
`c545968fb8cf6e550b82ba631e92fd756484db75e621aee211347749cff55313`.
The parent baseline remains independently pinned to PR2288 head
`614c74a63b0f6d4a24c7740d7ddb90d37861b3c7`. Neither source is modified.

## 1. Coherent four-role change to the actual adopted word

Let the low raw roles be `(616,617,618,620)` and the high roles
`(619,621,622,623)`. Twelve consecutive preparation ADDs implement `L += M H`:

```
M = [-1 -2 -2  0]
    [-1  2  0  2]
    [ 1  0  2 -2]
    [ 0 -1 -1 -1].
```

Their common chart is `C5=span(260,132,75,42,25)` and the low entrance is
`span(51)`. The constructor identifies scalar events in the actual PR2312
word, including its already present pivot-518/506 kernels. There is no
intervening incidence on these eight roles before their first source
acquisition. The twelve ADDs can therefore move to immediately before that
acquisition without changing the scalar operator on any input.

Use `C4=span(260,132,75,51)`. Since `51=42+25`, C4 lies in C5 and contains
the low entrance. All eight rank-six acquisition charts contain C4. Replace
the four high roles by retired source fields `(1,4,6,12)`. Their actual last
uses precede the handoff, with measured rank-four charts. The explicit
invertible binary maps in `generate_words.py` carry those charts to C4;
the native chain checks their physical Clifford representatives, phases and
inverse orientation.

The initial high columns have zero final target response, so the new values
can be arbitrary operator-valued forms. They are not assumed clean or equal
to old helper dirt. Exact replay uses independent noncommuting handoff symbols
and inverses. FULL cleanup is derived by reversing the actual changed
non-target word; proper-ended restores and all 78 zero buffers are retained.
Both complete words are checked on all 658 arbitrary public input columns,
forward and inverse-transpose. All retained helper entrances and endpoints,
PR2312's actual refits and its two kernels are preserved.

Four low jumps become `1→4` and eight acquisition jumps become `4→6`;
four retired-source `4→9` jumps disappear. The actual local change is

```
ΔH = {1:-8,2:+8,3:+4,4:-4,5:-4}.
```

The helper inventory decreases 438→434 by deleting old compact indices
`384,386,387,388`, exactly raw roles `619,621,622,623`. There are 46 handoffs.
The actual local profile is `{1:2335,2:512,3:426,4:120,5:38,8:8}`, mass 5371.

Of the 2664 deleted width-four placements, 2647 occupy rank-32 `[4,9,9,9]`
bins with idle rank one, and 17 occupy full rank-48 `[4,8,9,9,9,9]` bins.
Deletion therefore changes idle ranks by `{1:-2647,5:+2647,4:+17}`.
Adding this to 666 copies of the exact native delta yields the full actual
pre-repacking profile, rather than crediting the helper deletion alone.

## 2. Two jointly legal whole-role exchanges

Two exchanges use disjoint port sets `{0,1}` and `{3,4}`. Together they fill
six rank-16 singleton-nine bins with rank-seven roles; release three rank-32
`[7,7,9,9]` bins into `[9,9,9]`; and remove respectively two and one rank-nine
roles from two full five-nine rank-48 bins. Their combined idle change is

```
Δidle = {3:-2,5:+3,7:-6,12:+1,21:+1}.
```

Every complete helper appears once with its actual width. For every role,
the invocation must lie after the owner's last source touch and before the
idle-consumption event. A full precedence graph contains these bounds and
each replica's ordered data recipe. The two assignments are composed by call
identity and accepted only if this joint graph is acyclic. Its topological
order is then expanded into literal source events. All 1332 windows and every
physical family exclusion, capacity and contiguous offset are independently
reconstructed. Individually feasible moves alone are insufficient.

`generate_owners.py`, CALL-ORDER.json and OWNER-MOVES.json.gz regenerate the
whole assignment from the pinned PR2312 owner map. The independent bounded
checker does not import that generator or the emitter.

## 3. Complete stock, moment and conditional transfer

The private namespace injects all 78 restored buffers into `[66312,66390)`
inside the priced 434-field reserve `[66312,66746)`. Live families are
`[0,66304)`, eight centers `[66304,66312)` and coefficient work
`[66746,66748)`. These ranges are disjoint. All 666 calls map their 658 data
and helper names to distinct live families. Both emitted native programs
restore every buffer to zero on all arbitrary input columns. Thus the
physical stock is 66748; no additional 78 fields are required. Physical phases
and the complete controller/invoice remain separate checks.

For `m=73` and `W=66304`, write

`F(b) = Σ_r H_r (r/73)^(1-b) / 66304`.

Every rank lies strictly between zero and 73, so F is strictly increasing.
The full H in CLAIM.json has rank mass 4816512 and deficit 23680. Directed
integer log/exp enclosures prove `F(b_lo)<1<F(b_hi)` at the two forty-digit
endpoints. The published rational lies below the final admitted outer point.

The changed suppliers receive full scalar, wrapper, physical phase and
Lemma G label checks. The new complete schedule/owners receive fresh strict
controller, physical invoice, finite assembly and rejection controls. The
retained fine-prime outer is retuned to the admitted native endpoint and all
63 inequalities, 17 controls and independent checks are rerun.

The source-bound replay explicitly authenticates the complete PR2288 baseline
cache and the complete new native evidence against immutable PR2312 sources.
The PR2312 runtime also retains its fixes for identical-provider negative
controls and hosted pooled-slot time binding. Our independent owner guard
compares all eleven hosted row fields and the actual owner-map digest.
Changed source, program, recipe, wrapper, phase or word evidence invalidates
reuse. Input and frozen SPEC artifacts are distinguished and their complete
effective discovery equivalence is recorded.

The bounded hook checks owner geometry, exact moment/cap and publication
bindings; it does not replace full native or outer execution. All inherited
README qualifications remain, including exact recovery, PR559 recurrence
correction and the all-size interfaces. Finite composition is not a complete
formal multiplication theorem.
