# Independent proof, source, and cost review of the cutoff prefix

**Result: PASS for the stated interface and added control costs.** This is a
proof/source review complementary to the root reviewer's separately implemented
dense CPU. I did not run the author's `verify.py` or use its machine execution as
independent evidence. No author files were changed.

## Reviewed snapshot

Canonical source base: `e54523517d0f03e58352e647c403a5af3e525a57`.
The input controller is the published CubeJerry fork package at
`9dfe6747b8553fd11b408f2b045c5954ef1e6eaa`.

| File | SHA-256 |
| --- | --- |
| `cutoff_prefix.py` | `1f67f85d14f472e94e05072c4d9840ff9b79ee7d944e2fb1699c44e4b9b8687d` |
| `PROOF.md` | `5cfa6f6c0a3c3eca790c7c155dcdff3b769dc320d3a5a9a31c7356cfe2d72262` |
| `SOURCES.json` | `aa19dd4d24a2d760fbc2d5168bc44dddb221276b09fecef1278b2b5a5aa00830` |
| `inputs/controller_reference.py` | `e664a748e6b6797d4b60f60a7a7dd68b59a5608acf56b9c5d8b466f363755f73` |
| `inputs/selected_control.py` | `1c977e9f4864d338f874aa4943d9f3422d964c3ab0cc2f877d9bc4c2d9e20237` |

## Actual source binding

I read the pinned `FULL-RESULT.json` and `interval_gate.py`, not merely this
package's interpretation. The claim/tested fractions differ by
`7/100000000000000`; the gate divides that difference by seven and sets
`ep=1-g`, `stop=g`. Thus `Q=100000000000000`, stopping exponent `1/Q`, and
`epsilon=1-1/Q` are the actual coupled values. `be=1-3*g` is a different
parameter. The stopping formulas in `notes/batched-complex-rows.tex` identify
the exponent through both the internal and leaf costs and require the strict
leaf test `e<d^beta`.

I read the full interface around the header in `05-layers.tex`: it starts
`Gamma(p)Gamma(d)`, promises `d<=b_d*p^epsilon`, `1<=D_total<=d`,
`|E|<=C_desc*p`, `w>=p+2`, and has volume `V=2*M*r*w`. I also checked the actual
Gamma convention in `02-streams.tex` and the selected application review's
reserved-axis treatment in its section 5. The supplied WIDTH is consequently
a retained premise; this prefix does not produce or validate the reserved-axis
calculation. All six mathematical source files used here match their recorded
Git blobs and SHA-256 values. The local preexisting copy of the complex note
has one extra terminal newline; removing exactly that extra byte gives the
recorded 6,085-byte blob `e13bd96eb29bdc6526f10dc32e0a146bc17848a4`.

## Saturation and trial proof

For positive operand lengths `a,b<=d`, write `z=min(a*b,d)`. The literal
multiply loop increments D and PRODUCT once per emitted symbol, so it emits
exactly `z` symbols. Testing D before the factor-end branch correctly stops
even at a row boundary. No input symbol is changed. Each operand head is at
an inspected prefix when its rewind starts.

An independent instruction recount gives a sharper exact helper count:

* If `d>a*b`, the count is `16*z+11*a+13`.
* If `d<=a*b`, put `r=floor((z-1)/b)`; the count is `16*z+11*r+14`.

The branches include the final failed read and all four rewinds. Since
`z>=max(a,b)` and `r<z`, both satisfy the author's `40*z+40` envelope. The
positivity and `a,b<=d` hypotheses are essential to the rewind and operand
copy charges, and every nonsentinel trial satisfies them.

The separately recounted stream helpers have costs `7*n+4` for erase,
`11*n+7` for copy, `12*n+7` for move/erase, and `16*n+5*delta+7` for doubling
with one optional bit. A whole power step is therefore at most `77*z+62`,
which is at most `160*d` for `d>=1`. Saturation is compatible with successive
squares and multiplies because truncation at d commutes with multiplication
of positive integers followed by truncation. Reading the fixed binary
expansion of Q therefore produces exactly `min(t^Q,d)`.

