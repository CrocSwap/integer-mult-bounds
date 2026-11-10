# Independent phases for all nineteen P104 LOCAL stages

The frozen PR6348 caller has 19 LOCAL stages on 104 retained ports. This package
independently verifies all **7,904** forward/inverse contact phases and matches
the complete translation ledger of the actual physical consumer. It completes
the stage range left open by unpaidmoon's stage-one check, rather than claiming
the original caller's successful author replay as a new discovery.

## Exact scope and proof

Let `C` be the nine central coordinate axes, `F_s` the eight fresh axes for
stage `s`, and `S_s` the eight-axis blocks strictly before that stage. Every
actual LOCAL event in the pinned controller has `1 <= s <= 19`. Its route fixes
all axes outside `C union F_s`, and swaps an orthonormal basis of `q`'s central
orthogonal complement with `F_s`. The central odd vector `q` is fixed. The
eight swap vectors are pairwise orthogonal and isotropic, so the linear route
is an orthogonal involution. These properties are checked for each source port.

Write a phase as a sum modulo four of weighted binary parity functions. The
raw, entry, exit and output phases are exactly those declared in the pinned
`physical.py`. In each of its four contact equations, the same sum of phases
on `S_s` appears on both sides. Because the route fixes those axes, it cancels
on arbitrary inputs. Later blocks are absent from both sides. Thus the entire
equation reduces to nine central plus eight fresh coordinates; relabelling
the fresh coordinates maps this core to every actual stage. This is why the
stage range can be checked without enumerating `2^161` addresses. The independent
ledger uses the actual controller's stage order and source port order.

For binary variables, parity on a support `A` satisfies

```
parity(A) = sum(x_i) - 2 sum(x_i*x_j)  (mod 4).
```

Terms of degree at least three have coefficients divisible by four. A sum of
weighted parities, including after a binary linear route, therefore has degree
at most two modulo four. Its values at zero, singleton inputs and pair inputs
determine its constant, linear and mixed coefficients exactly. The new engine
evaluates these inputs directly using bit parity; it does not import the
predecessor polynomial, route, contact or stage-one implementation.

For each contact, singleton differences must be even. They uniquely determine
the physical translation. Evaluating every pair then verifies that no mixed
term remains. The inverse is separately checked with the routed translation.
Evaluation at zero retains the absolute constant phase. This proves the phase
identity on every input in the declared diagonal operator model, not just on
the tested basis addresses. Spectator cancellation and coordinate embedding
then give the same identity for every source stage. All translations remain
inside seventeen active axes and the source dimension 161.

After the contacts, subtracting raw from output phases cancels the central and
earlier blocks, leaving exactly the eight fresh-axis phases `D_s`; the cross
phase additionally contains `-q`, hence `D_s Q^-1`. This is an algebraic identity
of the declared boundaries, not a claim about the supplier's internal word.

## Reproduce and reject

```
python -B scripts/research_package.py --package research/p104-all-stage-contacts
```

Each registered normal/optimized replay authenticates every input before parsing,
derives the independent ledger and runs the unchanged source `physical.py` with
its original phase backend. The complete fresh consumer result must equal its
frozen receipt, while the independent translation ledger must match the
consumer's digest. The equality is source-relative and uses SHA-256 binding;
the original consumer is a comparison, not the independent engine.

Controls reject malformed/tilted source bases, invalid ports, missing/reordered
stages, changed source bytes, a changed final translation and reversed consumer
port order. Coordinate-port and mixed-parity controls exercise the evaluator.
The registered tests use explicit failures and work under optimized Python.
The consumer executes additional endpoint/idle checks as part of its unchanged
body; this package does not claim independent coverage of those extra results.

## Limits

This is a scoped phase proof and finite source-bound certificate. It does not
replay a changed supplier word, its scalar endpoint, owned lifetimes, native
Gaussian normalization, all positive column widths, compiler, funding or outer
predicates. Application to PR6353 or a later successor also requires checking
its exact port and caller contracts; no automatic transfer is claimed. No new
bound, selected-frontier change, human review or proof-kernel acceptance.

## Open next questions

Bind the exact changed supplier to the certified LOCAL boundary and verify the
remaining native, ownership, funding and outer obligations. Start from that
successor's own sources, not from the presence of this certificate.

## Credit

Ali Romman supplies PR6348's balanced query tree, the physical consumer and its
retained PR5544/PR4359 native-phase lineage. The original phase data, Clifford,
helper, recursion and outer authors retain their attribution in their unchanged
sources. unpaidmoon's stage-one package at commit
`6205312028bd6d58cd297eb2f7c98f5ebfa5ce35` identifies the remaining stage range;
its code is not imported or copied. PR6361's Laurent endpoint audit is distinct
from physical phase contacts. Binary parity expansion and spectator cancellation
are classical. The new implementation is a direct evaluation check of this
specific full contact family. Apache-2.0. Prepared with substantial OpenAI Codex
assistance; both new implementation and written proof are AI-assisted work.
