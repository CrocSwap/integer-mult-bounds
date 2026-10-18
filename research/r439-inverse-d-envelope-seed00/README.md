# A signed inverse-D envelope for the frozen PR967 bit word

The unchanged PR967 word admits a tighter finite reverse-prefix estimate: **10,394,084 -> 4,525,748**. The improvement comes from retaining integer cancellation inside its 5,563-ADD frame-zero D block. The rest of the reverse word keeps the original conservative propagation. No circuit, paid profile, production allowance or selected bound is changed.

| Quantity | Retained positive envelope | Hybrid estimate |
|---|---:|---:|
| Forward peak F | 72,847 | 72,847 |
| Reverse peak B | 10,394,084 | 4,525,748 |
| Local expression strict bit count | 102 | 99 |
| Nine-stage expression strict bit count | 192 | 188 |

The reverse C/B/scatter/A prefix peaks at **49,347**, so D determines both reported reverse bounds. The maximum new weighted norm occurs after **5,335** inverse-D elementary ADDs, in physical register **158**, immediately after subtracting register **179**. Its row has 346 nonzero coefficients. The full word still has **11,783 ADDs**, including **5,563 D ADDs**; the inherited paid rank mass remains 5,129. This is a precision certificate for the existing signed stream, not another target/helper basis retune.

## Reproduce

From the repository root, with Python 3.10+ and its standard library:

```sh
python3 -I -B research/r439-inverse-d-envelope-seed00/verify.py
python3 -I -O -B research/r439-inverse-d-envelope-seed00/verify.py
```

On Windows use python in place of python3. Expected final line:

```text
PASS_R439_INVERSE_D_ENVELOPE B=10394084->4525748 prefixes=5563 columns=661 controls=10 no_new_kappa
```

The default run reconstructs the entire [CERTIFICATE.json](CERTIFICATE.json) and compares every decoded field, including all 661 entry weights, all 5,563 prefix destination bounds and the full extremizing row. Add --write-certificate only to deliberately regenerate it. [SOURCES.json](SOURCES.json) has an exact mandatory inventory of six consumed files at frozen base 2921874911956718fcaaaf9396fe8267b3cfa9f0. Missing entries, changed bytes, duplicate JSON keys, nonfinite values and Boolean-for-integer substitutions are rejected.

## Bound and tightness proof

Reverse the retained stream through C, B, scatter and A using its original positive recurrence. This supplies a nonnegative entry vector b with |x_i| <= b_i and an earlier peak P=49,347. The bounds may be correlated and loose. Replacing the reachable set by the independent box X={x: |x_i|<=b_i} only enlarges it, so any bound on X applies to every earlier-compatible state.

The actual inverse ADD is x_d <- x_d - x_s. Each D gate is at frame zero in the forward word; in the reversed frame convention all affected registers use its common complementary frame. There are no MOVE, COPY, ERASE, recursive frame changes or coefficient scales inside D. Thus a D prefix acts by an exact integer matrix Q_k in this fixed coordinate chart. A changed row evolves by q_d <- q_d-q_s, starting at the identity.

For any prefix k and register d,

```text
|(Q_k x)_d| <= sum_i |(Q_k)_(d,i)| b_i = L_(k,d).
```

This is the triangle inequality for scalar values, and also bounds vector-valued registers with the same chart by their norm bounds. At a single ADD only its destination row changes. Consequently it is enough to inspect every changed destination row and the initial maximum max_i b_i: every other row keeps its previous bound. This covers every register at every one of the 5,563 prefixes, rather than only the final D matrix. Including the earlier prefix gives B_hybrid=max(P,max_k,d L_(k,d))=4,525,748.

For the maximizing row q, set x_i=b_i sign(q_i), with zero for zero coefficients. This point belongs to X and satisfies qx=sum_i |q_i|b_i. The verifier replays this corner literally to the maximizing prefix. Hence 4,525,748 is **exact for this independent entry-box model**. The construction does **not** assert that this corner is reachable from unit-bounded physical inputs through C/B/scatter/A; it does not prove a tight full-word operator norm.

The proof uses cancellation between repeated occurrences of the same entry variable, not an uncharged new primitive or a choice of new gate signs. The source already emits negative coefficients for reverse ADDs. Applying this smaller number to an unsigned inverse is invalid and is rejected by a control.

## Source-bound lowering and arithmetic

