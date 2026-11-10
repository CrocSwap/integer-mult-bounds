# The fixed P104 prefix schedule already has the optimal concave tail

The exact minimum delivery-tail price on the fixed prefix paths of Adam
Gall's [PR1940](https://github.com/CrocSwap/integer-mult-bounds/pull/1940),
using 32 monotone fixed-term chains, is

```text
85 f(1) + 17 f(2) + 19 f(3) + 20 f(4).
```

This holds for every concave rank tariff on the integer ranks 0 through 8
with f(0)=0. In particular it holds simultaneously for every f(r)=r^s,
0<s<1. Reassigning these read frames to different chains cannot improve
that tail. A cheaper proposal must change another part of the contract.

This is a scoped optimality proof with an exact finite dual certificate.
The attaining histogram and the 32-chain construction belong to PR1940;
their optimality on its fixed prefix paths is the new result. This settles
the fixed-path part of that package's third Open next question. Target read
orders are frozen. No global optimum over changed read orders is claimed.

## Proof and evidence

[PROOF.md](PROOF.md) reduces each centre's chain assignments to a
fixed-cardinality bipartite matching. [CERTIFICATE.json](CERTIFICATE.json)
contains integer potentials for seven hinge tariffs at each of eight
centres. The verifier checks every residual arc directly, giving **56 dual
witnesses and 3,752 nonnegative reduced-cost inequalities**. A discrete
concave function is a nonnegative combination of those hinges plus a
linear function. All covers have the same rank mass 256, so the duals
prove the stated minimum for the entire tariff class.

The domain contains all partitions of the 116 distinct centre/read-frame
nodes from the pinned parent edges into 32 nested fixed-centre chains.
Each chain enters at its singleton survivor and exits at the full
nine-dimensional frame. Entry and exit moves are included. The proof
allows every strict inclusion link, including links absent from the
published cover. Chronology is preserved by increasing frame dimension.
The fixed target tails and scalar reads add constants to this optimization.

The exact centre values remain supplied at entry, as in PR1940. Formation
of the 24 extra copies, arbitrary dirty-state restoration, side corrections,
native phase/width realization, hosting, precision/tape and all-size
compilation remain separate obligations. No current supplier invoice,
new kappa or complete multiplication theorem is claimed. The selected
frontier and its five assumptions are unchanged.

## Reproduce

From the repository root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/p104-prefix-tail-optimum/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/p104-prefix-tail-optimum
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/p104-prefix-tail-optimum --check-source-history
```

Replace the interpreter path with another CPython 3.12 interpreter when
needed. Normal and optimized direct replays must print
`PASS_P104_PREFIX_TAIL_OPTIMUM chains=32 frames=116 duals=56 inequalities=3752 controls=8 all_concave no_new_kappa`.
The package runner must print `PASS_REGISTERED_RESEARCH_PACKAGE`.

Normal replay is read-only. `--emit-certificate PATH` deterministically
regenerates the dual certificate. `--emit-receipt PATH` generates the
hash-bound result receipt after checking the certificate and eight semantic
rejection controls. No optimization library or floating-point arithmetic
is used by either path. [RESULT.json](RESULT.json) binds all seven package
inputs and both live predecessor files by SHA256.

## Source and implementation scope

Canonical base is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority
revision 8. The question source is PR1940, head
`a9b7dfe2809092a9a4c90784d12bb60061e995e8`.
[SOURCES.json](SOURCES.json) pins the unchanged schedule and README at the
canonical base. [TASK.json](TASK.json) records the changed scope from the
current supplier card to this historical supplied-copy interface. The
selected bindings-only positive control passed; predecessor scientific
replays were not run or claimed as new work.

Source files are capped at 256 KiB. The problem has eight centres, at most
20 nodes per centre, at most 42 residual vertices, seven hinges and at most
440 residual arcs per centre/hinge. The optional generator makes at most
42 relaxation passes per witness. Acceptance uses explicit exceptions
under normal and optimized Python. Functions stay below 60 lines; there
is no recursion, network access or subprocess call.

Power of Ten rule 3 deviation: CPython, JSON, lists, dictionaries and integer
arithmetic allocate dynamically. This is confined to the bounded input,
graph and certificate sizes above; file handles close on every exit.
Verification checks those capacities and all dual inequalities. A larger
problem requires a new capacity review before changing these limits.

## Open next questions

- Can different target read orders give a cheaper 32-chain supplied-copy
  tail? Start with one changed parent-edge witness and rebuild all target
  and delivery moves. The present certificate freezes those parent edges
  and does not supply a global ordering bound.
- Can an actual producer form and restore the 24 extra exact copies within
  a favorable complete bill? Start with one rank-four-ending chain and
  its arbitrary dirty-input correction. The required physical producer
  and restoration contract remain missing.

## Credit

This contribution was produced by Nick Petalas. Credit Adam Gall / PR1940
for the question, prefix schedule, attaining histogram and supplied-copy
boundary; Ali Romman / PR1125 for the 32-path obstruction; Josie Elliston /
PR1071 for the pinned fixture; themilkman216 / PR968, DreamingOfClouds /
PR717, PR446 and PR595, and Joel Pulikkan / GamingPuzzled / PR620 for the
decoder and geometry lineage. Minimum-cost matching potentials and the
discrete hinge decomposition are standard methods. The new contribution
is this source-bound optimum for every concave rank tariff. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.
