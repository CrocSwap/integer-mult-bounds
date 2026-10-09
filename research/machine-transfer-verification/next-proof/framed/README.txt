TYPED ADDRESS-GAUGE REFINEMENT OF LITERAL XOR WORDS
8 October 2026

What was proved
---------------
FramedXor.lean is a new Lean 4.21.0 module using Std and the unchanged local
DirtyWrapper.lean dependency. It is a general semantic refinement theorem,
not another finite Boolean replay. Roles, addresses and initial payloads are
universally quantified. Addresses need not be finite for these equalities.

A gauge g[r] maps a logical address to its physical location. Decoding reads
P[r,g[r].forward(a)]. Reframing a role from old to new physically reads its
old row at old.forward(new.inverse(b)), where b is the new physical address.
This is the payload pullback of the position pushforward new * old^{-1}.
Both inverse laws are explicit in the Gauge structure.

The typed Step constructor permits a physical XOR only when the source and
target CURRENT gauges are equal. Trace's type records initial and final
assignments, so an instruction cannot silently use a stale assignment.
decoded_execution proves that the complete physical trace decodes to the
literal XOR word obtained by erasing only reframes. encoded_execution and
physical_execution expose both endpoint gauges; restored_execution and
restored_addresswise cover identity endpoints and DirtyWrapper.run.

Source injection and scatter have distinct source/auxiliary/target banks.
decoded_injection and decoded_scatter are specializations of the common-gauge
invariant. scatter_permutation proves that a literal list of auxiliary-to-
target reads may be permuted, even if targets repeat. This justifies center-
first dispatch at the scalar level while preserving every incidence. It does
not allow general reordering of mixer XORs.

copied_fanout_correct uses ONE newly allocated blank Option.none row, ONE
transport to a common target gauge and an arbitrary literal list of reads.
The fresh row is then restricted away. All Option.some original roles begin
arbitrary; there is no clearing or overwrite of an original dirty auxiliary.
copied_fanout_preserves_other proves exact physical preservation of every
original role outside the target list. Allocation, copying, transport, reads
and erasure still require the separate complete-stream and tape-cost proof.

terminal_role_transport is the interface for role split/merge. destination(r)
is the output role of input role r. Assume the scalar word has this role
permutation and
  g_out(destination(r)).forward(a) = sigma.forward(g_in(r).forward(a)).
Then
  physical_out(destination(r), b) = physical_in(r, sigma.inverse(b)).
Thus sigma is a position pushforward; payloads use its inverse pullback.
The equality is valid along destination's image; an outer role-permutation
undo must separately supply its bijectivity. The parent RowInterchange proof
is intended to instantiate the complete finite split/merge boundary.

Two kernel-checked counterexamples show that unequal incident gauges invalidate
pointwise decoded XOR semantics, and that an arbitrary dirty temporary cannot
replace the required fresh blank copy. Neither is a counterexample to the
actual construction; they make the necessary interfaces explicit.

Verification
------------
The module was checked with Lean 4.21.0, commit6741444a63ee. No Mathlib, axiom
declarations, native_decide, unsafe theorem proof, sorry or admitted result is
used. All 18 printed main theorem axiom reports contain only propext and
Quot.sound, except the two explicit counterexamples which require no axioms.
The unchanged DirtyWrapper dependency has the same standard axiom boundary.

Fresh reproduction, with Lean 4.21.0 installed:
  LEAN=/path/to/lean bash check.sh /absolute/path/to/empty-build-directory
The script recompiles both sources; it does not reuse supplied .olean files.
build.log records the actual successful check, and proof-receipt.json binds
the source and log hashes. Existing five Lean deliverables were not edited.

Exact remaining connection to the multiplication candidate
--------------------------------------------------------
This closes the ABSTRACT address-gauge semantic lemma. It does not establish
the full multiplication theorem or instantiate the selected serialized words.
The following concrete refinement obligations remain:

1. Interpret every retained rational subspace label as an actual partial-swap
   Gauge on the complete finite q-adic address set, with valid inverse laws
   after one common eligible runtime prime is selected. Generic Gauge is not
   itself a proof of integrality, prime eligibility or partial-swap factorization.

2. Emit a typed trace for the entire ambient two-stage circuit, not only the
   recorded middle mixer. Early L,J,L^{-1} use D0; only the middle L uses its
   per-role D_U path; cleanup L^{-1},V uses D1. The source and target data paths,
   source copies, side-growth flags, endpoint corrections and complementary
   reverse orientation must be present with their actual tensor embeddings.
   The paper phase assignment and finite middle-incidence checks exist, but
   no generated Lean term currently binds that full concrete trace.

3. Bind each concrete copied-center fanout to the actual literal scatter list,
   show every target still has the common D0 (or reverse D1) gauge at its read,
   allocate only a fresh complete temporary stream, and prove the original
   center has no intervening producer use. The new generic fanout theorem and
   scalar scatter-permutation theorem cover semantics once these are supplied.

4. Bind scalarWord of the concrete trace to the independently replayed wrapper
   (allowing only the proved scatter permutations and explicit fresh copies).
   Supply the all-role scalar permutation and the actual terminal gauge equation
   to terminal_role_transport. DirtyWrapper's algebra alone does not provide
   these concrete address/frame equalities.

5. Refine each literal transport to the ordered contiguous residual blocks
   charged by the selected profile and prove fixed-tape implementation cost,
   whole-row divisibility, retained spectators, descriptor bounds and uniform
   overhead. FramedXor counts no operations and proves no recurrence estimate.

Reference boundary: inherited written phase/copy arguments are in baseline
64ed4cbf872b86b81c22f104967b88d24b8e4548, notes/dag-construction.tex:94-139,
notes/paired-construction.tex:104-113, notes/incidence-construction.tex:94-123,
and notes/copied-centers-lemma.tex:15-76. outputs/transfer-review.txt gives the
broader paper-level review. This module adds a genuine checked semantic lemma;
it does not turn that limited review into complete machine verification.
