# An all-field obstruction for the exceptional mixed Pappus frame

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped mathematical obstruction with a written proof and exact
finite corroboration. The exceptional mixed frame of Sagar Thakrar's
[#2274](https://github.com/CrocSwap/integer-mult-bounds/pull/2274), with
`a=(0,1,-1), b=(0,-15,15)`, has a frame-universal realization over a field
K **exactly when char K is different from two**. This replaces that
frame's bounded GF2/GF4/GF8/GF16 exclusion with an all-field theorem.
The earlier searches are cited, not rerun as this contribution.

The support zeros force three points onto one line and three Pappus lines
through an external point. [PROOF.md](PROOF.md) justifies normalization
even when allowed coordinates vanish. Three remaining incidences force
a required nonzero pairing to be 2a. The opposite-characteristic witness
has only +-1 and +-2 as nonzero integer pairings. Allowing just the first
coordinate of the Pappus-line covector to be nonzero admits the explicit
GF4 boundary witness in `verify.py`.

This concerns one common assignment for the whole fixed frame. It does
not exclude instance-specific CR2 certificates, prove a pairing-cost floor,
give a counterexample to the decoder conjecture, or improve kappa.
Independent human and formal proof-kernel review are unclaimed.

## Reproduce

From the repository root, with CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/pappus-mixed-frame-obstruction/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/pappus-mixed-frame-obstruction/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/pappus-mixed-frame-obstruction
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/pappus-mixed-frame-obstruction --check-source-history
```

Another CPython 3.12 installation can replace the local interpreter path.
The final command requires the publication commit and full Git history.
The direct checker also runs from a standalone copy of these six files.
It prints `PASS_PAPPUS_MIXED_FRAME_OBSTRUCTION` and a generated receipt
binding the check results to their SHA256 hashes. It writes no files and
uses only the standard library. Both registered modes retain all checks
with assertions disabled.

The checker enumerates the new normalized three-parameter equation core
over F2, F3, F4, F5, F7, F8 and F16. It checks the field arithmetic on
those fixed domains and all 4,752 core triples, the literal dot-product identity, every support and
pairing of the universal odd-characteristic witness, and the new GF4
relaxation witness. Mutation controls reject an incidence change and a
zero point; the unrelaxed support rejects the GF4 witness. Removing the
required nonincidence admits the stated F2 core control. Finite checks
corroborate the proof; they do not replace its universal quantifiers.

## Sources, scope and implementation

Canonical base is `a5df48c55ea806d7952b65acc9c76d878ff09b13`, priority
revision 7. The `formal-interface-lemma` card changes to this original
algebraic certificate obstruction. The selected source-binding first
example passed as metadata orientation only. No selected cold replay,
Lean or Docker build was run or required for this isolated proof.

Sagar Thakrar's #2274 supplies the exceptional frame, its integer data and
the finite exclusion question. Its archived README and `data/special.json`
are pinned as historical provenance in [SOURCES.json](SOURCES.json).
The 18 integer vectors in `verify.py` are the fixed mathematical fixture;
no predecessor executable is imported. The new normalized witness, GF4
relaxation control, algebraic proof and checker are this contribution.
DreamingOfClouds #2111/#2162/#2125 supplies the three-total decoder model
and CR2 route; #446/#595 supplies earlier cost-model context. Aaron Wang
#2427 studies adjacent classical pairing costs. All predecessor files
and their original notices remain unchanged. The proof uses standard
projective incidence algebra; no historical novelty is claimed for
classical Pappus geometry.

The claim and overlap checks are recorded in [TASK.json](TASK.json).
Live open PRs, recent account work and handoffs, active Discussions,
all-main distinctive README searches and merged-PR searches were checked.
Sparse local notes, arbitrary diffs and unpublished work limit coverage.
No absence-of-matches result is a novelty certificate.

Every loop in the checker has a fixed bound: at most 16^3 arithmetic
triples per field, 15*16^2 normalized core triples, nine rows and three
coordinates. Functions stay below 60 physical lines. Receipt reads cover
six files of at most 1 MiB each. No subprocess, network access, recursion,
dynamic code or shared mutation occurs. Managed Python allocation and
standard iterator dispatch are deviations from Power of Ten rules 3 and
9; fixed domains bound retained state to the constant fixtures, one
current triple and seven result rows. Warning-strict normal and optimized
commands provide recurring runtime diagnostics. No external static
analyzer is claimed.

## Open next questions

1. Does the exceptional frame satisfy the decoder inequality for the 70
   larger instances left open by #2274? The smallest useful step is a
   jet certificate for one skipped instance. The present obstruction
   removes the full-frame characteristic-two substitution route, but
   does not obstruct instance-specific assignments or prove any cost gap.
   Exponential pairing search remains the blocker.
2. Which other mixed Pappus frames have a universal characteristic-two
   obstruction? Start by detecting the same three-point collinearity and
   external three-line concurrency in one new support pattern, before
   launching a field search. Other coordinate constraints may require a
   different argument. This package holds no follow-up claim.
