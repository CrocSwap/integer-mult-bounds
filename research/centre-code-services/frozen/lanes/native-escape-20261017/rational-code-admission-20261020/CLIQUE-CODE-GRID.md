# Exact scalar codes for the signed rank-sixteen response

The actual pair modes and an actual partition of the other 64 ports give
a full 112-port response E with rank(E-I)=16. Its only eigenvalues are
1, -5, and -7. Both E and its inverse have an in-place scalar word on the
112 data fields. The words need no owned field and no native child at a
proved common-frame cut.

Each word costs 3,420 old real scalar units and 32 real fixed-odd scans.
The forward scans multiply by five or seven. The inverse scans divide
by five or seven. These scans are separate from the old scalar tariff.
The inverse has at most one new factor five and one new factor seven
at every prefix. All other data and borrowed fields remain unchanged.

This is an exact scalar construction for the full response. The new
native supplier word, its phases, its helper progress, the controller,
and the complete recursive invoice have separate proofs. In particular,
this packet does not supply a native inverse response. It supplies the
inverse at an already legal common-frame cut.

## The actual response

The source files are pinned in `check_clique_codes.py` and the receipt.
The actual pair codes, all 48 mode carriers, and their eight groups come
from `CYCLIC-FLAGS.json`, SHA256
`3034e1df3670f64e5b79a51a435d7903f3be7cef10d6b486a8bd4d420c989585`.
The four sign changes and the certified eight-clique sets come from
`RESPONSE-PROGRAM.json`, SHA256
`5832788135e16c2427f8c746f251501621684a02ef88b0a14322056653dc2d7c`.
The checker also binds both scalar endpoints to the frozen native
extension's `response` and `response_inverse`. Its compressed source is
`odd16-normal-v2/EXTENSION-PROGRAM.json.gz`, SHA256
`7160a8764f0b12131e30dd1ca90a28b781b9dd99e8eb2f1935b8592aaf48037b`.
Its decompressed payload has SHA256
`d466cea24be92fb7f749d686c5efc63f44ea82575c15f78c38e9d6d4c972eba4`.
This equality binds the scalar code to the native response. It does
not repeat the native word or phase checks.

Let A be the direct sum of the 24 signed two-by-two pair codes, extended
by identity on the other 64 ports. Each pair block satisfies

```text
A_e A_e^T = 2I,       A_e^-1 = A_e^T/2.
```

The six carriers at a vertex have a sign vector d_v. Four vertices have
one negative sign each. The other entries are positive. In pair-mode
coordinates, the 48-port block is the direct sum of

```text
C_v = I_6 - d_v d_v^T,       C_v^-1 = I_6 - d_v d_v^T/5.
```

On each of the eight certified disjoint eight-cliques, use

```text
C_8 = I_8 - 1_8 1_8^T,       C_8^-1 = I_8 - 1_8 1_8^T/7.
```

The 16 groups partition all 112 physical mode labels. Set

```text
E = A^-1 (direct sum of the 16 blocks) A.
```

For a block of size k and a sign vector d, d^T d=k. Thus I-dd^T acts
by 1 on the kernel of d^T and by -(k-1) on its span. This proves

```text
rank(E-I) = 16,
det(E) = 35^8,
(E-I)(E+5I)(E+7I) = 0,
E^-1 = (E^2+11E+23I)/35.
```

The checker constructs both full matrices from the actual pair codes
and carrier sets. It checks both inverse orders and the polynomial
identity with exact fractions.

The full inverse uses only five and seven. This statement does not
apply to every principal inverse. In particular, a caller that inverts
the 104-port ordinary complement of the selected-eight split introduces
31. Such
a caller must add 31 to its grid and prefix analysis. The determinant
of the full E does not remove that obligation.

## A word without an owned field

First conjugate a signed block by its signs. For an unsigned block of
size k, choose its last field as the pivot p. Let the other fields be
x_i. The forward word is

```text
x_i -= p                   for every nonpivot i
p *= -(k-1)
p -= x_i                   for every nonpivot i
x_i += p                   for every nonpivot i
```

After the first loop, x_i is its old value minus the old pivot. The
middle two steps set p to minus the sum of the old nonpivot values.
The final loop therefore returns I-11^T on every coordinate, including
the pivot.

The inverse word is

```text
x_i -= p                   for every nonpivot i
p += x_i                   for every nonpivot i
p /= -(k-1)
x_i += p                   for every nonpivot i
```

Its new pivot is the old pivot minus the total old sum divided by k-1.
The other outputs have the same correction. This is the stated inverse.
Each word uses three unit-ADD loops, one sign change, and one fixed-odd
scan on each real component of p. No arbitrary data value is cleared.

For the full word, apply A, apply the four mode signs, run all 16
blocks, undo the signs, and apply A^-1. The signed pair words use only
unit ADDs, signs, doubling, and halving. Their full literal events are
in `verified-final-normal/CLIQUE-CODES.json`.

