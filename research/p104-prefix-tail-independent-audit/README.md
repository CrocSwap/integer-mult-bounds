# Independent audit of the P104 tail-prefix certificate

A separate exact interpreter corroborates [AAAmirinu's PR2358](https://github.com/CrocSwap/integer-mult-bounds/pull/2358),
head `e8950db523c9682518049a42cfc28642224292ff`, in its **rational pooled-snapshot model**.
The shared correction dimension is 99 on cuts 2718–2753 and 98 on cuts 2754–2823;
2754 is the earliest cut attaining 98. These are the predecessor's results,
not new minima. The contribution is separately implemented finite evidence and
an independent written check of the rank reduction and its required premises.

The interpreter imports no predecessor Python code. It uses Fraction-valued
sparse rows, canonical binary row elimination and an every-cut scan, instead
of the predecessor's integer/8 rows, enumerated binary subspaces and changed-group
collector. The parent inspected predecessor mathematics/interfaces/code before
implementation: this is a separate implementation, not a blind audit. The
specialist independently checked the written algebra and then reviewed the new
interpreter. Neither is independent human review or a formal proof assistant.

## Evidence and scope

The replay reconstructs the punctured E8 root ordering and `RR^T=104I`, carries
all 280 independent target/source/dirty columns through all 4,058 original
events and 4,059 cuts, checks scalar common frames, nested paid transports,
private-copy lifetimes, all endpoints and the unchanged local profile.
It scans every cut's matching donor/target frames. Full-row interning removes
only duplicate algebra, and recovers exactly 110,814 distinct target/snapshot
pairs and 324/427 nonzero target/coefficient pairs through cuts 2753/2823.

Every eligible donor has zero own-target dirt and source part in row(R).
The other 175 nuisance units are available at cut zero. These premises justify
projecting arbitrary serving spaces in all 280 columns into source space.
The proof then gives

```
h(c) = min rank(C+12AR) = 96 + min rank(I8-RA),
C = I104 - R^T R/8,    A_t in L_t(c).
```

All generators satisfy the six/three required annihilator functionals.
The compressed residual determinants are fixed at −2/−1, proving the universal
rational lower bounds. All 18/46 upper contacts are replayed at their exact
cuts; direct rational ranks of the 104-by-104 corrections are 99/98. The small
residual ranks are 3/2; the cut-2754 residual also matches its explicit two-term
factorization. Monotonicity joins these lower and upper certificates.
[PROOF.md](PROOF.md) spells out the rank-nullity derivation and projection premises.
[RESULT.json](RESULT.json) is the exact finite receipt.

There is **no chronological correction, paid transport-cost bound, global owner
map/moment, native Gaussian regeneration, recursive precision/all-size proof,
selected cold replay, admitted supplier or new kappa**. Pooling combines original
snapshots at different times and grants nuisance subtraction for free. Inserting
contacts into an actual circuit need not preserve those later snapshots.
The evidence is finite exhaustive trace replay plus a written all-rational
conditional argument, not a formal-kernel proof of multiplication.

## Reproduce

Python 3.12 standard library, no network for direct replay:

```sh
python3.12 -I -O -B research/p104-prefix-tail-independent-audit/verify.py
python3.12 -I -O -B research/p104-prefix-tail-independent-audit/test_verify.py
python3.12 scripts/research_package.py --package research/p104-prefix-tail-independent-audit
```

The verifier checks immutable inputs and the byte-identical predecessor
certificate. `--out NEW.json` refuses an occupied path. Eight control groups
cover equivalent frame bases/contact order, wrong coefficient, future/self
contacts, nonzero compensation/cleanup faults, illegal scalar/private frames,
a forbidden lower generator, and explicit low-rank matrices when compression
premises are dropped. All mathematical guards remain enabled with `-O`.
The registered hook includes the tests and exact source pins. Local CPython
3.12 optimized registered replay passed all eight groups after the zero-row
Fraction hardening; a Git-free CPython 3.14 optimized export passed unchanged,
and source-pin/occupied-output controls rejected. Selected-record integrity
passed; hosted CI remains separate.

## Open next questions

Realize and fully price one complement under actual lifetimes, including source
reads, creation/restoration, frames and chronological owners. Begin from the
separately claimed 41-contact lift rather than duplicating it. This is blocked
by the difference between pooled access and executable access; even a valid
local lift does not supply the missing shared complement or a full moment.
[TASK.json](TASK.json) records the concrete next step and limits.

## Attribution

The copied certificate's exact origin, hash and Apache-2.0 attribution are in
[CERTIFICATE-ORIGIN.json](CERTIFICATE-ORIGIN.json). AAAmirinu/#2358 supplies the
six/three annihilator certificates and 46-contact witness; AAAmirinu/#2345
supplies the reduction and 18-contact rank-99 witness. Gonzalo Mier/#2173
supplies the pooled model, Gareth Davidson/#2251 the full-pool complement,
and @josecarlosgonzalezroque-design the late-prefix handoff. Rohan Arun/#1972
supplies the frozen scalar/frame channel; Chafik Boukhalfa/#1991 its native
package; Adam Gall/#1940 the schedule; Josie Elliston/#1071 the fixture, with
Ali Romman/#1125 and the retained PR968/717/446/595/620 lineage.

Prepared for Ross with substantial OpenAI Codex assistance in proof, code,
controls and writing. Independent exact-circuit specialist proof/code review
is AI-assisted. Apache-2.0. Existing source files/notices and selected records
are unchanged. The manual trial tests the saved prompt's lifecycle, not the scheduler.
