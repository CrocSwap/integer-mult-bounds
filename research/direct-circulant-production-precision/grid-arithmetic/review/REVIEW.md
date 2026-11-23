# Independent review of the supplied private-grid arithmetic bridge

**Status: accepted in the stated local, conditional scope.** Prepared for Jerry Chen / @CubeJerry by a separate orchestrating review context with substantial OpenAI assistance. This is model-assisted mathematical and source review, not independent human peer review or proof-kernel admission.

Accepted author proof SHA-256: `05e85b54fd4b8f834f1790ff18ca53f5cd05aaf58e316aef4ba72aabe2b7fa9a`.

Accepted arithmetic program SHA-256: `cce97fcc515e3240224cada0a25c666fbac13454135b4fd71589f30bf67b3184`.

The proof retains the exact #7849 caller, the published `spectral-downset` precision theorem, the native-H interface and the surrounding ownership/transport obligations. It does not strengthen the canonical assumption status or change the selected kappa.

## Mathematical assessment

The source rounds an integer product numerator n to the unique integer z satisfying `-q <= 2(n-q*z) < q`, with q=2^P. The half-open interval settles both positive and negative ties toward positive infinity. This differs from the coefficient converter's ties-to-even rule. The separate review checks that distinction directly rather than assuming the two uses of rounding are interchangeable. Identity shortcuts satisfy the same interval certificate.

For signed B-bit inputs, put M=2^(B-1). Each exact real product has magnitude at most M^2. The binary multiplier retains at most M^2 in its growing term and partial sum when the multiplier is nonzero. A zero multiplier must be handled separately: the initialized growing term can be M even though the product is zero, but no loop executes and it still fits. The author corrected this wording before the accepted proof was frozen. Two products and the positive half-grid bias have magnitude at most `2M^2+M < 4M^2`, since B>=2. Thus signed width W=2B+1 covers every arithmetic value, including the most-negative input's positive magnitude and the full imaginary sum before rounding. A right shift then cannot create overflow.

The seven-register schedule is complete for this supplied arithmetic task: two outputs, one row accumulator, one offset, and three multiplication registers. It retains all four B-bit input components until both outputs are ready. Accordingly its local live data bill is `4B+7W = 18B+7` bits, plus logarithmic control. Signs, loop indices and the word-width parameters fit that control allowance. This is a written register schedule, not a measurement of the Python diagnostic's heap. Destructive zeroing is stated explicitly; reversible uncomputation and return of a dirty owned region are not derived.

The all-size caller bridge is sound under the retained precision theorem. Every rounded table factor is bounded by F_i=2b_i>=2. Expanding the right-associated rounded recurrence gives the product of the F_i plus proper suffix products. Normalizing by the positive upper bounds, rather than by actual factors, produces a geometric sum below one. This proves the factor-cache cap even when actual factors vanish. The pinned odometer refreshes each affected suffix from current factors, so the number of prior records does not enter that bound.

For data states, taking the finite maximum Z of the computed run gives `Z <= R/2 + a(1+Z)`, where a=J*M0*epsilon<1/4 and R>=1. Hence `(R/2+a)/(1-a) <= R`; the argument does not assume the conclusion as a loop invariant. During the source diagonal scan, complete coordinates are old or new stage coordinates. Combining this with the coefficient-cache cap proves `B=P+max(A,E)+3`. In particular P<=B-3, and the supplied rational coefficient denominator and numerators meet C=B in the predecessor theorem. The sharper common-grid bound therefore applies to every `product_diagonal` multiplication while leaving coefficient conversion, H, public truncation/product, routing and event order untouched.

The quadratic local bit cost is honest. It proves an available local arithmetic implementation; it does not establish the accelerated tariff needed by the full multiplication recurrence. No claim that this replacement preserves that asymptotic price is accepted here.

## Independent executable evidence

`independent.py` imports the arithmetic program as the subject under test, but imports neither the author's checker nor its expected outputs. It authenticates the retained inputs and extracts the literal `Grid` and `product_diagonal` definitions. Its result oracle uses the half-open integer interval above and an independently expressed rational ceiling. It checks 39,220 arithmetic cases, including 18,716 halfway components and 8,628 cases with a zero real multiplier component. Wide signed inputs extend through B=4924; the largest observed arithmetic word has 9849 bits.

A separate mixed-radix position enumeration constructs each coefficient as a right-associated product at the current coordinate. This agrees with 15 literal odometer scans containing 1,020 multiplication calls. Twenty-eight parameter bindings check the published precision API, strict bootstrap numerator and both signed-width margins, including a 129-axis case. Adverse controls reject incorrect negative-tie rounding, an imaginary subtraction, rounding the separate products before addition, substituting ties-to-even coefficient rounding, and a one-bit-short register schedule.

Both the normal and optimized reviewer commands pass and produce identical scientific JSON. The commands are:

```sh
python3 -IB review/independent.py --source . --output /tmp/grid-independent.json
python3 -I -O -B review/independent.py --source . --output /tmp/grid-independent-optimized.json
```

The expected marker is `PASS_INDEPENDENT_GRID_CALLER_REVIEW`. These finite checks corroborate the written all-size proof and source binding; they do not prove the universal claim by exhaustive sampling.

## Source and execution boundaries

The extracted expression fixtures supply Python `operator.mul` as an exact-integer helper. They do not claim to execute the retained `word_product` tape machine or its complete instruction schedule. The separately proved local multiplier is the new supplied-word construction; its physical caller transport remains retained.

The `(2,)` side, five-digit-bit example is an admissible explicit `Multiplier` geometry. It is not a claim about which geometry the outer `multiply_uniform` selector chooses at a particular input length. The literal `operand` method, with the one-axis identity CRT adapter, produces `2^3431` at P=3438 from operand 1. The unchanged predecessor diagnostic rejects the necessary signed B=3433 before mutating its input. This is a finite-reference integration limitation, not a refutation of Nick Petalas's all-width mathematical theorem.

The original once-rounded Full-gate semantics must also remain distinct from the externally lowered sixteen-H chronology. The source-level discussion and small counterexample establish that distinction; they are not evidence of failure at the sufficient production precision. Coefficient delivery, synthesis, global resident arrays, native private workspace, physical movement and reversible cleanup remain separate.

Credit Nick Petalas for the original all-rational arithmetic width theorem; Armin Pourshafeie for rounded-event and partial-write semantics; Jose Manuel and the rational compiler lineage; Ali Romman for the external tensor caller and recovery integration; and all retained source authors and notices. Apache-2.0.
