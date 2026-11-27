# Packed batches without a radix larger than the row width

Status: **proved conditional component; awaiting independent review**. This
removes one reason for choosing a huge address radix. It does not supply the
compact routing/repair template in its interface or a new multiplication bound.

Source: OpenAI `math@3344da59991ed94f9ba711217b29c1d760badfa6`, November
tape manuscript `build/interchange.tex`, “Spectral conversion and the choice
of constants” and “Running the recursion”. The source chooses `b>W` and uses
one leading radix digit for W independent rows. Binary-to-radix padding then
costs below `b^2`. Here the batch index may occupy several leading digits.

## 1. Exact local interface

Fix integers `m>=2`, `a>=0`, `W>=3`, an odd compatible prime `b>=3`, and
positive encoded symbol width h. Put `K=m+2a` and

    ell=min {r>=1 : b^r>=W},   B=b^ell,
    C=W ceil(B/W),            beta=C/B.

Then `1<=beta<2`, `ell<=1+log2 W`, and B,C have
`O(log b+log W)`-bit descriptions.

Assume a **packed main template** satisfying the following concrete contracts.

1. On W independent rows it implements the m main field swaps, restores all
   2a occupied reserves and preserves other coordinates. Rows are a complete
   lexicographic index range; every row is an independent input.
2. For arbitrary batches/spectators, ordinary scans, row maps, comparisons,
   regroupings and control cost `c V+g(log(V+2))` actual steps on encoded
   volume V and use at most `c_space V` payload cells. Constants c,c_space
   and the actual polynomial g are declared. In the intended application
   they must have fixed polynomial bounds in the compact description,
   m,b,h,log W; symbolic sparsity does not itself establish these bounds.
3. Its spatial calls are executable on packed groups of rows with relative
   volumes `nu_i`, `sum nu_i<=q`, and `max nu_i<=1/4`. Each call is an
   ordinary width-f interchange with arbitrary prefix/gap/suffix ranges.
   Its gather/return work and descriptor belong to item 2. The number of
   calls has the declared compact bound: there is no exponential loop over
   empty roles. Grouping R identical calls by using R as a spectator prefix
   preserves total volume, but only actual realized groupings qualify.
4. A child parks at most `c_space V` payload cells and a polynomial-size
   end-access descriptor. Main work areas are cleared before reserve calls.

These are local interfaces at every f, not assumptions of an interchange
exponent or final H(n). The convenient group maximum 1/4 could be replaced
by any fixed number strictly below 1/2.

## 2. Packing and padding are scans

At a node with two width-e radix-b fields take

    f=floor((e-ell)/K).

If f<1, use direct radix-digit swaps. Otherwise partition each large field
into ell leading digits, a reserve fields of width f, m main fields of
width f, a reserve fields of width f, and fewer than K remaining digits.
The earlier field supplies early reserves; the later supplies late reserves.

The first ell digits of the earlier field already enumerate `[B]`. Extend
them to `[C]` by appending zero rows inside each preceding-prefix fibre.
The suffix stays unchanged. Decompose each value as

    z=W batch+row,  0<=row<W.

This is exactly the existing lexicographic order. No transpose, W-way
materialized split or W-entry table is needed. Compute W,B,C in binary;
amortized counters or polynomial(log W,log b) division at a row boundary
expose the two indices. Each row has a nonempty suffix, so even charging
that polynomial per row fits the compact invoice. A control marker records
genuine values. Padded data rows are initialized to zero and paid in the
volume; they are not counted as extra productive input.

Insertion and removal cost

    V poly(log(W+2),log(b+2))+poly(log(V+2),log(W+2),log(b+2))

on a fixed number of tapes with O(V) payload cells. The padded volume is
exactly beta V, below 2V. Arbitrarily long suffixes do not add log V work
per symbol: decrement a low-end down-counter with amortized ripple carries,
signal zero during decrement, and reset/copy O(log suffix-length) bits once
per complete row. That reset is bounded by its positive row length. Prefix
counters also advance amortized. The row index has O(log W) bits already
covered by the declared polynomial.

## 3. Correctness and recurrence

Run the packed template. Its completed full-rate map acts separately on each
row and preserves the leading value, so it preserves the genuine set z<B.
Remove padding by a scan. Intermediate predictor/repair maps may mix genuine
and padding rows; it is the completed identity that justifies removal.

Exchange the 2a reserve-field pairs recursively on the original volume V.
Exchange the ell leading digits and fewer than K remainder digits directly.
A radix-digit exchange costs polynomial(b) times V by splitting/merging b
classes. Thus this final direct work is `poly(b)(ell+K)V`. The two complete
width-e fields are now interchanged exactly.

Let T(e) be time per encoded symbol, with descriptor terms retained
separately. Suppose an explicit applicability guard gives
`g(log(V+2))<=c_setup V` at every executed non-base node (or a separately
proved absolute-degree bound gives that inequality at all V). Include
c_setup in c0. Under this guard the actual recurrence is

    T(e)<=c0+(beta q+2a)T(f),
    f=floor((e-ell)/K)<=e/m.                           (PB1)

c0 includes template scans, packing, direct digits, parking, erasure and
returns. It depends polynomially on ell and b under the declared compact
contract, with no automatic B or W factor. Taking q as the source normalized
call volume recovers its `2 sigma/W+2a` upper invoice since beta<2.

Suppose `1/2<alpha<1`, `0<eta<=1`, and

    beta q+2a <=(1-eta)m^alpha.                        (PB2)

With `E0=ell+K`, a direct base costs at most `C_dir poly(b)E0` per symbol.
Choose `M>=max(c0/eta,C_dir poly(b)E0)`. Induction gives

    T(e)<=M max(1,e)^alpha.

The recursive part is at most `(1-eta)M e^alpha`; the remaining c0 is at
most `eta M e^alpha`. Base widths e<=E0 fit M. All parameter dependencies
remain explicit. The setup polynomial is absorbed into volume only after
its actual coefficients and degree are bounded. A template-dependent
degree can give a non-polynomial absorption constant; this lemma does not
call it polynomial in compact parameters. Nodes failing the explicit guard
must be priced separately as base cases. No arbitrary interpreter or
fixed-parameter polynomial is silently made uniform.

## 4. Visited cells and binary input

A grouped main call has volume at most `(beta/4)V<V/2`. Depth-first parked
payload therefore sums by at most two times the declared coefficient.
Before full-volume reserve descents, main arrays are merged and cleared;
only descriptors remain parked. End-access stacks and reusable regions
bound all cells ever visited. Descriptor workspace must separately meet
the declared compact threshold/space profile.

For binary field width u, choose the least e with b^e>=2^u. Source range
padding increases volume by less than b^2, with e<=1+u. If b is polynomial
in compact parameters, this remains polynomial even when W is exponential.
Constructing a compatible small b and small-coefficient endpoint maps is
a separate obligation.

## 5. Consequence and remaining questions

The literal condition b>W is sufficient for one-digit batching but is not
forced by independent occupancy. Under the stated packed-template contract,
multiple leading digits replace that expense by log W. This does not prove
arbitrary compressed matrices or their grouped calls satisfy the contract.

The next gate is to compose S003 masked rotations, shift-only repair and
endpoint routing so every spatial call meets item 3 without increasing its
total normalized volume. A second gate is actual small-magnitude rational
address maps and a compatible radix. A complete overhead rate requires
both plus the numerical Walsh, precision, uniformity and space accounting.

Credits: source padded spatial recursion and depth-first scheduling; S002
full-rate and structured-shift work; Jerry Chen (@CubeJerry); AI-assisted
S003 packed-batch derivation. No full multiplier or formal build was run.
