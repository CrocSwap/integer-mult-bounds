# Every real body-sign profile has the same selected Type A factor circuit

This scoped computer-assisted proof extends ToikY's [PR #7439](https://github.com/CrocSwap/integer-mult-bounds/pull/7439)
from one nonunit body profile to all 17 independent real body signs.
Every factor in its fixed 20-factor full-suffix selection is conjugate to
its unit-body factor by one explicit diagonal sign matrix. This contribution
was produced by Nick Petalas.

For gathered roles `j` and `18+j`, `0 <= j <= 17`, the diagonal entry is

```text
E_jj = E_(18+j,18+j) = product_(r=1 to min(max(j-1,0),8)) D_r.
T_i(D) = E(D) T_i(1) E(D)^(-1)   for every selected i.
```

The later nine signs cancel from these normalized factors. They are applied
at all their literal body contacts. It follows that any unit-body rational
transvection factorization transfers to every real body-sign profile.
Together with the cited 19-factor witness of #7439, this closes its real
body-sign extension for the normalized selected circuit. The predecessor's
witness and minimum-length theorem are not replayed or claimed as new here.

[PROOF.md](PROOF.md) gives the exact model, prefix-transport lemma, gauge,
character-ring certificate and limits. [inputs/ORIGIN.json](inputs/ORIGIN.json)
binds the unchanged literal caller to #7439 head
`ba83c9bebd99502cd64bb1cab2bc4e5336d9d7b2`. The source data is retained, so
reproduction needs no pending branch or network access.

## Evidence and reproduction

From the repository root, using CPython 3.12 and only the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/p104-real-body-factor-gauge/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/p104-real-body-factor-gauge/independent.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/p104-real-body-factor-gauge
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/p104-real-body-factor-gauge --check-source-history
```

Use another CPython 3.12 interpreter path on other machines. Expected markers:

```text
PASS_REAL_BODY_FACTOR_GAUGE selected_factors=20 signs=17 nonzero_entries=659 controls=6
PASS_INDEPENDENT_REAL_BODY_GAUGE profiles=21 entries=544320 omissions=21
```

The primary verifier checks both complete endpoints and every selected
displacement entry over the exact rational sign-character ring. It covers
all simultaneous body signs without sampling. Six negative controls reject
missing host body action, missing idle body action, two wrong gauges, a
changed factor coefficient and changed input bytes. It prints a generated
receipt bound to the hashes of all package files; normal replay writes no
files.

The second implementation obtains factors from negative prefixes and literal
full-suffix transport. It checks the new gauge on 21 nonunit profiles,
including four mixed profiles, and checks selected products on all basis
columns. It imports no executable code from the primary checker or from a
predecessor. This is independent implementation structure by the same
contributor, not independent human review or proof-kernel acceptance.

## Scope and credit

The result is a normalized real-sector identity. Arbitrary complex phases,
the two imaginary central signs, native host reuse, physical sign synthesis,
ownership/restoration and complete supplier pricing remain open. There is
no kappa or selected-frontier change. The full-host price obstruction of
#7439 remains applicable to its stated replacement model.

ToikY's [#7457](https://github.com/CrocSwap/integer-mult-bounds/pull/7457)
also excludes reusing enough old hosts under their fixed negative-prefix
frames and unit bodies. This package supplies no escape from that premise.
Its factor conjugacy differs from the diagonal body-retiming gauge of
[#7144](https://github.com/CrocSwap/integer-mult-bounds/pull/7144), which
keeps the scalar/HOST skeleton and nonnegative replacement body powers.

Credit ToikY for the full-suffix selected circuit, the unit-body witness,
the one-body gauge and its arbitrary-body opening; Rohan Arun for the
literal signed #7113 caller; Clear1nsight for #7334; and the P104/native
lineage retained by those packages. The present theorem, positive-prefix
transport derivation, exact character certificate and two checkers were
produced by Nick Petalas. Classical conjugation and sign-character algebra
are used without a claim of general mathematical priority. Original source
notices are retained in [NOTICE](NOTICE).

Card `p104-side-correction` has changed scope. The selected record is #7000
on base `e54523517d0f03e58352e647c403a5af3e525a57`; revision-8 prose and
the card retain older supplier context. This is a bounded interface step
toward a completed changed supplier, not another audit or admission run.
The card's first baseline binding check passed. Current overlap was checked
against live PRs, handoffs, active discussion #7111, cached card coverage
and canonical-main package notes. Those checks are not a novelty proof.

## Verification implementation bounds

Both programs are nonrecursive and use exact rational arithmetic with
explicit error checks that remain active under Python optimization.
The source is hash-pinned and capped at one MiB and 4,783 events; dimensions
are fixed at 36, 17 signs and 38 relative factors. Primary expanded actions
are capped at 20,000 and each character dictionary at 2,048 entries. All
loops range over those bounded data or fixed profile/role/factor inventories.
Registered checks have 120-second limits.

Power-of-Ten rule 3 has a managed-runtime deviation in both checkers:
CPython's arbitrary-precision rationals and dictionaries allocate during
arithmetic. Fixed source/input dimensions, the character cap and fixed
profile inventory bound the live problem; no workers, subprocesses or
persistent resources are created. Replacing this with fixed storage is
deferred until a native implementation is justified. Rule 9 has a narrow
deviation in the primary negative controls: bounded local callbacks pass
only six explicitly defined rejection cases to the exception checker.
No dynamic import, generated code or external solver is used. Warning-as-error
execution and AST compilation are the diagnostics for these Python files;
no separate configured static type checker is added to this research package.

## Open next questions

1. Does an analogous common conjugacy exist for arbitrary fourth-root body
   phases and the imaginary central signs? This would decide whether the
   normalized witness extends to all native sectors. Start with the same
   literal contacts over a rational Gaussian character ring. The real-sign
   simplifications and scalar `Q=-I` transport premise need replacement.
2. Can a changed negative-prefix frame deliver a conjugated factor while
   preserving an actual old host's body, mate and ownership contracts?
   This could change the complete paid comparison outside #7457's fixed-frame
   obstruction. Start with one host and its full physical input/output
   contract. A new frame delivery, legal reuse and favorable complete bill
   are all missing here.
