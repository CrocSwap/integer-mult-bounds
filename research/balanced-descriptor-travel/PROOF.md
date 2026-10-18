# Sequential factor access for the unchanged balanced word

## 1. Claim and hypotheses

Let n>=1 be any integer. Number the factors 0 through n-1.
Use the balanced factor word in the pinned PR985 `compose` dispatcher.
Every internal call splits its contiguous factor interval into lengths
l=floor(n/2) and r=n-l. Its positive chronological child word is

```text
U, V, U^-1, V^-1.
```

Its negative word reverses the positive word and negates every operation.
We study factor indices only. We do not change array roles or arithmetic.
The claim applies to both signs of every completed invocation.
No assumption on numerical coefficient values enters the index argument.

Let N(n) be the number of factor lookups. Let V(n) be the sum of absolute
successive index differences in the positive trace. Let C(n) include travel
from index zero to the first lookup and from the last lookup back to zero.
For either sign,

```text
N(n) = 3qn - 2q^2,       q = 2^floor(log2 n),
V(n) <= 2(N(n)-n),
C(n) = V(n) + floor(n/2) < 2N(n).
```

For n=1 these formulas give N=1 and V=C=0.

Suppose the records occupy a contiguous read-only region with fixed width B>=1 bits.
The descriptor head starts at that region's first bit.
No unrelated operation moves that head during a leaf.
The reader below obtains every record and restores the head at completion.
It uses fewer than 4NB descriptor-head moves and exactly NB bit reads.
This is a factor-access theorem, not a full multiplication theorem.

## 2. Endpoints and inverse traces

A single-factor trace starts and ends at its only index.
Assume the endpoint claim for shorter intervals.
The positive word starts with U, whose first index is the interval's left endpoint.
It ends with V^-1, whose last index is the first index of V.
That index is the splitting point l, relative to the interval's start.
Thus the positive endpoints are 0 and floor(n/2).

Writing rev for sequence reversal, the positive index word is

```text
P(l), l+P(r), rev(P(l)), l+rev(P(r)).
```

The actual negative dispatcher orders its children V,U,V^-1,U^-1.
This is precisely the reversal of the displayed index word.
Consequently the negative trace has the same variation and swapped endpoints.
This proves both claims by induction, including unequal child lengths.

## 3. Exact recurrence and universal bound

Each child's internal variation occurs twice.
Put a=floor(l/2) and b=floor(r/2).
The three bridges between children have lengths

```text
l-a,     l+b-a,     l+b.
```

These values are nonnegative. Their sum is 3l+2b-2a.
Hence

```text
V(1)=0,
V(n)=2V(l)+2V(r)+3l+2floor(r/2)-2floor(l/2).
```

If r=l, the bridge sum is 3l<=2n.
If r=l+1, the difference of the two floors is zero or one.
The bridge sum is therefore at most 3l+2<=2n.

Define H(1)=0 and H(n)=2H(l)+2H(r)+n for n>1.
The leaf recurrence is N(1)=1 and N(n)=2N(l)+2N(r).
Substitution and induction give H(n)=N(n)-n.
The preceding bridge bound then gives V(n)<=2H(n)=2(N(n)-n).

Both signs pay the same initial and final travel, totaling floor(n/2).
For n>=1, floor(n/2)<2n. Thus C(n)<2N(n).
No finite census supplies this all-n conclusion; the induction does.

For completeness, the balanced binary interval tree has leaves at depths h and h+1,
where h=floor(log2 n) and q=2^h.
There are 2q-n leaves at depth h and 2(n-q) leaves at depth h+1.
Each binary-tree leaf at depth d occurs 2^d times in the four-child word.
Therefore N=(2q-n)q+2(n-q)(2q)=3qn-2q^2.
In particular N<=2n^2 and N>=n.

For n=2^h, substitution in the recurrence gives V(n)=3n(n-1)/2.
For n>=2 in this family, C(n)=(3n^2-2n)/2.
The quadratic travel order is attained by this word under the stated layout.
This is not an optimality claim over other encodings, words, or caches.

## 4. Reader construction and complete lookup bill

At a requested index i, seek to bit iB from the current record's first bit.
Read and copy B bits into scalar workspace, advancing one cell per bit.
Return B cells to the record's first bit.
Keep this descriptor head there while the leaf executes.
After the final leaf, return to the first record.

