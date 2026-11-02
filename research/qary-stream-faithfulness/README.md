# Sharp q-ary point-column faithfulness thresholds

Scoped written proof with exact finite corroboration, produced by Nick Petalas.
Apache-2.0. Independent human and formal proof-kernel review are unclaimed.

Let q=p^e, let payload coefficients have characteristic p, and let each
GL_d(F_q) or AGL_d(F_q) label act on w point columns with the same linear
map and translation on every column. For arbitrary full payloads, the
least widths making the group-algebra action faithful are

| Group | d>=2 | d=1, q>2 | d=1, q=2 |
| --- | --- | --- | --- |
| GL_d(F_q) | d | 1 | 0 |
| AGL_d(F_q) | d+1 | 2 | 1 |

Faithfulness holds at every larger width, including every block of a complete
dirty-register endpoint. [PROOF.md](PROOF.md) proves the universal statement.
This extends ywz65's binary-only PR2599; it does not replay its theorem or
the predecessor target-minimum censuses. The new one-dimensional affine
case needs a separate obstruction: the difference between the sums of two
multiplier cosets is formally nonzero but acts as zero on a single point.
The group norm alone cannot prove that case, because its stabilizers have
order q-1, which is nonzero in characteristic p.

A literal F_3 witness uses two arbitrary dirty payloads, ten full-address
operations and six scalar ADDs. Its formal endpoint is I+u_2 E_01. It is
identity on every input at width one, while six dirty basis columns expose
it at width two. These are logical records, not elementary native prices,
and no cheaper monomial target is claimed.

## Evidence and reproduction

From the repository root, use CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/qary-stream-faithfulness
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/qary-stream-faithfulness/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/qary-stream-faithfulness/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/qary-stream-faithfulness --check-source-history
```

On another machine, substitute its CPython 3.12 executable for the absolute
workspace path. The registered normal and optimized checks use the active
interpreter. Expected markers are `PASS_QARY_STREAM_FAITHFULNESS` and
`PASS_REGISTERED_RESEARCH_PACKAGE`.

The verifier enumerates fifteen group fixtures, comprising 853 group elements
across those fixtures. It checks 158 complete below-threshold addresses, all
their stabilizer counts and explicit annihilators, fifteen separating orbits,
and full permutation-matrix ranks for twelve line actions. Fields of orders
2,3,4,5,8,9 include genuine extension fields; all 1,465 field triples are
checked. Separate formal and literal replays check the affine-line alias
on all 24 dirty basis columns across its two widths. Fourteen controls cover
lost separation, the affine-line exception, wrong characteristic, a missing
coset term, invalid/reducible fields, six omitted scalar ADDs, the dirty input
boundary and altered source bytes. Checks remain active under `-O`.

Each run prints a generated JSON receipt containing its outcomes and package
SHA256 values. Redirect it outside the checkout if retention is desired.
The source README is authenticated without importing predecessor code.
[SOURCES.json](SOURCES.json) pins the exact source and historical catalogue;
[TASK.json](TASK.json) records the scope change and structured next questions.

## Scope and limitations

This refines `bit-new-register-model` to a q-ary algebraic interface side
result. The card's current first baseline command passed source bindings
only. The selected record remains PR6030, conditional kappa 781451/250000000.
The theorem distinguishes formal group-algebra identities from actual
full-stream identities when changing the address alphabet.

The coefficient characteristic, full arbitrary payload space and common
affine translation are explicit premises. Different coefficient
characteristics, restricted payloads, independent per-column translations,
integer carry arithmetic and native frame actions need separate arguments.
No target-call saving, native or physical supplier, complete caller invoice,
compiler/stock/precision/tape result, selected-frontier change or new kappa
is claimed. All five selected framework assumptions remain. Selected cold,
Lean, Docker and predecessor scientific replays were unrun. Finite evidence
corroborates the written proof; it is not independent mathematical acceptance.

## Open next questions

Can a specific nonbinary native caller realize this diagonal action with a
complete paid boundary? This would decide whether the interface can transfer
a formal supplier claim. Start by naming its address encoding, legal scalar
and address operations, all arbitrary dirty inputs, and restoration costs.
No such caller or favorable complete invoice is supplied here.

What is the complete annihilator ideal of the single-point affine-line
action in defining characteristic? The displayed coset relation proves
nonfaithfulness but does not classify the kernel. Start with the enumerated
permutation-matrix spans and seek a universal presentation. This package
does not derive a general image-rank formula, and reserves no continuation.

## Sources, overlap and credit

Base is canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority
revision 8. The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19362326)
names the original q-ary question. Main README searches included general-field
and general-group formulations, alongside live open/merged PRs, recent account
work, active Discussions, the latest handoffs and local reservations. The
cached card report covered 387 open PRs and 6,319 Discussion records with
complete remote pagination, but only 118 of 8,917 main note paths. Supplemental
Git searches covered main README text. Sparse notes, unpublished work and
arbitrary historical diffs remain limits; absence of a match is not a novelty
certificate.

ywz65 / PR2599 retains the binary thresholds and regular-orbit/norm method,
and PR2629 retains its distinct binary kernel-checked interface. Woklerx
retains the finite-address regular-action bridge. Gareth Davidson / PR1333
retains the formal-versus-represented distinction; Josie Elliston and Hanson
Sun retain the GL3 census context. Orbit-stabilizer and group-algebra norms
are classical. The contribution here is the sharp defining-characteristic
q-ary application, its affine-line coset obstruction and complete dirty alias.
No predecessor credit line or source is changed, and no literature-wide
priority is claimed.
