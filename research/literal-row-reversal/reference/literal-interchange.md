# Literal all-width elementary interchange

PR5162's standalone component still executes counters, routing and scratch
selection through Python methods. This package replaces the complete callee
with one4589-instruction local-symbol program, independent of encoded input
width and spectator sizes. No source method, numeric loop bound or allocator
callback survives at runtime.

For H>=0,A/G/S>=1 and V=A*4^H*G*S binary payload cells, the written refinement
proves exchange of the two H-bit fields, borrowed preservation, a distinct
owned output and repeatable cleanup on15 private tapes. H=0 is a paid owned
identity. The static opcode admission/CFG checker gives at most two free
jumps between charged cell operations. The complete source-sized u/back call
H2/A1/G1024/S12 also includes literal caller copy-back and terminal disposal.

Run `python3 -B research/literal-elementary-interchange/verify.py`.
PROOF.md states the quantified domain, full conservative price and limitations;
RESULT.json records the finite evidence. PREDECESSOR.json pins the unchanged
PR5162 official export, including its original vendor notices and the retained
PR2809 sources. SOURCES.json pins the original CRT context. Frozen predecessors
and selected result are unchanged.

The model has five local symbols and binary payloads. It does not silently
claim a two-symbol tape implementation, a total retained-backing bound, a
literal whole raw/repair caller, ROM production, native/selected admission,
all-size multiplication or a new kappa. Input descriptors and valid disjoint
ports are supplied. Error rollback is not promised. Finite checks support the
written source refinement; independent human/kernel acceptance is unclaimed.

## Open next questions

- Give a fixed-block two-symbol encoding and actual alignment microprogram.
- Prove a total retained-backing grant across varying call histories, including
  erased arrays; fixed tape count alone does not give that bound.
- Compose the complete raw rotation/ROM and repair programs with this callee,
  retaining all original input/output and lifecycle costs.

Credit Jose Manuel's physical ordinary wrapper; retained PR2809/PR2753
stream/cardinality authors; Cinna Davis's CRT construction; Hiroki KUMAZAKI's
repair lineage; Douglas Colkitt and all archived notices. JoyboyBrian with
substantial OpenAI Codex assistance. Apache-2.0.
