# One-contact A2 rewrites with freely chosen native correction frames

On the exact final G20 word from
CrocSwap/integer-mult-bounds#5708, every one-contact A2 rewrite has
strictly greater paid-query cost even when its new correction may use any
of the 645 native frames and every demanded route may use any finite
proper nested path through that same catalogue. This holds for every
exponent 0<t<1: all 184×645 =
118,680 assignments are ruled out by exact sign certificates. **No new κ.**

This closes a specific escape from fixed-correction-frame searches:
changing the scalar word first and then moving the newly inserted
correction. The source common-frame searches and the older fixed-order
contact theorem do not cover that operation. This package keeps all other
scalar events and frames fixed, charges each actual frame demand's route
separately, and gives a favorable paid-cost relaxation;
it is not a complete multiplier theorem or an all-depth lower bound.

## Result and reproducibility

Base: `2485805a6d47f36ea83ddde6327d453ac82d44dc`.
`SOURCES.json` binds exact source word, route table, both matching frame
catalogues and provenance. There are no pending executable dependencies
and no import from the concurrent two-step research package.

From the repository root:

```sh
python3 -I -W error -B research/g20-one-contact-free-frame/verify.py
```

Expected final line: `PASS_G20_ONE_CONTACT_FREE_FRAME`. The command
reconstructs the graph, integer metric, complete 184-interval source
domain, all 118,680 assignments and all 245 exact sign shapes, then compares
the full frozen certificate. It verifies all 685 scalar columns and all
public final returns. There is no random search: the stopping rule is
complete coverage of the stated finite domain.

Of the assignments, 118,677 have disjoint-rank partition proofs. Three
have shape `3^t+4^t−2^t−5^t`, proved strictly positive by decreasing
increments of the strictly concave power function. No numerical sign
screen is included in the published certificate. See [PROOF.md](PROOF.md)
for the full claim, cost model and limitations; [VERIFY.json](VERIFY.json)
lists the replay and independent checks actually required.

The independent verifier scans the source domain separately and uses a
chronological symbolic-frame interpreter with set-valued input rows. It
checks every assignment without importing the primary verifier, plus 736
numeric full-word checks. Its metric comes from a separately derived exact
RREF graph and bucket-distance computation. All checkers support isolated
and optimized Python; semantic checks do not rely on `assert`.

## Scope and inherited assumptions

The strict result concerns paid native queries. Every other new ordinary
expense may be free, and productive targets are held fixed. Complete
native admission, denominators, recursive child realization and the
selected framework assumptions remain inherited. The selected conditional
κ=0.003125804 is unchanged. The theorem does not cover multiple correction
frames, moved original contacts, alternative placement, changed owned
resets, new projectors, shared or cancelled queries between different
demands, or additional rewrite steps.

## Open next questions

- Can two noncommuting contacts with separately chosen correction frames
  evade this obstruction? Start with one exact two-contact interval and
  price all coupled demand transitions; this package does not cover that
  larger domain.
- Can a new scalar mechanism or a projector outside this catalogue lower
  the complete supplier invoice? Such a proposal needs a native endpoint
  proof, all recursive/ordinary costs and owned restoration before claiming
  a bound improvement.

Structured dependencies and stopping criteria are in [TASK.json](TASK.json).

## Provenance and attribution

Prepared for **@CubeJerry**, with substantial **OpenAI Codex assistance**:
the lead developed the moved-demand experiment; one research worker
packaged its proof and exact verifier; a separate worker independently
reconstructed the full invoices using symbolic frames. Native geometry,
exact distance and sign infrastructure was developed alongside a separate
fixed-frame two-step investigation; all required code and fixtures are
included here, with no dependency on that unpublished package.

Credit Ali Romman and the retained native geometry lineage for
CrocSwap/integer-mult-bounds#5708 and
CrocSwap/integer-mult-bounds#5616; unpaidmoon for
CrocSwap/integer-mult-bounds#6290; and Nick Petalas for
CrocSwap/integer-mult-bounds#6305. The latter two remain open predecessor
investigations; this package imports no pending executable source. The
older CrocSwap/integer-mult-bounds#5616 flow certificate and caller invoice
are not used. Apache-2.0,
following the repository and retained source license.
