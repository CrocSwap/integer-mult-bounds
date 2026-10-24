# Two outside directions remove the P112 swap deficit

Under the exact separator hypotheses of DreamingOfClouds' PR3154 RDEP2,
the row swap deficit is zero for the entire s=2 class; the column deficit
is zero for t=2. The written proof covers any coefficient field and any
number of projective classes. A connected-component partition handles
cases that the predecessor's whole-class coloring screen does not.

This is the two-sided K1 ledger. The completed one-sided K2 ledger is not
reopened. All other DR-prime debits and original decoder hypotheses remain;
no global C(P112)>=64, supplier, kappa or Lean-kernel claim is made.

See PROOF.md for the exact source implication and limits. The predecessor
separator identity is explicitly imported; the binary-label independence
premise follows directly from all actual root/label pairings checked here.

Run from the repository root, Python3.10+ standard library:

```sh
python3 -B research/p112-two-outside-direction-swap-deficit/verify.py
python3 -O -B research/p112-two-outside-direction-swap-deficit/verify.py
```

An independent exhaustive functional/list-color solver is also available:

```sh
python3 -B research/p112-two-outside-direction-swap-deficit/independent.py
```

All commands are read-only and require the complete typed RESULT.json. Use
`--write /tmp/two-outside-result.json` only for explicit regeneration.
SOURCES.json pins actual geometry and vendored RDEP2 text to exact Git
objects. The finite graph census and root fixture are proof controls,
not a substitute for the all-field argument and not a decoder construction.
No historical suite, solver, Lean, or selected-supplier replay is needed.

## Open next questions

The s>=3 kernel geometry and remaining F/O/XM/SH deductions are open here.
A first step is a source-admissible higher-dimensional separator instance;
a relaxed graph with arbitrary labels is not enough. All physical caller,
stock, precision and cleanup work remains outside this algebraic lemma.

## Attribution

DreamingOfClouds supplied PR3154 and PR717. Mihir Srivastava supplied the
retained exact p112-single-lift geometry snapshot/checks. New proof and
controls by JoyboyBrian with substantial OpenAI Codex (Astra) assistance.
Apache-2.0; original vendored NOTICE and LICENSE retained. Source-level
AI-assisted review is not independent human or proof-assistant acceptance.

SOURCES.json external_origins records original PR3154 paths, head and byte identities. The byte-identical vendored live inputs are pinned to the first package commit, so publication does not depend on ancestry of the unmerged PR3154. Original and retained SHA256/Git blob identities agree; external source authenticity was checked locally, not inferred by the cold replay.
