# Independent review of the D25 views and FULL scalar code

The actual dimension-25 entry and exit views pass. The five scalar
code cuts in the pinned one-pair program pass. The complete common-frame
code for the new response E costs 2,396 real scalar primitives. It uses
no owned field, private field, or native child.

This review does not certify the three-factor terminal, recursive
hosting, finite precision, or a complete supplier invoice. Those are
separate obligations.

## Exact access check

The source is the DATA member of the pinned selected-replay archive.
The checker imports no producer. It reads the 73-axis route records
and checks each of the 336 stage-port records for stages 0, 1, and 2.
The first 25 columns preserve their span. The other 48 columns are
unchanged coordinate columns. Every restricted route is an orthogonal
involution and fixes its intrinsic line q.

For a list of line factors, write its character phase as a polynomial
with values in Z/4Z. The values on basis vectors fix the diagonal
coefficients. Binary polar rows fix the off-diagonal coefficients.
All phases here have zero constant coefficient. Thus equality of these
data proves equality on every character; it includes the global phase.
The checker uses this representation to verify each literal route and
translation. It does not discard the even phase.

The independent counts are 672 entry identities, 672 exit identities,
336 future-Y identities, and 672 past-X identities. Deleting the entry
translation fails in 448 cases. Deleting the exit translation fails in
448 cases. These controls reject a phase-free use of the frame labels.

The pinned controller has these five occurrences:

| Bank | Code stage | Completed or hole level |
| --- | --- | --- |
| X | 0 | 0 |
| Y | 1 | 0 |
| X | 1 | 1 |
| Y | 2 | 1 |
| X | 1 inverse | 2 |

All 560 port-cut instances belong to the checked access cones. In each
specified view, every field in the code has the same frame. Scalar
mixing is therefore valid for arbitrary field values at these cuts.
This result does not permit the same code at an arbitrary Y hole.

The all-FULL X endpoint is also checked against the actual native
payload, for both providers and both directions. No frame change is
inferred from the scalar response alone.

## Independent scalar calculation

The code matrix equals the actual native response. Its square is the
identity. It has 48 rows with four nonzero entries and 64 rows with one
nonzero entry. There are no diagonal entries.

For each two-field code, let its matrix be [[a,b],[c,d]], where all
four entries have absolute value one and d=-abc. The four operations

```text
x <- a*x
x <- x+b*y
y <- 2*d*y
y <- y+c*a*x
```

give the stated matrix on arbitrary x and y. The last row is
c*x+(2*d+c*a*b)*y=c*x+d*y. No zero input is used.

The complete 112-field word consists of the pair codes, a signed
permutation in those coordinates, the inverse pair codes, and the
64-port negative permutation. The four prices are 470, 624, 470,
and 832. Their sum is 2,396. The literal census is 264 complex ADDs
and 120 complex SCALEs. Forward row replay and a separate reverse
column replay both give the full response. Applying the complete
literal word twice gives the identity. Omitting the inverse pair
code gives a different matrix.

The exact largest prefix row one-norm is four. This is a local
coefficient growth bound, not a finite precision proof.

Each routed application has a conservative allowance of 224 monomial
view calls. Those calls are separate from its scalar price. The five
controller codes cost 11,980 scalar primitives, which is 1,360 less
than five copies of the prior 2,668-primitive word. This subtraction
does not establish a complete supplier improvement.

## Reproduction and provenance

Run from the workspace root:

```text
python3 -I -B work/centre-encoding-campaign-20261014/lanes/bridge-review-20261017/matched-stage-review-20261018/check_access.py
python3 -I -B -O work/centre-encoding-campaign-20261014/lanes/bridge-review-20261017/matched-stage-review-20261018/check_access.py
```

Both runs must report:

```text
PASS_INDEPENDENT_MATCHED_D25_ACCESS_AND_FULL_GAUGE
```

The receipts must have equal bytes. ACCESS-REVIEW.json contains the
source pins and exact counts. ACCESS-FREEZE.json preserves this review
separately from later terminal work.

The bridge-access lane supplied the physical views. The independent
review lane supplied the cheaper scalar word. The oblique and controller
lanes supplied the native matched response, and the history lane supplied
its permutation64 part. The encoded-controller lane supplied the five
code cuts. This review used OpenAI Codex assistance. It made no PR,
commit, or push.

Before a future PR description, read
/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md.
