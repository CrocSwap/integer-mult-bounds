# Integral retraction and monomial reconstruction

Lean 4.30.0 checks the conditional bridge from three concrete integer matrix
identities to an image/kernel equality, an actual additive quotient isomorphism,
and unique multiplicative reconstruction. The package uses core/Std only.
It addresses the formalization question in [PR 1497](https://github.com/CrocSwap/integer-mult-bounds/pull/1497),
`audit.md` sections 8.2-8.3, under [Discussion 1527](https://github.com/CrocSwap/integer-mult-bounds/discussions/1527).
It does not instantiate the finite E8 matrices or prove their geometric use.

## Exact conditional result

`PR1497Bridge.lean` defines `Row n := Fin n -> Int`, finite sums, ordinary integer
matrix products, and the three-field proposition `MatrixIdentities M P Q W`:

```text
M : Mat m N,  P : Mat N d,  Q : Mat d N,  W : Mat N m
MP = 0,  QP = I_d,  I_N - PQ = WM.
```

For arbitrary natural dimensions, `MatrixBridge` proves that the integer row
image of `M` equals the kernel of `v -> vP`, identifies that image with literal
finite integer row combinations, and constructs the quotient by the relation
`v ~ w iff exists z, zM = v-w`. The quotient isomorphism has forward map
`[v] -> vP` and inverse `z -> [zQ]`. Integer lattice saturation is proved with
concrete integer torsion-freeness; it is not assumed as a certificate field.

For a lawful commutative group, signed powers, finite products, monomials and
their algebra laws are constructed in the source. From the individual relations
`x^(M_r) = 1`, `MonomialBridge` proves that the Q-defined parameter tuple
`theta_j = x^(Q_j)` reconstructs every coordinate as `x_i = theta^(P_i)`.
It proves reconstruction for every exponent row, the converse for arbitrary
parameter tuples, recovery and uniqueness of those parameters, and the explicit
residual product using `W`.

The custom group structures contain only operations and ordinary group laws.
The matrix certificate has exactly the three identities above. Image/kernel,
generation, quotient, saturation, monomial substitution and reconstruction are
proved conclusions. `SCOPE.md` gives the exact public interfaces and boundaries.

## Reproduction and observed evidence

Use an **already installed** Lean 4.30.0 at full commit
`d024af099ca4bf2c86f649261ebf59565dc8c622` and Python 3.12:

```sh
LEAN=/path/to/installed/lean python3.12 -I -B research/integral-retraction-monomial-bridge/replay.py > /tmp/integral-retraction-replay.json
```

`LEAN` may be omitted if the installed compiler is on `PATH`. Use its direct
binary rather than a package-manager shim. The wrapper checks release, full
commit and source hashes, then uses fresh temporary copies. Inherited `LEAN_*`
settings are discarded; only the scratch import directory is supplied. It
installs nothing, invokes no package manager and leaves compiler outputs in
temporary storage. The JSON receipt goes to standard output.

The replay sequence is universal compilation, its 159-query axiom census,
positive-fixture compilation, the combined 197-query census, three intended
negative compilations, and the unchanged Python tooling tests. A failed stage
stops the replay. The original `check_axioms.py` rejects missing, unexpected or
duplicate query reports and dependencies outside
`{propext, Quot.sound, Classical.choice}`. The wrapper also requires successful
compilation and fresh `.olean` outputs before accepting those reports.

`REPLAY.json` records the actual local run on `arm64-apple-darwin24.6.0`, with
Python 3.12.14. Universal and positive sources compiled without errors or
warnings. All 197 queried declarations reported; the observed dependency union
was only `{propext, Quot.sound}`. No `sorryAx` or custom axiom dependency was
observed. Each negative fixture failed at exactly its intended false `decide`
proposition, rather than an import or syntax error. All ten Python tooling and
synthetic arithmetic tests passed.

The positive fixtures include a signed nonzero-W certificate, negative powers,
an ordinary integer-addition group interface, a Bool XOR torsion group, direct
calls of the universal quotient/reconstruction interfaces, and missing-identity
countermodels. The three negative files separately reject a wrong W sign,
omission of `MP=0`, and omission of `QP=I`. Synthetic fixtures are separate from
an E8 instance or a field/unit adapter.

The producer delivered source without running Lean and supplied diagnostic
repairs. Later local replay supplies the execution evidence. Packaging changed
only the introductory comments in the main and positive Lean files to report
that evidence and normalize the observed model attribution. Every byte after
those comments is unchanged. The axiom parser, tooling tests, and negative
fixtures are byte-identical to the repaired delivery. `SOURCES.json` records
both original and packaged hashes; `REPLAY.json` also records the body hashes.

The generic package hook runs only the Python tooling tests, not Lean:

```sh
python3.12 scripts/research_package.py --package research/integral-retraction-monomial-bridge
```

A generic CI pass therefore does not establish kernel acceptance. Use the
separate exact-version replay above for that evidence.

## Open next questions

Connect one pinned E8 instance to the concrete `MatrixIdentities` interface and
provide a lawful field nonzero-element group adapter. This would connect the
conditional bridge to actual finite data. The first step is to choose exact
M/P/Q/W source bytes from PR 1497 and check their Lean instance separately from
the adapter. `TASK.json` records the question and blockers.

The geometric generator-to-relation and coverage obligations remain separate.
This package supplies no E8/P112/P120 matrix instance, rank API, field `Units`
adapter, Laurent scheme, local Lemma 5, decoder K, all-size compiler, or full
multiplication theorem. It changes no selected frontier or supplier profile.

## Attribution and provenance

Andrey Mas, with substantial **GPT-6 Pro** mathematical formalization and
diagnostic repair through ChatGPT, as identified in the browser UI. Codex
prepared source briefs, coordinated, audited execution, replayed and mechanically
packaged the artifact. No mathematical proof repair was made locally. A
producer self-reported variant label was not independently verified.

The source statement is PR 1497 at
`7a1309f18f56d04c2db33bf1607e0332d19f72b3`,
`research/complex-rank8-ratio-gluing-audit/audit.md`, sections 8.2-8.3; its exact
bytes were checked locally. Inherited context credits **Brett Halligan /
burntout76 and Ninefold**, [PR 1212](https://github.com/CrocSwap/integer-mult-bounds/pull/1212);
**DreamingOfClouds**, [PR 717](https://github.com/CrocSwap/integer-mult-bounds/pull/717);
and **themilkman216**, [PR 968](https://github.com/CrocSwap/integer-mult-bounds/pull/968).
No predecessor Lean implementation was copied. Apache-2.0; see `LICENSE`.

Historical task-card and selected-record provenance remains at revision 2,
`ddb4371c16a5a5de9e363afa8c0d6d7c27429e3c`. The publication checkpoint is
main `81e81af67714bdc8d1693b0bf5c29468b92f62ff`, priority revision 3; the independent
verification follow-up remains relevant. `TASK.json` records the changed scope
without remapping the original card into the newer catalogue.