The checker replays 112 independent data columns and two arbitrary
spectator columns. It also checks that no event reads or writes an
index outside the 112 data fields. Thus any number of unrelated borrowed
or owned fields stays exactly unchanged. The two spectator columns are
a check of this scope argument, not a substitute for a helper schedule.

## Complete scalar invoice

Each direction has 384 complex unit ADDs, 126 complex signs, and
48 complex binary scales. The retained prices are eight real units
per unit ADD and two per sign or binary scale. Thus

```text
384*8 + 126*2 + 48*2 = 3420.
```

There are eight complex fixed-odd operations with divisor or multiplier
five and eight with divisor or multiplier seven. These are 32 real scans.
Neither direction uses C0, another owned field, or a native child.
There is no address map inside the common chart.

At a current input-Y cut with frame I, the constant scalar word acts
directly. At a completed-X cut, use the existing current-stage views to
obtain a common FULL chart, apply the word, then undo the views. One
conservative external count is 112 entry views and 112 exit views.
Each view consists of its ordered route and translation, so this is
448 monomial applications when those two operations are counted apart.
Their inherited address-map costs must be paid. No O(V) shortcut is
claimed for interleaved selected bits.

This access statement does not cover an old query on retired Y or an
arbitrary new physical output code. A new cut must prove its actual
view and phase identity before it uses this scalar invoice.

Exact prefix row-sum bounds, relative to the full word's input, are
20 for the forward word and 18 for the inverse. These include the pair
codes, sign changes, pivot loops, and all 112 live fields. One extra
binary fractional bit suffices for either word. A factor 64 is a safe
stored-value and unit-ADD temporary bound for either direction. This
local bound is not a guard for the complete recursive supplier.

## Exact generic division

The retained fixed-tape model evaluates a complete butterfly layer
exactly before its final truncation. It does not require every local
coefficient to be dyadic. The retained common odd grid already admits
fixed odd division, including arbitrary borrowed input values.

Let r_5 and r_7 bound additional odd height in every prefix of one
finite parent, after completed children are replaced by their proved
dyadic endpoints. One occurrence of the full E^-1 word adds at most
one to each bound, not eight. A block divides only its own pivot, once.
The other blocks act on disjoint mode coordinates. The final pair
inverse is dyadic. This proves the height statement on arbitrary input.

If D bounds the number of recursive edges in a live chain, set

```text
K_5 = r_5 (D+1),       K_7 = r_7 (D+1),
S = 5^K_5 7^K_7.
```

At the outer entrance, multiply the padded numerator of every physical
numeric record by S. This includes all arbitrary borrowed data,
helpers, and numeric work streams. Do not scale addresses, tags, or
descriptors. Use one common grid 2^-P/S and one common width throughout.
Private zero values stay zero. No local module changes the format.

Each unfinished node adds at most its local height. A completed
dyadic child adds no odd height. Thus every quotient lies on the
common grid, and every encoded numerator is divisible by the requested
odd divisor. At an outer endpoint proved Gaussian dyadic on all roles,
divide every numeric numerator by S exactly. This restores the old
encoding, including every borrowed role's required endpoint.

One real fixed-odd multiplication or division costs at most 4(w_g+1)
arithmetic-head steps per record under the retained scan convention.
The concrete carry and head-pass argument is the pinned A8 odd-grid
proof, SHA256
`e0210105ba6c6246f1f84c8ce2d92cfd07aa6cc8a161ca27d7fcc8e0183cfb01`.
For a fixed positive odd divisor d, scan the input bits from low to
high. With input bit b and carry c, division writes

```text
a = (b-c) mod 2,       c' = (c+d*a-b)/2,       c starts at 0.
```

Each transition preserves 0<=c<d. Summation gives
d*Q_unsigned=N_unsigned+2^w*c_final. For input and output sign bits
s_N and s_Q, the quotient is exact if and only if
c_final=d*s_Q-s_N. Multiplication instead writes
a=(d*b+c) mod2 and sets c'=floor((d*b+c)/2). Its final overflow test is
c_final=d*s_N-s_Q. A fixed guarded width makes this test pass for every
required multiplication. Both algorithms overwrite the numeric record
in place. The fixed carry and two sign flags use finite control.

A move to the low end, the arithmetic traversal, delimiters, and the
head return fit in four passes of at most w_g+1 cells. This is the
arithmetic-head charge. Record counters and descriptors are separate;
the coefficient four does not include them.
Descriptor and record-counter work is additional linear work. If N
counts all real records over all physical numeric streams, the two
outer conversions cost at most

```text
8 N (K_5+K_7) (w_g+1)
```

arithmetic-head steps. The added width is at most 3(K_5+K_7) bits.
If K_5=K_7=K, a direct multiplier or divisor 35 gives a smaller
alternative: 8 N K(w_g+1) head steps and at most 6K added bits.
The carry alphabet for 35 is fixed. No residue field is stored.

