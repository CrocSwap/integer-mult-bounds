# Independent fixed-interval response-rank audit

Prepared for @CubeJerry with substantial OpenAI assistance. This is a separate
shared-context AI check, not human review or proof-kernel admission.

## Actual source check

`check_covectors.py` imports no predecessor evaluator or matrix routine. It
authenticates the original #6937 source blob
`5a71ca9f80ced1aeb8a68e97516cab52eb72a52a` at commit
`a98df73ddae1d1ea85a62b6bdf2714b28cb7b359`, and the attainment blob
`cf55f4271009a06ad192a070d330a4466b6d44fa` at public commit
`617903497387a98f7ca929ad0b6928dd32abffec`. It applies literal transposed
operations in reverse order to output covectors 0, 1 and 19, keeping all 76
input coordinates and using exact rational arithmetic.

For the exact original events `[457:576]`, its response at q=+1 minus q=-1,
with D9=1, has the claimed rows/columns 0,1,19 minor

```
[-2 -4  0]
[ 0 -2  0]
[ 0  0  2]
```

with determinant 8. LAMBDA specializes to 1 at both signs directly from
its even polynomial; the interval's only IDLE_ONE contains D9. No other
D_j is specialized or occurs in this interval. The replacement has exactly
223 rows, leaves both external event segments unchanged, contains exactly
three QUERY operations, and has no QSELF. All six complete reverse covectors
agree at these two specializations. This finite two-point comparison is not
a substitute for the predecessor's formal replacement-identity proof.

Deleting each of the three charged original sites or each of the three
attainment queries makes this response minor singular: six negative controls.
Normal and optimized Python runs both passed and produced identical receipts.

## Mathematical scope review

Let the chosen full finite state include every auxiliary register and one
homogeneous constant coordinate. Every fixed affine instruction is then a
linear map on that state. The initial embedding and output extraction are
the same at both evaluations by premise; they may have arbitrary rank.
If a fixed finite instruction stream changes register dimensions, padding
all registers to their finite union gives the same conclusion without any
invertibility assumption.

At the two legal evaluations, a charged rank-one QUERY has matrix difference
of rank at most one. The same holds for an even-conjugated version because
its two surrounding free matrices agree at the evaluations. The telescoping
identity for the difference of the two whole matrix products is a sum of
one term per charged site; each term has rank at most one after all prefix,
suffix, initialization and extraction maps. Therefore the response rank is
at most the number of queries. Copy, erase, auxiliary initialization and
noninvertible maps do not invalidate this argument. The exhibited determinant
8 proves at least three queries in this model over characteristic zero.

The declared coefficient ring Q(i)[q,D1,...,D18]/(q^4-1), with no additional
q/D relations and all free denominators regular at both signs, makes both
evaluations legitimate. The claim must retain the following restrictions:
independent inputs at the fixed interval boundary; fixed, data-independent
linear/affine control; identical free initialization and extraction at both
signs; no free odd-q side information; and rank-one charged operations on
the entire chosen state, rather than an unpriced wider payload operation.
A reachable-input subspace, nonlinear or adaptive coefficient generation,
changed endpoints, or extra relations excluding a sign could defeat this
particular lower bound and are outside the statement. There is no issue
with q^4-1 having multiple components: the proof uses two lawful evaluations
into Q(i), not a rank calculation over the quotient ring itself.

The rank argument is classical. The new source-specific fact is the exact
minor, and hence three-query optimality for this interval in the stated
model together with the separately proved three-query attainment.

## Reproduction

```sh
python3 -I -B check_covectors.py /path/to/research/p104-query-only-interval
python3 -I -O -B check_covectors.py /path/to/research/p104-query-only-interval
```

Expected: the exact JSON receipt in `RESULT.json`; determinant `8`, all six
attainment covectors equal, and all six deleted-site determinants `0`.
