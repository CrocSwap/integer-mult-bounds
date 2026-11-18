# Sharp radial Gaussian rounding with complete phase-covariant ports

A parity-dependent square-ring matching attains the sharp pair radial
supremum **h/sqrt(2)** while preserving global Gaussian phases, exact sum,
wire swap and common translations. Its inverse is its componentwise
conjugate. This supplies the symmetry missing from
[PR #7696](https://github.com/CrocSwap/integer-mult-bounds/pull/7696).

The new provider runs through the unchanged explicit backend interface
and complete two-/three-call C0/C2 ports retained in
[PR #6509](https://github.com/CrocSwap/integer-mult-bounds/pull/6509).
Both arbitrary stored dirty banks return exactly under successful reverse
execution. The source coordinate-error requests remain valid. No new
kappa, selected-assumption discharge or accelerated native tariff is claimed.

Read [PROOF.md](PROOF.md), [RESULT.json](RESULT.json), the
[provider](kernel.py), [retained complete port](ports.py) and
[source pins](ORIGINS.json). All source wrappers and additions remain.

## Radial and implementation contract

For N=8^f, put D=f*h*sqrt(N)/2. A complete native call changes the field
norm by at most D in absolute value. For entry-bank norms X,Y, the full
k-call forward port has output norms at most X+D and Y+3X+(k+2)D.
The reverse port has bounds X+D and Y+3X+(k-1)D. The per-layer bound is
sharp; the complete-call and port bounds are sufficient, with no claim
of optimality. Approximation error remains f*h*sqrt(N/2) per call.

The pair implementation uses fixed comparisons, signs, parities and exact
halves. It uses no variable data division or growing lookup. Stored words
use the retained signed width w; a constant number of w+6 auxiliary words
suffice. Their work and storage are included. The complete indexed bounds
are O(fN*(w+f)) bit work and O(N*(w+f)) stored bits, with every native pair,
source wrapper, addition, range check and owned route/auxiliary cleanup.
These are not exact tape-transition counts or a measured speedup.

The fourth-power identity and tensor-stage commutation fail. The inverse
must reverse the literal stage order. No native graph identity is inferred.
A fixed tape graph, physical routing, owned backing, recursive pricing,
stock and selected caller admission remain open. The selected frontier
and all five assumptions remain unchanged. The old eight-word scratch
allocation is not claimed for this different pair computation.

## Evidence and reproduction

Use CPython 3.12 and its standard library from the repository root:

```sh
python3.12 -I -W error -B research/phase-covariant-radial-ports/verify.py
python3.12 -I -W error -B -O research/phase-covariant-radial-ports/verify.py
python3.12 -B scripts/research_package.py --package research/phase-covariant-radial-ports
python3.12 -B scripts/check_research_commit.py --package research/phase-covariant-radial-ports --check-source-history --check-modes
```

Expected markers are PASS_PHASE_COVARIANT_RADIAL_PORTS,
PASS_REGISTERED_RESEARCH_PACKAGE and PASS_RESEARCH_COMMIT_BYTES.
Both modes check 13122 pair directions, 52488 phase cases, 16900 complete
ring points, all signed input domains at widths 2/3/4, and 68 sharpness
indices through 4097 bits. There are 24 complete native calls, 672 fiber
observables, 24 complete port executions with 60 actual paid cuts,
24 exact dirty returns and 12 aligned predecessor comparisons. The
primary port executions contain 16720 pairs and 133760 stored range checks.

Exact source bytes, direct rational errors and radial inequalities are
checked. The copied ports.py retains its source trailing blank line;
new-source whitespace checks exclude only this byte-exact retained file. Overflow, invalid domains, aliases, wrong inverse order and
excluded finite-order/tensor identities have controls. Full predecessor
package replays, selected cold replay, Lean and Docker were not run.
Independent human and formal-kernel review are unclaimed. These finite
checks corroborate the written all-input proof.

## Source and overlap

Base: canonical main e54523517d0f03e58352e647c403a5af3e525a57, priority
revision 8. The uniform-transfer card changes scope to this source-bound
local provider and inverse contract. [TASK.json](TASK.json) states the
family decision and remaining costs. The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19707602) follows
the existing exact-sum handoff. Live handoffs, source-reference intake,
refreshed PR/Discussion overlap and the complete closed snapshot with its
updated-order delta show no competing one-pair ring-provider claim.
Sparse local and unpublished work remain coverage limits.

## Open next questions

Can the whole indexed program be lowered to a fixed tape graph at a useful
recursive tariff? First specify a signed format, routing, every temporary
and the exact operation order. Preserve both arbitrary banks and do not
substitute the failed fourth-power identity for the actual inverse.

## Credit

Prepared by Ali Romman with substantial OpenAI Codex assistance.
[CREDITS.md](CREDITS.md) links the exact global-optimum and port sources,
CubeJerry's distinct four-axis phase precedent, and all retained native
attribution. The runtime source files keep their original notices.
New work is Apache-2.0.
