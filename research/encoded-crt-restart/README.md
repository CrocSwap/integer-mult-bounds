# Restart both encoded balanced CRT endpoints on the same 79 historical roles

This package answers the persistent-restart question left open by
[CrocSwap/integer-mult-bounds#7352](https://github.com/CrocSwap/integer-mult-bounds/pull/7352).
The exact published forward and inverse address-state evaluators now reuse
one fixed inventory of **79 private roles across any finite successful call
sequence**, including changes of direction, shape, moduli and precision.
The predecessor's fresh forward/inverse pair retained 158 histories. Both
full invocation bills remain charged. **No new kappa.**

## Exact result and why it matters

The numerical owner already reuses 63 roles within a traversal. The new
`restart.py` supplies the missing whole-call boundary: it retains that owner
and rearms the existing eight guard, seven topology and one staging ports
through a fixed constructor facade. All ten imported scientific files stay
byte-for-byte unchanged, including encoded topology, both numerical
producers and the retire-before-commit source writer. Runtime receives no
decoded node list, precision, width, axis count or coordinate.

The [proof](PROOF.md) shows that complete successful retirement leaves
every old tail blank, so a smaller next call can safely use its own current
extent. It need not scan an arbitrarily large old blank capacity. Historical
backing, physical identities, meters, caller source bytes and all head
returns are preserved. Growing again reuses blank old cells or extends the
same backing; it never replaces a role.

Let `A_i` be the sum of declared widths in call i, `d_i` its axis count,
and `K0` the total initially supplied private local history. The complete
source-operation time is

`T_initial + sum_i O(A_i^4)`.

Write `Amax=max_i A_i` and `dmax=max_i d_i`. The exact rolewise envelope gives

`private backing <= K0 + 3 Amax dmax + 74 Amax + 23 dmax + 223`.

Since `dmax <= Amax/2`, this is `K0+O(Amax^2)`, independent of call count.
Source histories and opaque left prefixes are also retained and charged.
The proof uses the **sum of each role's historical maximum**, not a maximum
of fresh total footprints. A source-level backing bound remains distinct
from a literal binary-TM visited-space certificate.

Fresh initial acquisition/retirement and wrapper validation cost **1264**
raw Port actions. Admission of an already owned blank inventory costs **316**
local validation actions, with its earlier acquisition paid by its caller.
Every successful restart adds exactly **80** rearm actions and **316** finish
actions. All inherited source scans, numerical work, current-width setup,
copying, staging, commits, cleanup and control refinement remain in the bill.

## Reproduce

Python 3.12 and the standard library, from the repository root:

```sh
python3 -I -W error -B research/encoded-crt-restart/verify.py
python3 -I -O -W error -B research/encoded-crt-restart/verify.py
```

Expected:

```text
PASS_ENCODED_CRT_PERSISTENT_RESTART calls=174 nodes=270 roles=79 controls=14
```

The fixed receipt [RESULT.json](RESULT.json) records all 174 calls and 270
actual numerical nodes. Every traversal is driven by the real encoded
`run()` method; a defining-congruence oracle observes each current source
and output without supplying a runtime value or schedule. Port, Word and
Arena constructors are sealed after initial acquisition.

Coverage includes all 32 padded pairs for moduli (3,5), eight adversarial
four-axis tuples, both composition orders, and a changing-shape sequence
with 2→8→4→2→4→8→2 axes. The latter starts from substantial clean history,
grows/shrinks/regrows precision, and runs behind opaque translated prefixes.
Its final charged private backing is **5695**, below the rolewise envelope
**5800**, while keeping the same 79 histories. Fourteen controls detect
unfinished traversal/commit, aliasing, wrong direction, omitted rearm,
hidden acquisition and other specific failures. A dirty hidden-tail
countercontrol exposes the limit of local entry validation.

Finite evidence corroborates the all-input induction. It is not a
formal-kernel proof or independent human acceptance. Executed replay and
independent review status are recorded in [VALIDATION.json](VALIDATION.json)
and [REVIEW.md](REVIEW.md), respectively.

## Source, novelty and limitations

Canonical base: `e54523517d0f03e58352e647c403a5af3e525a57`.
The exact inputs are package-local exports, authenticated by Git blob and
SHA-256 in [EXPORT-PINS.json](EXPORT-PINS.json); no pending commit needs to
be fetched to replay the package. [OVERLAP.md](OVERLAP.md) separates this
result from existing numerical ownership and within-traversal work.

[#7351](https://github.com/CrocSwap/integer-mult-bounds/pull/7351) and #7352
already provide the two complete encoded address-state maps.
[#7154](https://github.com/CrocSwap/integer-mult-bounds/pull/7154) already
derives geometry from the source;
[#5505](https://github.com/CrocSwap/integer-mult-bounds/pull/5505) already
provides the persistent numerical bank;
[#7152](https://github.com/CrocSwap/integer-mult-bounds/pull/7152) already
reuses a different 127-role numerical/ROM pipeline at compiled geometry.
This package does not claim any of those constructions as new. Its delta
is the actual 79-role encoded endpoint restart and its complete repeated-call
time/history contract.

Initial **whole-tail blankness** is an explicit admission premise for a
supplied inventory. The local checks do not certify arbitrary retired
memory or clean hostile hidden dirt. Subsequent successful calls establish
the premise inductively. Clients follow a linear-use lifecycle; old leases
or endpoint handles acquire no renewed authority after retirement. Failed
calls do not supply a rollback or restart guarantee.

Source acquisition/re-encoding, payload routing, exceptional-key adaptation,
literal binary lowering and the full outer caller remain separate work.
The five selected assumptions remain conditional and the complete selected
bound stays at **kappa=0.00363005817**. This is scoped progress on the
owned-erasure and precision interfaces, not a full foundational discharge.

## Open next questions

1. **Bind one actual exceptional-key caller.** Pin its admitted format and
   sequence of required calls, then charge source production, changing
   representation and returned keys. Reusable private history alone does
   not supply the raw compact macro or payload interface.
2. **Lower the whole source closure to one binary program and tariff.**
   Begin with the two fixed facade procedures, then include the inherited
   arithmetic, topology, input acquisition and all control constants. The
   present fixed source model does not certify that binary refinement.
3. **Admit initially dirty histories if a real caller requires them.**
   A usable encoded historical frontier and paid cleaning protocol must be
   specified first. Local blank observations cannot prove an unbounded
   unseen suffix clean; this package deliberately does not assume otherwise.

## Credit

Prepared for **Jerry Chen / @CubeJerry**, with substantial **OpenAI
assistance** in reasoning, code and checks. Retain CubeJerry's encoded
forward/inverse and source-driven topology lineage; JoyboyBrian's numerical,
entry and persistent-owner contracts; Ali Romman's encoded padded source
and retired-write boundary; Cinna Davis's balanced CRT construction;
Hiroki KUMAZAKI's current-coordinate and padded-map work; ToikY's compiled
whole-tree work; commdata2338's history accounting; and every notice in the
unchanged exports. New material is Apache-2.0. No independent human or
formal-kernel acceptance is asserted.
