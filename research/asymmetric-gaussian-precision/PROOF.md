# Asymmetric accuracy for normalized convolution

This scoped proof was produced by Nick Petalas. Apache-2.0.

## Contract and new conclusion

Take the normalized channel in Jerry Chen / CubeJerry's
[#6993](https://github.com/CrocSwap/integer-mult-bounds/pull/6993), retained at
`research/deferred-gaussian-recovery/PROOF.md`, sections 2-4. Its exact
Fourier identity, source interfaces and physical endpoints are premises.
They are not reverified here. Cinna Davis's #4100 supplies the construction
and exact source definitions. Ryanson Jonathan's #4320 supplies the
identity/recovery audit, and his #4415 supplies the predecessor one-middle
error ledger. #6993 retains the further native,
scalar, source, codec and Fourier attribution in its NOTICE.md.

Let b >= 1 and Gamma >= 0 be integers, and let 1 <= S < 2^b. Set

    h = ceil(log2 S), a = 2h + 2b + 7,
    epsilon = 2^-a, lambda = 2^-Gamma.

All vector norms in the argument are the maximum complex modulus. The two
ideal forward maps and the ideal opposite map are lambda times maps with
operator norm at most one. Their exact composition with pointwise product
is the inherited normalized convolution, with accumulated scale lambda^3.
The original input vectors have norm at most 1/4.

Suppose the approximate forward calls have errors at most lambda epsilon
on those inputs. Suppose the approximate opposite call has error at most
lambda^3 epsilon on every admitted quarter-disk input, including its
actual rounded input. Keep the original common q grid, with

    q >= a + 3Gamma + 7,

and retain every additional source, reference, native and ledger guard.
The pointwise operation multiplies exactly and truncates each real and
imaginary component toward zero once on that grid. No other uncharged
rounding operation is allowed.

Then every forward return has norm below 1/2, the actual pointwise result
has norm below 1/4, and the opposite return has norm below 1/2. The final
error after multiplying by S^2 2^(2b+4+3Gamma) is strictly below 1/4.
Consequently the same final nearest-integer gate remains valid.

The new forward-map tolerance is lambda epsilon, replacing #6993's
lambda^3 epsilon. It is larger by exactly 2^(2Gamma). This is an accuracy
allocation result, conditional on delivering the named maps. It asserts
no reduction in the common q grid or completed physical cost.

## Separate the four error sources

Write U,V for the ideal forward returns and Uhat,Vhat for the approximate
ones. More generally, allow forward errors alpha,beta, pointwise error
delta, and opposite error omega. Since |U|,|V| <= lambda/4,

    ||Uhat Vhat - UV||
        <= (lambda/4)(alpha+beta) + alpha beta.

Multiplication is coordinatewise. Apply the ideal opposite map to the
actual rounded product first. Its operator norm is at most lambda. The
opposite algorithm's error is then charged at that actual input. The
complete error E in the normalized final result satisfies

    E <= lambda[(lambda/4)(alpha+beta) + alpha beta + delta] + omega.   (1)

This argument does not require the approximate routines to be linear or
contractive. Their error promises must hold on the reached input domains.

Substitute alpha=beta=lambda epsilon and omega=lambda^3 epsilon. Each
component truncation has error below 2^-q, so the complex modulus error
satisfies delta < sqrt(2) 2^-q < 2^(1-q). The q guard gives

    delta < lambda^3 epsilon/64.

Divide (1) by lambda^3 to obtain

    E/lambda^3 < epsilon(3/2 + epsilon + lambda/64)
                 <= epsilon(3/2 + 1/512 + 1/64)
                  = (777/512)epsilon < 2epsilon.                    (2)

Here a >= 9, including S=1, b=1 and Gamma=0. The larger forward error is
attenuated once by the other forward output and once by the opposite map.
The opposite algorithm's own error has neither attenuation factor.

## Verify the actual input and return radii

Each approximate forward return has norm at most

    lambda(1/4+epsilon) <= 129/512 < 1/2.

The actual rounded product has norm strictly below

    lambda^2(1/4+epsilon)^2 + lambda^3 epsilon/64
        <= (129/512)^2 + 1/32768
         = 16649/262144 < 1/4.                                    (3)

Thus the opposite error promise used in (1) applies to its actual input.
Its return norm is strictly below

    lambda(16649/262144) + lambda^3 epsilon
        <= 17161/262144 < 1/2.

These are the same interface radii required by #6993. In particular Gamma=0
requires no separate limiting argument. The native half-disk carrier
checks remain applicable, and the pointwise quarter-disk guard is preserved.

## Recover the integers at the unchanged scale

Keep both exact S multiplications and the complete shift 2b+4+3Gamma.
By (2), the error after this restoration satisfies

    E S^2 2^(2b+4+3Gamma)
        < 2epsilon S^2 2^(2b+4)
         = S^2 2^(-2h-2) <= 1/4.

The first inequality is strict even when S=2^h. The exact convolution
coefficient is real, so projection to its real component cannot increase
the error. Nearest-integer recovery is unambiguous. The source identity,
original-coordinate extraction, CRT and carry obligations remain inherited.

## Translate the improvement into stage requests

The three public stages of each transform are expansion, middle and
compression. Use the same source-interface implication as #6993, section 3:
if each stage has restored error below 2^-tau, then the complete normalized
map error is below 3*2^(-tau-Gamma). Every actual finite applicability guard
in that implication must still pass for that call.

The previous request for every call was tau_old=a+2Gamma+2. Replace it by

    tau_forward = a+2, for each of the two forward calls,
    tau_opposite = a+2Gamma+2, for the opposite call.

Then the forward-stage sum is below 3lambda epsilon/4, and the opposite-stage
sum is below 3lambda^3 epsilon/4. Both fit the map budgets used above. Each
forward stage therefore requests exactly 2Gamma fewer accuracy bits. At
Gamma=0 the requests coincide.

For each forward call independently, the same substitutions in #6993 give

    z_forward = tau_forward + Gamma + ceil(log2 m) + 1,
    chi_forward = Gamma + tau_forward,
    tau_comp_forward = tau_forward + K_f.

The last equality preserves the compression-only normalization K_c, since
Gamma=K_f+K_c. The analogous opposite requests retain tau_opposite. These
are requests to separately prepared stage implementations, not a license
to reuse an old phase bank at a different declared accuracy. Preserve the
source-first ordering and all finite radius, normalizer, coefficient, q and
reference gates. A changed reference can change its derived parameters;
this proof does not assert that a previously admitted reference remains
admitted without checking its new declaration.

The old q lower bound remains sufficient for the new forward source rule
q >= Gamma+tau_forward+5, because it is stronger by 2Gamma. Other guards
can still dominate. A maximum with the fixed q or another width can erase
a physical width reduction. The proved improvement is in requested
accuracy, with no unconditional storage, runtime or kappa improvement.

## Why the opposite tolerance is retained

The distinction is necessary in this error-only model. Take S=1, b=1,
Gamma=1, zero inputs, exact forward and pointwise operations, and an
opposite return error lambda epsilon. These satisfy the hypothetical
looser opposite tolerance. Here a=9 and restoration multiplies by 512, so
the final error is exactly 1/2. It fails the strict 1/4 recovery contract.
The retained opposite tolerance lambda^3 epsilon excludes this example.
This is a counterexample to relaxing all calls alike, not an error in #6993.

Equation (1) is also exact in the scalar abstract additive-defect model:
use input values 1/4, ideal scalar maps multiplication by lambda, and align
all four nonnegative defects on the real axis. This equality only concerns
that abstract model. A freely signed pointwise defect is more permissive
than the actual inward truncator, and no sharpness claim for that truncator
or physical native algorithms follows.

## Scope and verification

The universal conclusion follows from the written inequalities. The
standard-library verifier supplies finite rational corroboration. It checks
separate budgets, exact length-1/2/4 convolution fixtures with literal
componentwise inward truncation, abstract scalar equalities and controls.
Its length-2/4 fixtures illustrate the norm contract; they are not the odd
production source domains. It imports no predecessor scientific verifier.

All five selected framework assumptions remain. There is no production
transform, new native word, physical controller, supplier admission,
complete multiplication theorem or selected-frontier change. Independent
human and formal proof-kernel review are unclaimed.