The Gamma decoder implements `v <- 2*v+delta`; the preceding binary prefix
values have sum less than d. Its unary work is consequently O(d), not
O(d log d). The length guide is consumed exactly, and TRACE records every
HEADER right move. Reversing TRACE restores the borrowed header head without
reading the following field or the region preceding the first Gamma code.

The candidate test reads CUTOFF before WIDTH. Equal length is tested by the
power routine, while exhaustion of WIDTH first is exactly the `e+1`
sentinel. Failed candidates increase by one, hence the accepted value is
`C=min(ceil(d^(1/Q)),e+1)`. There are at most C power tests. Since the positive
integer d itself has `d^Q>=d`, `C<=ceil(d^(1/Q))<=d`; thus `C^2<=d*C` pays for
the growing trial scans. At every descendant `x<=e`, capping the cutoff at
`e+1` leaves `x<max(N,C)` equivalent to `x<max(N,ceil(d^(1/Q)))`, including
the equality/perfect-power case.

## Literal joining and historical backing

`relocate` changes precisely the literal jump targets. Each predecessor has
one halt, and the code explicitly checks this before replacing those halts
by jumps to the next fragment. Prefix execution leaves a marked unary
CUTOFF and restores the other ten tapes to their entry contents and heads.
The selected controller touches only its original four tapes and restores
them. Retirement erases the cutoff and its owned guard, so all eleven entry
states are restored. The initially blank owned guards are written and
erased physically; they are not supplied delimiter oracles. Ancestor cells
below those guards are never crossed.

I independently bounded the new visited intervals by `e+2` each for WIDTH
and CHILD, `C+2` for CUTOFF, `e*N/(N-1)+depth+2` for STACK, `h+1` for HEADER,
`h+2` each for TRACE and LENGTH, and `d+2` each for D, ACC, FACTOR, PRODUCT.
Using `depth<=e-1` and `C<=d`, even their sum is at most
`(3+N/(N-1))*e+5*d+3*h+20`. This is within the published, looser bound
`K0+(5+N/(N-1))*e+5*d+4*h+40`. Including K0 retains all historical entry
backing, and erased cells are not treated as freed capacity. In particular,
the unary decoded d remains an O(d) historical charge when `d` greatly
exceeds the active width e.

The recounted helper costs, at most C trials, guide/trace work, fixed marker
operations, retirement, linking jumps, and halt fit
`1000*(R_Q+1)*(h+d*C+1)`. The unchanged selected control costs remain a
separate `200*(P+1)*sum_v e_v` charge. `R_Q=bit_length(Q)+popcount(Q)=64` is
fixed program data, not a run-time exponent register.

## Complete added budget and limits

With the actual source parameters,
`d*C <= d^(1+1/Q)+d = O(p^((1-1/Q)*(1+1/Q)))+O(p^(1-1/Q)) = O(p)`.
Also `h<=|E|=O(p)`, so the added prefix and retirement cost O_Q(p) and the
new historical backing is O(p). A nonempty complete array has
`V=2*M*r*w>=2*(p+2)`, which pays this as an O_Q(V) root setup charge. The
prefix runs once around the complete recursion, not once per visited node.
The inequality would not follow from an arbitrary `epsilon<1`; the exact
coupling just checked is necessary for this particular budget argument.

This supplies a literal control prefix for the promised valid header and
already produced positive active WIDTH. It does not produce the final
astronomical native manifest, root row grants, payload/remainder consumers,
or the analytic/native services. The five foundational assumptions and the
accepted conditional kappa remain unchanged. No new complete kappa and no
unconditional multiplication theorem are claimed.

Prepared independently by the compiler research worker for CubeJerry with
substantial OpenAI assistance. The precursor selected-controller review and
the root's independent joined-machine test are complementary evidence,
not replacements for the source and universal cost arguments above.