The seeks and final return use BC(n)<2NB moves.
The reads and local rewinds use 2NB additional moves.
There are exactly NB reads and NB copied bits.
Thus fewer than 4NB descriptor-head moves suffice, including the final return.
A copy destination can use one additional tape with O(NB) movement.
This bound does not charge a separate descriptor head for every factor.

A required preflight scan reads the n records consecutively and returns once.
It adds 2nB moves and nB reads, hence remains O(NB).
Numerical validation of the records remains an inherited arithmetic cost.
Padding or rearranging a different input layout costs P_layout and is not free.
A provided fixed-width binary tuple format allows O(B) parsing per record.
Any other parsing cost P_parse must be added explicitly.

The root has a fixed number of common parameters, such as the gauge and margin.
Let G be their total bit length. Copy them once into a fixed number of scalar
workspaces before the word, paying O(G) reads, copies, and eventual clearing.
Access within these workspaces remains part of the leaf arithmetic bill.
If the interface prohibits these retained scalar parameters, charge its alternative
access scheme separately; this theorem does not make distant global reads free.

Here is a conservative bound for the lookup scheduler's own control work.
Let a=ceil(log2(nB+2)) and h=ceil(log2 n).
The four-child call tree has (N-1)/3 internal nodes and N leaves.
A stack stores interval endpoints, direction, and next-child state in O(a) bits per frame.
Its depth is h+1. Local push/pop and midpoint calculations cost O(a^2) per node.
Computing a seek distance B|i-j| by binary schoolbook arithmetic costs O(a^2) per lookup.

A countdown controls each literal head walk.
Use a binary counter with its head returned to the least significant bit after each decrement.
Across d decrements, digit k changes at most floor(d/2^k)+1 times.
The sum over k is O(d+a), including carry travel and counter-head returns.
Store no leading zero digits. When a borrow removes the leading one, erase that position to the end marker.
Only that leading position disappears; lower borrowed positions now contain ones.
The next iteration detects zero from a blank least-significant position in constant time.
This avoids a full-width zero test after every decrement.
Loading and clearing the counter cost O(a); the seek distance itself remains charged.
Consequently the control does not multiply every descriptor move by a bit-length factor.

The resulting classical fixed-tape lookup bound, including preflight, is

```text
P_layout + P_parse + O(G + N(B+a^2)) bit operations,
O(B + G + (h+1)a) workspace bits,
a = ceil(log2(nB+2)).
```

This counts descriptor copies, returns, control, and the retained common parameters.
It excludes data-array operations and coefficient preparation, which remain paid by their own bounds.
It permits ordinary scalar clearing and does not construct reversible bit gates.
No array of cached factor records is required beyond the supplied read-only region.

## 5. Relation to prior bills

Ali Romman's PR985 states a safe O(r W_total) lookup allowance per leaf,
and hence O(r^3 W_total) over the balanced word with n=r-1 and r>=2.
That allowance is conservative, not a false upper bound.
The present reader replaces repeated worst-case full scans with the word's actual access order.
For B=O(W_total), its factor-access term becomes

```text
P_layout + P_parse + O(G + r^2(W_total + log^2(r W_total+2))).
```

Factor and phase preparation, internal powers, rounded divisions, mutable-array routing,
source restoration, recursive children, assembly, and all compiler hypotheses remain unchanged.
This statement neither proves that preparation improves nor asserts a faster measured program.
The combined bound must add the predecessor's other terms and these explicit setup costs.

PR1054 improves the dirty leaf's sufficient precision and length admission.
We do not reprove those numerical statements or certify its entire displayed invoice.
Hanson Sun's PR1085 bounds ideal prefix magnitudes; it does not bound this descriptor trace.
Chafik Boukhalfa's PR628 supplies the balanced commutator and its paid preparation lineage.
The exact leaf-count result also appears in 0xkilgore's PR663 and is not new here.

The contribution is the all-n sequential-access bound and a paid reader for the unchanged word.
It closes a specific lookup-cost obligation without claiming a new kappa or physical supplier.
Finite checks, package validation, and this written proof have distinct roles.
There is no independent human review or formal verification of the multiplication theorem.
