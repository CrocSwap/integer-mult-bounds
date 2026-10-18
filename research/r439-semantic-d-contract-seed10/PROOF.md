# A semantic zero-frame preconditioner for the interleaved scalar lemma

## Contract

Let M be any module over F2, including arbitrary finite or infinite F2-valued streams under pointwise addition. There are source coordinates x in M^v, target coordinates y in M^v and helper coordinates h in M^R. Every source, target and helper value is arbitrary; helpers are not initialized to zero.

Replace the old target-only D syntax by the following contract H2-sem:

1. Targets and helpers enter D at the zero frame. Every D gate uses that frame and has distinct destination/source operands drawn only from targets and helpers. There are no COPY, ERASE, recursive child, allocation or frame-change events inside D.
2. Retain the inherited H1 prohibition on a target feeding a source or helper, including inside D. Other target-to-target and helper-to-helper additions are allowed.
3. The complete D operator is exactly (x,y,h) -> (x,y+N h,h) for a specified binary v-by-R matrix N.

Condition 3 is a full boundary equation. It requires source and helper identity rows, target identity on all target input columns, no source-to-target contribution, and the stated helper-to-target response. Checking only zero-helper inputs or only target outputs does not establish it.

The old H2 implies this contract by summing each target's direct helper reads. The converse fails: h0 += h1; y += h0; h0 += h1 obeys H2-sem with N=[1,1] and restores both arbitrary helpers, but violates target-only syntax. Thus this is an actual enlargement of the admissible scalar preconditioner class.

## Substitution theorem

Retain the inherited conditions on W0=(A,scatter,B) and cleanup C:

- H1: no target feeds a source/helper;
- H3: the original A/scatter/B operand restrictions;
- H4: C reverses the z-destination gates of A then B at the common full frame, where z=(x,h);
- H5: the target-to-target block V of W0 is the identity.

The raw scalar word consequently has the block form

    z' = U z,       y' = V y + J x + K h.

The separately checked raw source-response condition is J=I. H4 supplies C=U^-1 on z and leaves y unchanged. These are precisely the predecessor's checked U, J and C conclusions; H1-H5 alone are not asserted to imply J=I for an arbitrary word.

With the new preconditioner, the complete output before C is

    z' = U z,       y' = V y + J x + (V N + K) h.

After C, sources/helpers are restored. With V=J=I, the final target is y+x+(N+K)h. Therefore the desired arbitrary-dirty boundary (x,y,h)->(x,y+x,h) holds exactly when N=K. This replaces the old syntactic sum-of-helper-reads comparison by the semantic D matrix. Necessity follows already on singleton helper assignments in M=F2; sufficiency holds for every F2 module M.

No normal-form rewrite is executed or priced. The semantic D implementation runs as given. The elementary block algebra is standard and credited to the original scalar-interface lineage; the contribution is this precise substitution contract and its source-bound application to an existing syntactically rejected word.

## Chronological substitution bridge

The block calculation above is a scalar identity. Applying it to a framed/interleaved supplier also requires a bridge to the inherited chronological lemma; a raw endpoint equality alone must not silently turn frame-sensitive A/B operations into a uniform matrix on arbitrary streams.

Construct a proof-only virtual word with the candidate's literal A, scatter, B and C, but the original PR589 target-only D. The unchanged predecessor checker must pass every H1-H5 hypothesis and every U/J/K/C conclusion on this splice, as well as its finite geometry and endpoint checks. This invokes the old scalar/interleaved lemma on a word satisfying its original syntax. The verifier records all bridge flags explicitly.

The actual D and virtual D have the same complete operator (x,y,h) -> (x,y+N h,h). Both operate wholly at the common zero frame, with no child, COPY/ERASE, allocation or frame-change events, and finish with identical values and frames. Equality over F2 therefore makes these D prefixes pointwise identical on every compatible input stream. Replace only that initial prefix. The remaining literal continuation, including its later chronological interleaving, receives exactly the same state and frames and is left unchanged. This transfers the inherited conclusion without rearranging any later operation or interpreting W0 independently as a frame-free stream operator.

The virtual D is a proof device; it is neither executed nor priced in the candidate. Accounting below uses the actual candidate D. The inherited common-frame and chronological realization premises remain explicit.

## Why a finite binary matrix certifies the D substitution for all streams

An elementary XOR gate is an elementary matrix over F2. A finite product has coefficients in F2, and its action on M^n is obtained by applying those same coefficients to elements of M. For the two zero-frame D prefixes, equality of their coefficient matrices therefore gives equality on every M. It is not necessary to test each possible bit-string length. Conversely, all n input basis columns in F2 determine the complete coefficient matrix, including arbitrary helper dirt.

Zero-frame placement matters separately: it ensures that D has no address-transform climb or recursive call, and its legal source-free operands share the unchanged entry-frame contract. The module argument does not justify moving the same circuit to a nonzero frame or reading a source at its own line frame. Those are rejected explicitly.

This is a uniform scalar-interface lemma, conditional on the inherited interpretation of common zero-frame additions. It does not independently establish the all-size physical compiler, rounding/tape behavior, hosting, native Gram/phase checks or analytic multiplication theorem. A changed implementation can have larger intermediate integer envelopes despite an identical binary endpoint; the package recomputes both positive guards instead of inferring them from this lemma.

## Application and independent evidence

The pinned PR1062 candidate retains v=111, R=439 and the original PR589 sources, labels, start/final frames, retained totals and scatter. It changes B,C,D as already credited to its authors. The unchanged checker validates all finite geometry and full F2 endpoints and reports exactly two failures: syntactic H2 and syntactic K_equals_D. All other inherited hypothesis/conclusion flags pass.

Our row engine computes D's full 661-by-661 operator and extracts N. An independent input-column engine executes all 661 columns as numeric bit vectors and obtains the same N. N also equals the original PR589 preconditioner's matrix and the actual helper response K of the candidate's raw A/scatter/B word. The proof-only original-D splice passes every original interface flag. The actual complete literal COPY/ERASE program is replayed forward and backward, including all source, target and helper inputs and the clean allocated copy temporary.

Every register's ordered frame path and every COPY rank agrees with PR589. The local profile is {1:1323,2:1342,3:79,4:44,5:102,6:11,7:19}, rank mass 5129, with nine rank-seven COPYs and nine ERASEs. The candidate's 11500 ADDs, including 5548 D ADDs, are predecessor savings, not new savings here. Positive bounds F=25717 and B=5911840 give strict local and nine-stage integers below 2^104 and2^192, with bit lengths 95 and 182. Exact integers are retained in RESULT.json.

Six negative controls reject neutral forbidden target feedback, neutral forbidden source access, a nonzero frame, an unrestored helper, residual target mixing and a wrong compensation column invisible on zero-helper inputs. A positive restored-helper circuit demonstrates the extension is nonempty. Source-inventory, duplicate/nonfinite JSON, source-mutation and typed-receipt controls exercise packaging separately.
