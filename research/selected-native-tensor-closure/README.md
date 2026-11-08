# Exact native traces and the selected all-column caller

This package proves and independently checks the **algebraic** assertion
`native_all_columns` for the pinned selected #6030 P104 native layer and its
assembled caller, at every positive column width and with arbitrary spectator
factors. It joins every signed native recipe,
the complete local word, all 18 forward calls and 16 wrappers, and every
whole-job helper/main/idle adapter. It does **not** implement the selected-rate
physical dispatcher or discharge the complete five-assumption framework.
The all-column operator assertion is proved; physical realization and the
source's ideal owned-reset semantics remain distinct obligations.
**No new κ.**

The accepted source remains canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, with conditional
κ = `781451/250000000`. No prior source, selected record, tariff or bill is
modified. [PROOF.md](PROOF.md) states the exact quantified theorem, proves the
trace algorithm and tensor interpretation, and gives the complete composition.

## Result and evidence

The new native acceptance mechanism computes the exact closed overlap
`tr(V*U)` as a constrained quadratic Gauss sum over binary variables. Checked
unitarity makes the value `2^9` equivalent to full operator equality. The
checker retains constant phases and Gaussian normalizations; it uses neither
a Pauli tableau, a distinguished input column, floating point, nor a dense
512-by-512 operator matrix. Quadratic elimination is polynomial in the finite
circuit description. This is a certificate-verification bound, not a
multiplication-runtime improvement.

The caller verification keeps two different types of objects distinct:
native products are lifted columnwise, while rational coefficients of
register ADD/COPY/SCALE and signed swaps stay outside the tensor power. A
native constant phase becomes `i^(p*f)`; a register coefficient remains the
same coefficient. The proof does not infer an all-width identity by tensoring
a width-one sum of different native group elements.

| Verified object | Complete coverage |
|---|---:|
| Distinct signed native/helper pairs | 2,922 |
| Distinct MOVE pairs within that union | 2,886 |
| Intrinsic main adapters | 208 |
| Complete local main paths | 312 |
| Distinct complete helper boundary types | 69 |
| Arbitrary helpers per local call | 562 |
| Local endpoint coefficients | 799 × 799 |
| Literal local events | 22,803 |
| Actual raw contacts | 7,488 |
| Composed contact/native/contact paths | 5,616 |
| Complete free-Laurent caller entries | 32 × 32 |
| Arbitrary main productive fields | 3,328 |
| Arbitrary helper productive fields | 10,116 |
| Whole-idle paid fields | 3,120 |

The source-bound reverse-functional Laurent replay checks all 218 physical
controller events and both literal rational boundary programs. It uses the
free Laurent ring, with no `Q^4=1` quotient. The geometry check composes the
actual entry/native/exit maps, matches the selected raw-contact payload hash,
and explicitly fixes the 120 omitted spectator rows of the 265-row source.
Each main/idle positive basis is completed on all 145 retained rows. The
all-width proof then applies to every complete occurrence embedding, including
the embeddings supplied by #6878.

The exact selected bill is unchanged: **13,444 productive fields, 66,834 paid
calls, paid rank mass 240,152 and productive rank mass 240,912**. The checker
reconstructs both complete profiles from the literal source events rather
than inferring a bound from this positive rank margin. Ordinary adapters,
source access, staging, physical erasure and restoration still require their
own implementation and charging theorems.

## What is new, and what is already proved

This is not a new local common-chart lemma or another dense native census.
The contribution is a different exact native acceptance mechanism together
with the **complete selected-source join** from those native equalities to
the assembled all-forward caller, including the exterior-scalar typing and
whole-job boundaries.

| Predecessor or concurrent work | Already established; relationship here |
|---|---|
| #5442, `research/allwidth-caller-certificate/` | Group-algebra and tensor framework for the older #5413 caller. The product-lifting principle is credited. |
| #5974, `research/p104-allwidth-native-certificate/` | Full exact native verification for #5599 and the factorwise lift. Its native census is not repeated as a claimed new theorem. |
| #6043, `research/p104-6030-independent-audit/` | Independent dense verification of the current #6030 native inventory. The present trace method shares neither its dense mechanism nor its candidate compiler's tableau/anchor acceptance. |
| #6635 | Complete selected scalar common-chart census. The present typed induction uses that established mechanism and checks its composition with every MOVE. |
| #6293 and #6331 | The `i^(p*f)` phase convention and the obstruction to deleting native phases. The current width-two controls explicitly enforce those distinctions. |
| #6546, `research/selected-absolute-stochastic-caller/` | Concurrent direct stochastic local execution and a fixed-local all-width lift; its stated limitation is identification with complete recursive callers. The present package closes the algebraic assembled-caller join, without importing its unmerged code. |
| #6878, `research/selected-compiler-occurrence-layout/` | Complete occurrence-specific coordinate embeddings and retained-row geometry. This package supplies their native algebraic endpoint premise; it does not reprice or redevelop the embeddings. |

At the frozen reconnaissance, #6546 was an open contribution at
`ff038070b8d122a43993f2b2524154323cc6b4d7`, and #6878 was an open contribution
at `41febf890fbbb852c6059d4c0cc8c593ae9dfa5c`. They are credited comparisons and
applications, **not runtime or source-import dependencies** of this package.
The proved tensor/naturality statement quantifies over any complete embedding;
the exact accepted inputs below all come from the pinned canonical main.

