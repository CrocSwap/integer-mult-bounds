# Attribution and assistance

New files are under CrocSwap/integer-mult-bounds' Apache-2.0 license.
Prepared with substantial OpenAI Codex assistance, as an independent local
verification contribution. This stage was originally prepared locally; the
contribution is now available on the public review branch. No PR or external
comment was made as part of this stage.

The motivating single-stream objection and exact numerical experiments are
RaD / hipotures' work, directed by humans with Claude assistance. Their model
is pinned to c6d971dabdde94e1c5ec1521c44ca63fd41debf9; see AUDIT.json. No Python
source is copied or executed by this package. These Lean proofs were written
independently after reading the model and the PR448 discussion.

PR448's package and acknowledgement are higherbeing's work with substantial
Claude assistance, building on DaysSky's whole-residual hosting and the credited
community supplier lineage. Chafik Boukhalfa / chafreaky's PR451 note identified
the operator review point. This package adds a scoped Lean interface proof,
not a new discovery of that objection or a replacement for those experiments.

PR397's existing B_K scalar formalization (Tintagel packet) is credited and was
replayed rather than copied. Jacob Sussman's route/window and RAM Fourier/WHT
formalization, and the OpenAI framework it extends, retain their attribution.
The other community authors and maintained sources inspected are recorded in
AUDIT.json. Credits imply no endorsement. No theorem, comment or definition
from their Lean sources is copied into SingleStream.lean.
