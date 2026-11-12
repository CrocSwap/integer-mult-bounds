# Height-one integral shear bicliques have exact balanced optimum six

The largest balanced rank-distance biclique among the 81 two-by-two integer
matrices with entries in {-1,0,1} is exactly **K_(6,6)**. Distinct matrices
within each part have rank-two difference; every cross-part difference has
rank one. The twelve associated integral four-by-four shear frames commute.

Claim type: **exact finite certificate**, with a written construction and
a proof reducing the ceiling to a complete finite enumeration.
This contribution was produced by Nick Petalas. No new kappa is claimed.

## Construction and ceiling

For the six integer solutions used here of `a^2+ab+b^2=1`, take

```text
E(a,b) = [[a,b],[-a-b,a]],  O(a,b) = [[a,b],[b,-a-b]].
```

Their determinant identities prove attainment. For the ceiling, every
pairwise rank-two triple in the complete 81-matrix inventory has at most
six common rank-one contacts. Thus a K_(7,7) is impossible. Two separate
enumerations agree on all 23,488 admissible triples and their complete
contact-count histogram. [PROOF.md](PROOF.md) gives the identities, histogram
and coverage arguments.

Nick Petalas / petalas [#6174](https://github.com/CrocSwap/integer-mult-bounds/pull/6174)
asks how coefficient height limits integral bicliques. Its all-size construction
gives a quadratic-height upper bound and no exact height-one ceiling.
This settles that first bounded inventory. Jerry Chen / CubeJerry
[#907](https://github.com/CrocSwap/integer-mult-bounds/pull/907) supplies the
earlier eight-frame example and the abstract distortion formula
`c_1(K_(r,r))=2(r-1)/r`. Applying that cited theorem gives distortion 5/3
for this new twelve-frame configuration; its cut proof is not replayed here.
The rational shear model originates in eumemic
[#288](https://github.com/CrocSwap/integer-mult-bounds/pull/288).
The separate common-flag and signed-rank obstructions of navinor #825 and
Jeremy Diviney #836 remain relevant. All predecessor attribution is retained
in the unchanged source packages. Apache-2.0.

Base main is `e54523517d0f03e58352e647c403a5af3e525a57`. The full original
`complex-rank-shape-decoder` card is pinned in TASK.json. Its scope changes
to a coefficient-inventory side result. Rank geometry and distortion alone
do not supply a decoder, productive credit or a favorable complete invoice.
The contextual picker reports its historical #5599 assessment differs from
the selected #7000 record. Selected kappa `363005817/100000000000` is unchanged.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19572817)
reserves this exact height-one question.

## Reproduce

From the repository root, with CPython 3.12 and only its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/height-one-shear-bicliques/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/height-one-shear-bicliques/ceiling.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/height-one-shear-bicliques
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/height-one-shear-bicliques --check-source-history --check-modes
```

A CPython 3.12 executable at another path can replace the local interpreter.
VERIFY.json registers warning-strict normal and optimized runs of both
verifiers, each with a 60-second timeout. Both commands are read-only and
work without Git or predecessor files. The source pins are provenance only.
No predecessor scientific executable is imported or replayed.

The expected direct markers are `PASS_HEIGHT_ONE_SHEAR_BICLIQUES` and
`PASS_FIRST_ROW_SHEAR_CEILING`. The primary JSON receipt includes the complete
witness, histogram, ordered triple-trace hash and SHA256 of all seven package
files. It is generated on every run. The separate checker uses Fraction
elimination, a first-row enumeration and the actual four-by-four shear ranks.
Ten rejection controls and five elimination fixtures test the stated boundary.

## Limits

Only the height-one integral two-by-two inventory is optimized. There is no
physical native implementation, complete caller, dirty restoration, paid
supplier invoice, compiler closure, tape/precision realization, complete
multiplication theorem or discharge of any selected framework assumption.
No selected cold replay, Lean or Docker run is relevant to this certificate.
Independent human and formal proof-kernel review are unclaimed.

## Open next questions

1. What is the balanced optimum at height two? Start by reducing the contact
   equations for its 625 matrices; a larger exact enumeration or a general
   coefficient-height theorem is missing.
2. Can these twelve frames participate in a favorable completed interface?
   First specify legal gates, targets, arbitrary dirty inputs and paid cleanup,
   and identify a hypothesis escaping the common-flag obstruction. None is
   supplied here; the metric example alone does not imply a coding gain.

## Verification-code bounds

Both scripts use bounded loops and no recursion or subprocesses. The primary
stores two 81-entry bitset graphs; the other stores an 81-by-81 rank table.
No triple list is retained. Every function is below sixty physical lines.
Errors propagate as exceptions, and checks do not depend on assertions.

Power-of-Ten rule 3 has a managed-runtime deviation in both scripts. Python
and Fraction allocate during enumeration. Input domains are fixed to 81
four-entry integer matrices, matrices of order at most four for elimination,
85,320 primary triple visits and 61,236 secondary candidates. Only the fixed
graphs, one matrix/triple at a time and a histogram of at most 82 bins remain
live. Normal and optimized replays verify those enforced domains. A port to
fixed-capacity arithmetic would be needed for allocation-free execution.
Python's dynamic dispatch is a runtime constraint; all scientific calls have
fixed, direct targets and no callbacks, plugins or dynamic evaluation.