The verifier reads the unchanged global_k.py and the actual punctured adapter adapt9p.py. It replays all nine non-path edits to that global script in memory; only the first import-path formatting edit is irrelevant and skipped. It then checks the exact syntax of:

```text
events.append([1,x,y,-c if reverse else c,f,int(reverse)])
norm[x] += abs(c)*norm[y]
prefix = (1<<nb)*cf**(K+1)*cb**K
nb == 6*(K-1)
```

The existing positive norm recurrence takes a maximum over every ADD prefix; it is not merely a final-state bound. MOVE records change the frame metadata without changing that scalar envelope, and COPY/ERASE update the copied value and norm. Our earlier C/B/scatter/A portion uses precisely that retained conservative scalar model. The signed calculation is restricted to the one common-frame D segment; no cancellation across a frame move or unspecified child map is assumed.

With the same F=72,847, substituting the hybrid B into the inherited finite expressions gives:

```text
64 F^3 B^2 = 506752294891315934525524876288
2^98 <= this local expression < 2^99

2^18 F^5 B^4 = 225610730107861331980569608403480309156822593397355184128
2^187 <= this nine-stage expression < 2^188
```

The old expressions are respectively 2672929057893220568931365420032 and 6276870480677531528435239117197771736166837152483102425088, requiring 102 and 192 bits under the same strict comparison. These are exact integers. **The production allowance stays 192 bits.** In particular, this audit does not silently change the existing 64-bit allocation granularity or reprice a recursive provider.

## Independent coverage and controls

[envelope.py](envelope.py) propagates sparse integer coefficient rows. [independent.py](independent.py) imports no primary implementation and uses three different checks:

1. It reconstructs the entry weights by traversing the literal grouped records in reverse order.
2. For each of 661 separate unit inputs, it executes scalar integer subtractions at all 5,563 inverse-D prefixes and accumulates their weighted absolute values. It compares every destination bound, then executes D forwards and checks the original unit input is restored.
3. It pulls the maximizing output functional backward through the prefix to recover its coefficient row, and separately executes the signed box corner to prove equality.

The unchanged owning checker reconstructs 120 root lines, 111 labels and 636 frames. The modulo-two D endpoint also matches the original PR589 word. Ten rejection controls cover unsigned use of the signed bound, a one-smaller peak, a wrong extremizing sign, an omitted peak gate, an interior-prefix mutation, ignoring entry weights, missing lowering source, duplicate/nonfinite JSON and receipt typing. Optimized Python mode passes; validity does not rely on disabled assertions in the new code.

## Scope, overlap and remaining obligations

The assigned seed **00** was recorded before this round and is not rerolled. [CLAIM.md](CLAIM.md) records the three candidates. This is a complete fixed-word prefix calculation, with no search budget, sign optimization, gate retuning, restart or omitted D prefix.

The accepted pointer at the frozen base remains PR942's conditional kappa 0.001661960547713947 with PR589's bit supplier. PR967 is an incorporated research candidate, not the selected supplier. The mutable selected-result.json is context rather than a runtime dependency.

Signed-prefix PR395/396/398 concern earlier complex target-prefix/gauge circuits; PR821 refines complex per-replica norm counts and credits PR496's maximum-stream norm method. PR975 checks exact complex row-L1 prefixes. They are relevant norm/cancellation precedents, not this frozen bit D certificate. PR1040 and PR1047 change the target/helper bases after PR967; their operations and savings are not imported or composed. This result makes no priority claim for weighted operator norms or cancellation.

As for PR967, original syntactic **H2 is false** and literal **K_equals_D is false**. The separate semantic D endpoint passes; H1/H3/H4/H5 and the other interface conclusions pass. Native hosted emission, precision/provider invoices, whole-repository suites and outer assembly were **not executed**. Adopting the bound requires the retained signed/common-frame semantics and a separately reviewed invoice migration; the finite scalar certificate does not discharge all-size compiler, common-label/mutable-source, hosting, tape, exact-recovery or analytic obligations. No new kappa, paid-profile improvement, native admission or physical tightness is claimed.

Prepared for **@woklerx** with substantial **OpenAI Codex assistance** in research, mathematics, implementation, verification and writing. Apache-2.0. Separate algorithms and agent reviews are not independent human review. See [NOTICE.md](NOTICE.md) and [VALIDATION.json](VALIDATION.json).