The native/caller identities and raw phase construction in
`research/p104-productive-controller/` and the independent caller audit remain
credited source results. Existing physical compact, Gaussian-monomial and old
controller work #3055, #3087 and #3385 was checked during scope selection and
was not reimplemented. Its older tariffs do not automatically price the
current selected dispatcher.

## Reproduction

From the repository root, using only Python's standard library:

```sh
python3 -I -B research/selected-native-tensor-closure/verify.py
```

Expected final marker:

```text
PASS_SELECTED_NATIVE_TENSOR_CLOSURE {"kappa_changed": false, "native_pairs": 2922, "paid_calls": 66834, "productive_fields": 13444, "raw_contacts": 7488, "rejecting_controls": 20}
```

The registered replay also checks the generic trace engine in normal and
optimized Python and rebuilds the full native recipe artifact with the
credited source compiler:

```sh
python3 -B scripts/research_package.py --package research/selected-native-tensor-closure
```

`SOURCES.json` records exact Git blob and SHA256 pins. Every live source input
is declared in `VERIFY.json`. The independent verifier authenticates the
selected word, result, controller, port data and mathematical source files
before parsing them; it imports no predecessor verifier or compiler.
`emit_recipes.py` alone imports the credited compiler to regenerate the
candidate artifact. Its complete recipe payload must reproduce the already
registered selected digest
`e22642923d5437c49e2d1dc79dd6b795503499d6f33615a1df3568f0b96164c1`.
The independent checker then accepts every complete emitted product by the
trace method. This producer/acceptor separation is deliberate.

`RESULT.json` is deterministic and records the exact coverage, profile and
endpoint digests and every rejecting control. `--write` regenerates only this
new package's receipt. `emit_recipes.py --write` regenerates only this package's
small compressed candidate artifact; ordinary replay compares its full
decompressed contents instead.

## Verification and negative controls

The trace engine's independent dense-column oracle uses exact rational
arithmetic on 120 deterministic random small circuits. Additional checks
enumerate all 16,933 quadratic forms through four variables with zero constant
term, 480 affine systems, 480 affine substitutions, nonzero constant phases,
unitary inverses and a 300-variable symbolic trace. Fixed seeds are `7606030`
and `7606546`; these are bounded verifier tests, not an open-ended supplier
search. Ten trace grammar/operator controls reject malformed expected gates,
wrong phases and invalid gates, including cases that agree on the zero column.

The source package has 20 separate controls. They reject source-byte and
registered-payload drift; a global `i` invisible to conjugation action; reversed
native factors; an omitted positive child; confusing a canonical rank-one
chart with the translation Gaussian on that vector; `i^p` used where `i^(p*f)` is
required; tensor-powering an exterior minus sign; tensoring a Gaussian sum
termwise; a wrong whole-helper normalizer; a scalar chart mismatch; reversed
MOVE orientation; aliased public roles; a missing wrapper translation or swap
sign; a wrong raw final exponent; a corruption on an arbitrary spectator
coordinate; and an omitted whole-job final translation. Mathematical fault
controls call the comparison mechanisms directly, so their rejection is not
merely an earlier source-hash failure.

Both normal and `-O` execution are required by the registered manifest. The
package uses explicit checks rather than optimization-disabled assertions.
The finite tests support the checker implementation; the all-f and arbitrary
spectator conclusions come from the written theorem, not from sampling
column widths. This is not a proof-kernel formalization or independent human
acceptance.

## Open next questions

The structured versions are in [TASK.json](TASK.json).

1. Bind this exact typed algebraic word to the selected-rate physical
   dispatcher. Start with one full compiled occurrence, preserving the
   distinction between native column phases and exterior scalar field
   coefficients, and account for every adapter, complete field, recursive
   child and return operation. This is blocked by the remaining physical
   implementation and charging obligations, not by a missing local chart
   identity.
2. Compose the resulting implementation with the owned-stream and precision
   contracts. Start with a complete source-owned call/return that realizes
   the 29-label local owned bank and separate thin scratch field, without
   treating the ideal CLEAR in this algebraic proof as a physical erasure
   algorithm. The required ownership and rounding premises remain explicit.

## Attribution and license

Prepared for **@CubeJerry**, with substantial **OpenAI Codex** assistance in
research, derivation, implementation and adversarial checks. The lead research
reviewer checked the Gauss-sum derivation and the complete typed composition;
that is an AI-assisted mathematical review, not a separate formal proof.

Credit DreamingOfClouds for the selected #6030 change; David Arias for the
coalesced source word, Cinna Davis for private reuse, the native representations
and the Laurent controller,
Gareth Davidson for their composition, and Ali Romman for the P104 caller and
independent source audits. The native compiler, source constructions and
proof framework retain their existing contributors' credit. Relevant earlier
and concurrent mechanisms are identified above rather than claimed anew.
Apache-2.0, following the repository license. No predecessor source is copied
or modified; the compressed artifact contains deterministically emitted
recipe data authenticated against the selected registration.
