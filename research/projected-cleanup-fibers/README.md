# A raw endpoint does not determine its projected cleanup

**Uniform scalar theorem and selected-word counterexample; no new κ.** For any
positive numbers k of source/helper coordinates and q of targets, the raw
matrix of a unit-XOR word and the matrix obtained by deleting target writes
range independently over

`GL(k+q,2) × { [A B; 0 I] : A invertible }`.

The construction uses the same dirty registers, with every operation counted.
An identity loop can change the projected matrix by one elementary gate in
**exactly five XORs**, or **six** when its donor is the sole target. These costs
remain sharp with any number of additional dirty source/helper registers.
Consequently, even knowing the *entire* raw matrix cannot justify projected
cleanup in this enlarged alphabet.

PR1105 / @woklerx already identified the underlying feedback-cleanup problem
and derived its four-block criterion and three-wire census. This contribution
proves the complete range for all dimensions, sharp identity-loop costs, and
adds the full PR589 witness below. It does not challenge the correct semantic-D
substitution theorem of PR1194 or its PR1311 application.

## Concrete witness

Use the selected-at-base PR589 word. Just before A, add this frame-zero loop:

```
222 ^= 111
111 ^= 223
222 ^= 111
111 ^= 223
222 ^= 223
```

Registers 222 and 223 are dirty helpers; 111 is a dirty target. The loop returns
all three exactly, and the original continuation remains correct. Its projected
helper-writing word, however, is the nonidentity `222 ^= 223`.

The scalar projected inverse compiles to the old cleanup followed by that one
helper-to-helper gate at the full frame. This is frame-legal, but now output222
contains input222 **plus input223**. Every source and target output is unchanged,
and testing only clean helpers misses the error. The unchanged owning checker
correctly rejects helper222; no production-verifier defect is claimed.

| Complete word | ADDs | Local / nine-stage scalar envelope bits | Dirty boundary |
|---|---:|---:|---|
| Baseline | 24,305 | 93 / 177 | Pass |
| Identity loop, original cleanup | 24,310 | 94 / 178 | Pass |
| Identity loop, projected cleanup | 24,311 | 94 / 178 | **Fail: helper222** |

All three have identical raw A/scatter/B maps, all 661 frame paths, 2,911
MOVEs, nine COPY/ERASE pairs, paid profile
`{1:1323,2:1342,3:79,4:44,5:102,6:11,7:19}` and rank mass 5,129. Both scalar
104/192-bit guards pass. The invalid variant satisfies raw U/J/K, H2 and H5,
while H1/H3/H4 and the actual inverse-cleanup condition fail. The relaxed rule
under audit permits feedback and a scalar compilation of projected cleanup;
the original literal full-frame H4 is explicitly not satisfied.

## Proof and evidence

[PROOF.md](PROOF.md) supplies the uniform F2-module identities, constructive
factorization, length bounds, sharpness proofs and full source-boundary argument.
The general constructor is not claimed to produce shortest arbitrary words.
The scalar alphabet allows target feedback; its full joint range is not a claim
about words satisfying the original geometric/interface restrictions.

Two separately represented engines—packed binary rows and literal Boolean
permutations—agree on every shortest distance in 4,716 paired states and all
28,248 edges, including 37,680 literal input assignments. The 4,032-state
three-wire case reproduces PR1105 and is credited to it. The constructor also
attains all 12,630 projected matrices with k<=3, 2<=k+q<=5, and 39 larger
fixtures through 64 registers pass independent column replay.

For the selected word, all 661 dirty columns in both directions are checked
for all three variants, including literal COPY/ERASE. The pinned exporter
matches the independent stream opcode by opcode. Original frame/lattice checks
and scalar-bound formulas are retained and source-bound; the bound formulas
are verified against their AST. Finite checks corroborate the written theorem;
they do not replace its all-dimension proof.

## Reproduce

Python 3.12 or later, standard library only, from the repository root:

```sh
python3 -I -B research/projected-cleanup-fibers/verify.py --work /tmp/cleanup-fibers-new
python3 -I -B research/projected-cleanup-fibers/test_package.py
python3 -I -B scripts/research_package.py --package research/projected-cleanup-fibers
```

Use a new output directory. The default registered replay runs the entire
result, with no omitted expensive theorem check. Optimized `-O` is supported;
all new semantic guards are explicit, and the retained exporter is invoked in
an isolated subprocess with assertions enabled. [EXPECTED.json](EXPECTED.json)
binds the complete result. [VALIDATION.md](VALIDATION.md) records environments,
receipts, seven test groups and replay boundaries.

Four runtime inputs have exact Git/SHA256 pins in [SOURCES.json](SOURCES.json).
The selected record/catalogue are historical provenance at base
`bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. No selected record or frozen package is
changed. No native 5/9/11-stage, physical-owner, hosted supplier or outer assembly
replay was run. Scalar envelope inequalities are not a new packed precision
proof. The proof is written, not Lean-checked; no physical supplier or improved
multiplication bound is claimed.

## Task and overlap

One OS draw selected `bit-mechanisms / bit-helper-contract`, nonce
`9092ff22c4d18f77e2b829eaae055120`, scope key `bfb61f829a81535adeae`, priority
revision 2. The required helper-star example reproduced successfully. The
ordinary semantic-D question was already covered by PR1194 and PR1311, so
[TASK.json](TASK.json) explicitly records the change to the adjacent
chronological feedback/cleanup implication. There was no reroll.

[Discussion 1396](https://github.com/CrocSwap/integer-mult-bounds/discussions/1396)
records the claim and result; [OVERLAP.json](OVERLAP.json) records live coverage
and exact compared heads. PR1306 studies minimum complete D compensation words,
not identity loops with prescribed projected effects. PR1256 changes helper
retirement and final frames, which this witness preserves. PR1333 changes the
register operation model for a different paid-call bound.

Submitted as [PR1420](https://github.com/CrocSwap/integer-mult-bounds/pull/1420).
Mathematical implementation commit:
`dc6ba012c92470ea830e3b0ff2dab28fbd8126d8`; the subsequent submission-link commit
changes only this README and TASK metadata.

## Open next questions

* **A frame-aware replacement cleanup contract.** Retain both chronological
  transfers at one feedback cut and require the actual inverse boundary, then
  test a concrete helper-star word. The blocker is a legal physical frame and
  hosting realization; raw endpoint equality or an unchanged paid profile cannot
  substitute for it.
* **The minimum cost of a general projected defect.** The compiler gives an
  explicit linear-in-factor-count upper bound, and this work proves sharpness
  for one elementary defect. Multiple defects may share gates. Start with the
  complete small distance tables and derive a lower invariant before searching
  larger dimensions. No general minimum is claimed here.

## Credit and license

@woklerx: [PR1105](https://github.com/CrocSwap/integer-mult-bounds/pull/1105),
head `20a960b545f4b0ade4f26922ef686bd5eaf275f4`, and
[PR1194](https://github.com/CrocSwap/integer-mult-bounds/pull/1194), head
`2e39c98238f543d988f9efc1b076590a4b780dca`.
Arham Tahir: [PR1311](https://github.com/CrocSwap/integer-mult-bounds/pull/1311), head
`a2875c1834b9c9ef42a84eda4890d5462cc98fa5`, independently checks semantic D on PR1122.
[PR1306](https://github.com/CrocSwap/integer-mult-bounds/pull/1306), head
`0d4c0069f1f4592833304a9ea6e61e676c566113`, supplies the separate feedback-cost census.
Credit eumemic's PR543/555 word and interface, DreamingOfClouds' PR589 tuning,
Zhihao Chen's PR425 predecessor, Dylan Crow's exporter, Sagar Thakrar's PR1062
composition/guard checks, @theon199's PR967 stars, and the original source lineage.
The elementary matrix identities and binary elimination are classical; no
literature-priority claim is made for those tools.

New work by Gareth Davidson (@bitplane), with substantial OpenAI Codex
assistance; Apache-2.0. No subagents or independent human review were used.
