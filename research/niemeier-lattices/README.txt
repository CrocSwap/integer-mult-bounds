Niemeier lattices, operator transforms, and paid spinor circuits
==============================================================

RESEARCH ONLY: no new kappa, complete supplier, or O(1) indexing claim.
Prepared for DominikScholz with OpenAI GPT-6 Astra in T3 Code.

This follows the Leech/Turyn research in PR #598 and the user's suggestion,
credited to David Ryan (@davidryan59), to investigate the other 23 Niemeier
lattices. The goal was a cheaper complete supplier, including the cost of
moving into and out of a transformed space. The exact constructions below
are useful intermediate results; none closes that goal.

What this package adds
----------------------
* A census of all 23 rooted Niemeier systems and exact scalar factors for
  D24+, E8^3 and E8^2. The symmetric Pauli operator basis reduces E8^2's
  center support bill to 12,752; its complex compensation I-K still has
  full rank 30,960.
* Rational bit addresses in dimension 16 for E8^2 and D16+, each with
  30,960 ports and binary decoder rank 815. On D16+ spinors, a group-basis
  transform gives 35 commuting shears (2,240 additions in that basis).
  The direct full transform's frame costs consume the prospective saving.
* A fused clique/matching compensation subword with 34 dirty helpers per
  16-port clique. Earlier cleanup lowers local rank mass from 1,024 to 832
  (18.75%), with exact dirty-state restoration. This is a local circuit
  improvement, not a kappa improvement. Proper-endpoint wrappers, spectator
  banks and full supplier admission remain open. Its alternate decoder
  also loses the needed center-rank surplus.
* An explicit native E8 tensor lift with 25,088 ports, exact embeddings
  and a paid invoice using pinned PR #600 profiles. Its best tested odd
  stage count gives nominal kappa about 0.000872182222, below the comparison.
* Scoped obstructions for full Mobius routing, independent rectangle
  factories, rank-minimal residual decoding and a hybrid fitting kernel.
  These do not rule out redundant factors, shared circuits, other endpoint
  schedules, or the 21 glue-dependent Niemeier constructions still open.

Core geometric receipts
------------------------
Candidate                  ports   binary h  real rank  centers  support bill
D24+ norm-four shell        85032      23        2600       2624       55224
E8^3 norm-four shell        89640      25        2088       2088       35400
E8^2 norm-four section      30960      17         816        816       12752

For E8^2, 256 centers have width 17 and 560 have width 15 on both sides.
The narrow centers share 70 frames whose restricted form has rank 13 and
radical dimension 2. The inherited general Clifford-frame lemma permits
such frames; it does not supply the complete circuit or helper schedule.
The hypothetical h=25, C=65000 comparison for all 23 systems is a cost
screen only, not a factorization or an exclusion of the other lattices.

Reproduce from a checkout
-------------------------
Requirements: Python >= 3.11, NumPy and SymPy. Z3 is needed only for the
optional clique discovery script, not for the frozen certificate replay.
The exact interval engine and native Hamming prototype are inherited from
other research directories in this repository and checked by source hash.
From the repository root:

    python3 -B research/niemeier-lattices/verify.py --workbench
    python3 -B -I -O research/niemeier-lattices/verify.py --workbench

Omit --workbench for only the census, geometric factors and initial exact
cost screens. Optional --output /tmp/niemeier-replay writes their combined
receipt outside the package. The workbench drivers use isolated temporary
outputs and compare their regenerated receipts to the committed inputs.
They regenerate coordinate NPZ inputs; the saved cross-factor NPZ is
compared by arrays, not ZIP bytes. Only the MOD4-RANK.json elapsed-seconds
field is excluded from semantic comparisons. Checks use exceptions and
remain active under optimized Python.

MANIFEST.json hashes the complete package except itself and Python caches.
This binds immutable published inputs; receipt replay checks mathematical
contents. The workbench READMEs identify optional discovery/history files
that are retained for context but are not independent certified results.
Finite certificates do not verify the full multiplication theorem or
freshly replay the cited upstream suppliers and their reported endpoints.

Reading order and claim boundaries
----------------------------------
CURRENT.txt records the initial construction attempts; CONTINUATION.txt
records the tensor, fused-word and alternative-kernel follow-up. Both are
research reports with explicitly pinned historical comparisons.
PROOF.txt, CATALOG.txt and catalog.json cover core lattice algebra.
COSTS.txt contains conditional zero-helper screens and moment budgets.
INTERFACES.txt distinguishes complex and bit address fields; its expensive
h=816 bit dual is superseded by the rational h=16 construction in CURRENT.
workbench/continuation/spinor-routes/PROOF.txt states the residual support
obstruction and its implementation assumptions.
SOURCES.txt, NOTICE and the subtree source metadata preserve references,
source pins, contributor lineage and substantial AI disclosure.

The outstanding route is a joint routing/restoration circuit whose paid
frame histories retain a positive center surplus. Neither a low scalar
rank nor a cheap transformed computation alone establishes that saving.
