# Independent source refinement of exact normalized-product recovery

This package independently checks the numerical implication implemented by
the retained `physical-ring-product` source from #3709 and inherited by the
FFT word service in #3787. For every admitted parameter tuple and every
disk-valued input packet, the source returns the required rounded normalized
negacyclic product, under its explicit integer, scalar-child, codec and
ownership contracts. **No new κ.** The production algorithm and selected
certificate are unchanged.

## Result

Fix integers `A,C >= 1`, `p >= 2`, `1 <= ell < p`, and let
`r = 2^ell`, `N = 2r`, `m = ell+1`. Each of the `C*2^A` records supplies two
degree-below-`r` polynomials with Gaussian `p`-grid coefficients in the closed
unit disk. If `Q_p` means componentwise truncation toward zero to the `p` grid,
the exact pinned `RingProduct.run` numerically returns

\[
Q_p(uv/r)\quad\text{in }\mathbb C[X]/(X^r+1)
\]

in the original record, coefficient and real/imaginary order. The source's
strict `ell < p` guard is retained: `m <= p` is needed for the quoted
`Q <= 8p` precision bound.

The complete argument in [PROOF.md](PROOF.md) combines two kinds of evidence:

1. Fourteen source-derived certificate groups check exact signed arithmetic,
   directed interval helpers, all Taylor phases, the actual twiddle call
   sites, complete DIF/DIT rounding DAGs, plan fields, stream order, source
   loop outlines and final recovery. Their polynomial inputs are symbolic
   arbitrary integers. The finite sign/magnitude cases are exhaustive domain
   partitions, not sampled input values.
2. Written source-bound inductions establish binary shifts and nearest
   rounding, the Machin/Taylor enclosure, reachable interval guards, all FFT
   stages and bit-reversal order, and the numerical recovery inequality.
   The last inequality is
   `(12m+2)*2^(2p+2m-Q) <= 1/8`, with strict actual error. It justifies the
   exact ordinary integer recovery before upper-half subtraction and the
   single final `p+ell` truncation.

The certificate reconstructs the actual rounding expressions. It does not
assume that a method named `multiply`, `truncate` or `inward` has the desired
endpoint. A source summary is installed only after its local contract has
been established. The unsigned scalar child and bit primitives remain
explicit premises, as stated below.

## What is new

The numerical estimates and underlying FFT/Machin/Taylor construction belong
to #3709; this package does not present them as new lemmas. The additional
result is an independently implemented source refinement connecting those
estimates to the actual integer operations, truncation sites, arbitrary-input
local dataflow, complete source loop order and returned product.

The bounded successor survey inspected `physical-fft-word`,
`fft-word-parameter-bounds`, `fft-carry-recovery`, `fft-time-constants` and
`fft-space-ratio`, alongside the originating and relevant later PR records.
The located geometry, carry and cost results do not supply this source-level
numerical check. This is a bounded novelty check, not a claim that the full
research archive was exhaustively searched.

This result matters to the numerical premise of the FFT word service. It
does not establish the whole selected multiplication theorem, replace the
word service's ownership/cost arguments, or transfer a stronger supplier
tariff to an older physical implementation.

## Scope and primitive premises

The theorem assumes the canonical exact nonnegative `Count` operations,
encoded iteration and canonical word codecs; an exact unsigned `WordProduct`
return at the declared operand width; and the retained successful-entry,
live-operand and owner/packet interfaces. The actual signed scalar wrapper,
its complete `2n`-bit read and the source's declared `Q+3` operand width are
checked. The source algorithm's Karatsuba recursion, allocator, exceptional
cleanup and all-size running-time bill are not reproved here.

The checker never imports or executes the retained production modules. It
parses their exact authenticated bytes into a restricted, source-specific
finite interpreter and source outlines. Unbounded loop correctness and the
analytic inequalities remain the written inductions identified in PROOF.md
and in the receipt. In particular, the arctangent/Machin loop and source
dyadic-admission block are written source traces, not automatically certified
Python programs. This is not a general sound Python verifier or a formal
proof-kernel result.

## Reproduce

From a checkout containing the package and its declared source inputs:

```sh
python3 -B scripts/research_package.py --package research/normalized-product-source-refinement
```

Both registered Python 3.12 commands must print:

```text
PASS_NORMALIZED_PRODUCT_SOURCE_REFINEMENT {"certificates": 14, "kappa_changed": false, "rejecting_controls": 63}
```

The second command runs with `-O`; validation does not depend on `assert`.
The commands use only the standard library and read the seven small pinned
inputs declared in [VERIFY.json](VERIFY.json). They need no predecessor
runtime archives, external solver or physical multiplication replay.

[RESULT.json](RESULT.json) contains the complete deterministic certificate
and each rejecting control's reason. `verify.py --write` deliberately
regenerates that receipt; ordinary replay compares the entire parsed result.
The registered normal and optimized replays and committed-byte preflight
were executed for this package. They do not replace the written proof.

## Adversarial checks and independent review

The 63 semantic controls change source text or ASTs in memory before the
numerical audit, bypassing the trivial source-hash rejection. They cover
premature truncation, wrong signs and widths, altered precision and stage
counts, reversed halves, a missing opposite transform, wrong normalization,
invalid final-index admission, lost output and incorrect twiddle production.

Separate reviewing work first derived the numerical target directly from
the original source, then found concrete weaknesses in an earlier draft of
this checker. Unresolved symbolic comparisons, zero tests and implicit
dictionary-key equality could be mistaken for concrete control; disconnected
inner loops and unchecked normal-completion clauses could conceal a broken
whole program. Those checker defects were repaired. The supplied probes are
preserved among the registered controls: symbolic predicates must have a
declared proof or reject, source loop bodies are attached to their actual
parents, and the complete successful exit retains the returned output.

These were defects in the draft verifier, not counterexamples to the
canonical #3709 numerical routine. The independent numerical derivations
found no defect in that routine under the stated primitive contracts. This
was separate AI-assisted reasoning and adversarial checking, not independent
human approval or an exhaustive theorem-prover audit.

## Provenance

The canonical base is
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
[SOURCES.json](SOURCES.json) pins every live input by Git blob and SHA256,
along with the frozen task and selected-record provenance. Only this package
is added; the source files and selected record are unchanged.

Credit Jose Manuel / `jmbarrancoml` for #3709 and #3787, their source
implementations, original numerical proofs and retained notices. The classic
Karatsuba, radix-two FFT and directed interval methods retain their original
credit. Prepared for `@CubeJerry` with substantial OpenAI Codex assistance in
derivation, implementation and adversarial review. Apache-2.0.

## Open next questions

* Compose this numerical refinement with a separate ownership and all-size
  cost review of the actual FFT word caller. Begin with its exact radix/carry
  interface and returned packet, keeping every precision and motion cost.
  The blocker is the remaining physical lifecycle/caller proof, not another
  numerical product census.
* Formalize the small polynomial/opaque-rounding algebra and the written
  interval/FFT inductions in a proof kernel. Begin with the six magnitude
  partitions and exact recovery scale. The current interpreter and mutation
  controls do not supply that kernel or prove arbitrary Python correct.

The structured questions, relevance and first steps are in
[TASK.json](TASK.json).
