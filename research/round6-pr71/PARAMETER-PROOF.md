# Positive-backoff refinement of PR71

The immutable baseline is Chafik Boukhalfa's PR71 commit
`1bef94fd40a746452548c84a4a8f8834670a3113`. Its physical words, complete
fixed profiles, split vector `[1,1,2]`, anchored point order, region schedules
and next-use-aware reclamation remain unchanged.

At the same bit saving 12854322426487/250000000000000000, change only the
positive balanced-assembly backoff from 10^-12 to 10^-18. The new exact
conditional witness is

    kappa = 25707323052097/500000000000000000

It exceeds pinned PR71 by exactly 31/200000000000000000. The unchanged paid
width is 135075665, with auxiliary roles 27455/36015. This is solely a
parameter refinement, not a new graph, physical saving or compiler mechanism.

The checker validates PR71's complete source and finite-input closure,
including predecessor archives, original generator/configuration hashes,
word digests and complete paid-profile reconstruction. It independently
reproduces PR71's κ and its adjacent accepted/rejected bit-grid enclosures,
using both of PR71's independent rational enclosure implementations.
The changed assembly passes all 47 strict constraints and seven margins,
rejects the next κ grid point, and recomputes the eventual arithmetic cutoff
as 14000000000000000000. The original cutoff was 14000000000000.

The new κ remains strictly below the same-bit scoped limit a/(1+a).
No global or fixed-profile optimality claim follows. PR71's physical replay
is inherited; it was not rerun for this parameter-only refinement. Broad
repository/CI checks also remain separate. All original all-size compiler,
analytic, routing, prime-selection, recovery and fixed-tape dependencies
remain conditional. The arithmetic cutoff is not a complete operational
threshold or practical running-time estimate.

Reproduce with an exact archive of the pinned baseline:

```sh
mkdir -p research/round6-pr71/baseline
git archive 1bef94fd40a746452548c84a4a8f8834670a3113 | tar -x -C research/round6-pr71/baseline
python3 research/round6-pr71/refine_parameters.py
```

`parameter-source-lock.json` binds the baseline source closure, baseline
arithmetic certificate and refinement script. `parameter-certificate.json`
contains the exact inequalities, enclosures, complete paid profile and
comparison. No physical word or earlier selected package is modified.

Credit Chafik Boukhalfa for PR71's aligned split graph and next-use score;
Rohan Arun for PR65/67 schedules and exact arithmetic; Alejandro Zarzuelo
Urdiales for the PR61 parameter-refinement precedent; and all inherited
graph, compiler and theorem authors named by PR71. This refinement is by
Dominik Scholz with substantial OpenAI GPT-6 Astra assistance. Apache-2.0;
all inherited notices remain applicable.
