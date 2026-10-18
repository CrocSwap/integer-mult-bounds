# Scalar-prefix grid and signed-range certificate

## Exact object

Fix one reconstructed PR3076 emitted program and orientation. Initially
`L_r = x_(r,empty)` for 632 live rows. Atoms `x_(r,w)` are independent signed
integer variables indexed by an input register and reduced free-group warp
word. A warp left-prepends its symbol and cancels the adjacent inverse. It is
a bijection on atoms. Coefficients are rational dyadics. Zero buffers start
zero. Scalar COPY, CLEAR, SCALE and ADD have their literal algebraic meanings.

This is the formal module used by the retained scalar identity check, not a
simulation of native adapters, climbs or centre transforms. A fixed assignment
to the whole atom family evaluates every prefix coherently. Independence can
also be realized by functions on the free group and its shift permutations.
This is broader than the actual finite native representation, which can
impose relations between words and coordinates.

`prefixes` maintains a dictionary for each row. ADD collects equal atoms and
removes zero coefficients; warp reduces adjacent inverses exactly. Induction
on events proves each yielded row is its formal linear combination.
Unchanged rows retain their last checked value, so initial rows and changed
rows cover every chronological cut. The separate final check demands the
exact forward or dual update, dirty-input return and private zero returns.

## Least shared dyadic grid

For `y = sum c_j x_j`, define its depth as the largest exponent of two in a
reduced coefficient denominator, or zero for the zero row. Let D be the maximum
over initial and changed rows. Encoding y as `2^D y` makes every prefix
integral for all integer atom assignments. Conversely, if a coefficient has
reduced denominator `2^D`, setting that atom to one and all others to zero
makes the D-1 encoding nonintegral. This proves necessity and sufficiency
within the common-grid contract.

The measured maxima are D=4 forward and D=5 dual for both providers. The
receipt retains a deepest row and its event. Its one-atom assignment is
allowed by the signed 64-bit input box. The verifier rejects D-1
arithmetically, without relying on a receipt hash.

At `T' = T + q S`, both encoded endpoint rows are integral. Therefore
`2^D q S = 2^D T' - 2^D T` is integral. For reduced `q=n/d`, coprimality
proves d divides the encoded source `2^D S`, establishing PR3080's ADD
divisibility premise. The implementation also computes and hashes every
increment row and checks its depth is at most D. That diagnostic is redundant
with complete prefix coverage, but detects missing coverage.

The increment itself need not fit in the signed width. PR3080 adds modulo
`2^W`; stored source, prior target and final target need the signed bounds.
Signed-power partial sums may wrap.

## Least signed endpoint width at P=64 and the least common grid

Let every independent atom lie in `[-L,L-1]`, with `L=2^(P-1)`. For a row,
let `C+` sum its positive coefficients and `C-` sum the absolute values of
its negative coefficients. Independence gives exact extrema

```text
low  = -L*C+ - (L-1)*C-
high = (L-1)*C+ + L*C-
```

Choose each atom's endpoint according to its coefficient sign to attain
these values. This treats the asymmetric negative signed endpoint explicitly;
negating the minimum input need not fit in P bits. Multiply by `2^D`, giving
integer endpoints. For `E = max(high+1, -low, 1)`, the least signed width is
`1 + ceil(log2 E)`, computed by integer bit length. Take extrema over all
changed rows and the initial box.

At P=64 the unscaled global extrema are

```text
forward: [-2785458355130142293828, 2785458355130142293902]
dual:    [-1558749874228457111531, 1558749874228457111404]
```

After encoding with D=4 or D=5 respectively, both require W=77. Retained
sign-extremal assignments exceed the 76-bit signed interval. The verifier
evaluates before-target, source and after-target rows under the same atom
assignment, checks source divisibility and executes PR3080's literal 77-bit
ADD circuit. Its executor checks the exact endpoint, source preservation
and clean-carry return.

The maximal row l1 norms are 302 and 169. The symmetric `abs(y) <= L*norm`
bound also gives 77 bits at P=64, so asymmetric endpoints do not improve
this width. The cancellation-blind control propagates nonnegative norms and
unreduced denominator bounds without subtracting equal atoms. It is a
sufficient bound in the same model and gives 195/202 bits. It is not a
benchmark of an upstream backend.

## Physical implication and limits

If a native interpretation realizes each atom as a signed integer coordinate
in this input box, and intervening native operations commute with the
interpretation without grid/range loss, the format bound is sufficient for
its scalar ADD layer. Signed coordinate permutations preserve the symmetric
box `abs(x) <= L`, but need not preserve `[-L,L-1]`: negating the minimum
input produces +L. For that interpretation use the symmetric row-norm bound,
which also gives 77 bits here, rather than claiming the asymmetric extrema
bound every physical phase assignment. The dyadic grid remains sufficient
for integer atoms in either box. Sharpness need not survive native relations.

This package does not prove that premise for emitted adapters, climbs,
centre transforms or physical warp implementations. A scalar W-bit register
alone cannot implement an arbitrary formal warp; its coordinate array,
movement and backing need their own realization. Non-ADD execution,
clean-space, precision, stock, all-size, supplier and outer admission remain
open. Abstract CLEAR/zero-return semantics are not a new physical erasure
proof. This is a finite formal coefficient-format certificate and conditional
interface lemma, not a complete multiplication theorem or new kappa.