For n records per real field, one full local code call adds at most
128 n(w_g+1) head steps for its 32 real fixed-odd scans, plus the
separate linear stream work and its 3,420 old scalar units.

For the retained largest child ratio 48/73, the bound
D <= 2 ceil(log2(d+1)) applies. Fixed r_5,r_7 therefore add O(log d)
bits and O(V log d) outer work. A new supplier must still prove its
actual child ratios, complete endpoint, finite node bill, and binary
guard. This packet does not copy those facts from an old supplier.

The same arithmetic admits generic T^-1 with divisor 2145 when its
source is reachable. Failure of an input to belong to the dyadic
T-code forbids only the no-root-scale decoding contract. It does not
prove that the rational operation is impossible.

## Exact valid-code division and its full test

The forward code E is Gaussian dyadic. On an input E x with dyadic x,
the inverse word needs no odd root factor. In the pair basis and one
signed block, its value is D_s C_k D_s u. Undoing the signs gives C_k u.
Immediately before the inverse division, the pivot numerator is
-(k-1) times the original pivot of u. Hence the division is exact on a
binary grid. The checker verifies every such division on all input
columns.

This code image has a small exact description. Let A be the pair
code above. Let L_5 have one row for each signed six-mode sum in A
coordinates. Let L_7 have one row for each eight-clique sum. For a
Gaussian-dyadic vector z,

```text
z belongs to E R0^112
if and only if
L_5 z = 0 mod5 and L_7 z = 0 mod7,       R0=Z[i,1/2].
```

In one k-block, the inverse is z-1 sum(z)/(k-1). It is dyadic exactly
when its signed sum is divisible by k-1. The dyadic unit A transfers
that criterion to the physical coordinates. This proves necessity
and sufficiency, including Gaussian coefficients. The checker also
verifies the eight independent syndrome rows and image rank 104 at
each prime.

Consequently a dyadic middle operator M maps a source E_s code into
a target E_t code precisely when it maps each of these two reduced
source kernels into its target kernel. Equivalently, for p=5,7 there
is a reduced operator S_p such that

```text
L_(t,p) M = S_p L_(s,p) mod p.
```

The syndrome rows are surjective, so the kernel condition gives the
factor S_p. For the converse test at one prime, the Chinese remainder
theorem lifts any vector in that source kernel to one that also meets
the other prime's source condition. Thus testing the intersection of
the two integral code conditions loses no reduced input. This test
applies to the full operator on all addresses and
all roles. It is not enough to check only the data columns if M reads
arbitrary helpers. When the codes are routed, their syndrome rows
must contain those exact routes in the correct order.

The separate `TYPED-CODE-POTENTIAL.md` gives the recursion theorem when
completed children carry such codes. Matching types can prevent odd
height from being charged once for every completed sibling. A matching
codebook must be proved for the actual controller.

## Approximation and exact borrowed state

Replacing a fixed-odd inverse by a rounded binary multiplier does not
inherit exact restoration. For example, use 51/256 instead of 1/5 in
I-J_6/5. Its product with I-J_6 is I-J_6/256, not I. The checker rejects
this substitution and the corresponding seven-divisor substitution.

A quotient-and-remainder scheme can retain the missing information,
but it needs a residue for each coefficient unless it proves a way
to recompute that residue from untouched data. A constant number of
bits per record is a full stream obligation. Exact restoration must
include that stream and its erasure. No such stream or rounded scheme
is required by the exact common-grid construction above.

## Validation and scope

Run with a new output directory:

```text
python3 -I -B work/centre-encoding-campaign-20261014/lanes/native-escape-20261017/rational-code-admission-20261020/check_clique_codes.py --out /tmp/clique-codes-normal
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/native-escape-20261017/rational-code-admission-20261020/check_clique_codes.py --out /tmp/clique-codes-optimized
```

Expected status:

```text
PASS_EXACT_CLIQUE_CODES_AND_TYPED_GRID_FIXTURES
```

Compare both output files byte for byte. The checks cover source pins,
the actual signed pair basis and clique partition, every scalar event,
all data columns, arbitrary spectator values, both inverse orders,
integer-grid divisibility, valid-code divisibility, prefix bounds,
invoices, modular code tests, and signed fixed-odd division. Typed
composition fixtures and deliberate interface mismatches support the
separate proof. They do not prove a supplier's missing type identities.

The source family and native schedule are prior work of the cyclic-pair
and low-displacement lanes. The coordinating lane supplied the
one-pivot factor and the five/seven response proposal. This packet
supplies the exact common-frame implementation, grid bounds, code-image
test, and typed-code proof. The work used OpenAI Codex assistance.
No PR, commit, push, or publication was made. Before a future PR
description, read
/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md.
