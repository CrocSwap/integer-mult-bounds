# Attribution and license

Prepared for **William Lawyer / WilliamLawyer**, with substantial
**OpenAI Codex assistance** in scope selection, mathematical derivation,
source inspection, implementation, verification and writing. No delegated
workers were used. No independent human review or proof-assistant
formalization is claimed. New text and code are Apache-2.0 under the
repository license, retained at `vendor/LICENSE`.

**Rafael Guevara / alephnan**, PR803 at
`d213ac12d4a1ab8f717d942e844df318ceb395fb`, supplies the inherited analytic
Wiener bound and the correctly stated operator-power hypothesis being
audited. Its proof, notice and source metadata are preserved byte for byte.
That note credits the classical Hardy coefficient inequality, finite
Blaschke reflection, and the Dolzhenko-Spijker arc-length inequality, with
references to Anton Baranov and Rachid Zarouf, and Yuichi Kanjin and Kunio
Sato. This package does not re-prove those analytic ingredients or execute
its verifier.

**Ryan Pinto / Ambassators**, PR692 at
`c5b53a5e80372a1fae9830d8dcf21aaabce3f729`, supplies the preceding explicit
cycle-local finite-geometric resolvent and independent weighted-stride
verification. Its proof, notice and source metadata are also retained
unchanged. The attribution here follows that source's own notice and the
PR author's identity. Our arithmetic implementation is independently
written and does not import PR692 code.

**Ali Romman**, incorporated PR621 at
`520774462b19b29af41554b74def31f9d01e997e`, supplies the prime-power circle
certificate motivating PR803. Our counterexample uses the elementary
polynomial z-a, so it does not depend on that certificate. The source chain
and its original OpenAI exact-DFT provenance remain as recorded in the
predecessor source metadata; they are not replaced by a new provenance claim.

**Chafik Boukhalfa / chafreaky**, PR628
`0768f97d06c623b8211e651543c66135796b62bf`, and **Charles Bethin / cbethin**,
PR764 `983d66f0f2e48ee500ec7eee2da9244c001c5064`, study rounded factor scans.
**Wentao Li**, PR805 `ef34bd5b32fcf2d5640dae90b5b8f28488738d5a`, concerns a
dirty scalar-leaf contract. **Thiago Costa**, PR832
`d42f42714018064078263aa77b4b4b4b2af874f8`, gives a distinct Sobolev transfer
bound under unit-operator assumptions and acknowledges PR803. These are
related work, not runtime dependencies or discharged implementation duties.

During the final refresh, **Rohan Guliani / Rohansguliani**, PR846 at
`4bdb3e755ea7118170a7a34764df955880dec282`, supplied an arbitrary-stride
rounded solver with an explicit strict contraction margin and tape charges.
Its proof and notice were inspected. That algorithmic result has a different
scope from our balanced, possibly locally expanding cycles; we neither
duplicate its algorithm nor claim that these witnesses violate its premises.

Weighted permutations, diagonal similarity, finite geometric inverses and
Neumann perturbation bounds are classical. We make no literature-priority
claim for these mechanisms. The contribution is this explicit audit of a
weaker admission rule, its arbitrarily near-unit exact counterexamples,
sharp cycle-local amplification accounting, and independently implemented
finite evidence and failure controls. It does not allege an error in the
correctly stated PR803 or claim a new kappa.
