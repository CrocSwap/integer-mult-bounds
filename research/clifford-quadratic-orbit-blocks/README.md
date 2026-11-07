# Two actual even-sector blocks for the Gaussian-dyadic three-qubit group

Under the retained group/table/width-nine/Gram premises, this source-bound calculation proves two actual even-sector irreducible blocks at tensor width ten. It answers a bounded part of Nick Petalas [PR6794](https://github.com/CrocSwap/integer-mult-bounds/pull/6794)'s actual stabilizer/decomposition question.

| Actual irreducible | Dimension | Width-ten multiplicity | Gram eigenvalue | Regular block dimension |
| --- | --- | --- | --- | --- |
| Sym²V | 36 | 2244 | 176715/32768 | 1296 |
| Λ²V | 28 | 2159 | 874395/131072 | 784 |

The last column is a contribution from the specified regular block, not the total multiplicity of an eigenvalue if other irreducibles coincide with it. These are actual blocks, not claimed global spectral endpoints.

The group is precisely the unitary three-qubit Clifford group over D=Z[i,1/2], with scalar kernel mu4 and z=iI, as in alephnan6714. Ordinary Hadamard and scalar omega/mu8 conventions would change this group. Legal generators S, Rx=((1+i)I+(1-i)X)/2, CNOT, Paulis and central iI stay within the source group.

## Mathematical scope

Use Hermitian Pauli matrices as Bell-matrix bases. Transpose parity separates Sym²V (36 dimensions) and Λ²V (28). Their distinct one-dimensional Pauli weight spaces are the two quadratic-form orbits; transitivity makes each module irreducible. The explicit map v tensor e_Q -> B_Q dagger v tensor B_Q identifies Vbar tensor µ with V tensor the ordinary permutation module on its quadratic orbit, with the actual phases cancelled. [PROOF.md](PROOF.md) supplies the quantified argument and source bindings; the finite checker is corroboration.

Two-transitivity gives permutation modules1+35 and1+27. The two degree35 table rows must be distinguished by transvection trace15 versus−5. The source width-nine multiplicities, rather than a rebuilt table or historical engine, then determine the two width-ten block values. The credited width-nine multiplicities give269+1975=2244 and269+1890=2159; the source Gram formula gives the table above. The written all-element argument and finite evidence remain distinct.

No full even-sector classification, actual spectral endpoints, sharp condition number, threshold improvement or total eigenvalue multiplicity is claimed. A regular matrix block's dimension is d²; other irreducibles may share its eigenvalue. Own completed6822's order-three/LP/traces are excluded and are not replayed.

## Evidence and reproduction

The first root-controlled diagnostic passed under CPython3.12.14 in0.3259265seconds at23.84375MiB maximum RSS, empty stderr and all14 then-present hashes unchanged. The new standard-library checker authenticates five retained source objects (75,775bytes) before any matrix calculation. It imports/runs no source scientific engine, full group census, full character-table calculation, native/Lean/Docker build, selected cold replay or old6822 order-three/LP work.

Observed domains:19 actual Gaussian-dyadic generators;1,216 signed Pauli conjugations,1,216 Bell congruences and1,216 complete8x8 intertwiner identities;4,096 Bell inner products and4,096 literal Pauli weight lines;77,824 distinct quadratic transport cases (two quadratic evaluations each), with77,824 linearity and77,824 symplectic-pairing comparisons;38 square-character checks. Ordered-pair BFS reaches1,260 and756 distinct pairs and checks38,304 directed generator edges. Four witnessed mathematical controls distinguish wrong dual, conjugation, degree35 row and transpose/Arf assignment; a separate multiple-Y basis-gauge guard does not call the alternate phase an illegal group element. Three strict parser controls also pass.

The Pauli matrices, quadratic forms and classical elementary quantities already appear in the source lineage. They are not new objects or a rediscovered construction. The new binding is the phase-correct intertwiner and these actual source-bound modules/multiplicities. The full21,547-byte packet is retained (SHA256 dfa9b37816dc1f9d8fe7393aa246374e4b751b26dddd6e309d9fad48b537feb1); subsequent direct/registered/export/hosted observations are separate delivery receipts. Finite generator/orbit checks corroborate the all-element written proof and inherited numerical premises; they are not human or proof-kernel acceptance.

```sh
python3.12 -B scripts/research_package.py --package research/clifford-quadratic-orbit-blocks
python3.12 -B scripts/check_research_commit.py --package research/clifford-quadratic-orbit-blocks --check-source-history --check-modes
```

SOURCES contains canonical selection/catalogue/legal provenance. SOURCE-PINS separately binds the five local inert mathematical source files to exact foreign head/path/blob/mode/size/SHA; their association was checked against resident source trees, with fresh matching bytes and current heads. These foreign commits are not publication ancestry. VERIFY.inputs=[] reflects the package-local runtime closure. Default normal/O commands compare the whole typed retained RESULT; --emit is generation stdout only, with no self-hash cycle or runtime Git/network.

## Open next questions

Determine an actually uncovered remaining quadratic-stabilizer representation and exact extension before claiming the full width-ten spectral endpoints. The other even irreducibles and possible eigenvalue coincidences remain unresolved here; no follow-on work is reserved. For physical use, bind one actual native caller and complete preparation/routing/chronology/precision/recovery/ownership/restoration/stock/recursive invoice. These costs are unknown. All five selected assumptions, selected kappa and frontier remain unchanged; the original native/formal task gate remains unmet.

## Credit and exposure

Credit Petalas6794 for the prior807 relaxation and actual-spectrum request; alephnan6714 for the group, source multiplicities, Pauli orbit, reciprocity and Gram framework; Lee-Yu-Peng-Lai for the published character table; Ali Romman/MatShep and retained Clifford/stabilizer lineage. Classical Bell/Pauli/symmetric/exterior/permutation/transvection/character methods retain priority. [LICENSE](LICENSE), [NOTICE](NOTICE) and exact source provenance remain.

The root proposed the unaccepted intertwiner/multiplicity recipe during prior orientation, including an ordinary-H/omega convention which source reading rejected before any new mathematical execution. Source-aware AI proposal/proof/implementation/overlap/metadata roles see those sources and the recipe. Substantial OpenAI Codex assistance is disclosed; this is not blind independent, human or proof-kernel acceptance. The inherited group/table/width-nine framework remains a source premise, not a newly replayed theorem.
