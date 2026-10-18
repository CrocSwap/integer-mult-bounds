# Admit triadic ADDRESS queries on the excluded odd moduli

**Exact local compiler tariff and constructive extension; no new kappa.**
[PR2593](https://github.com/CrocSwap/integer-mult-bounds/pull/2593) correctly
excludes moduli divisible by3 from its one-child lowering. This package supplies
that missing branch and proves the exact minimum number of its designated
interchange children, for every odd modulus m and integer power k:

| Residue k modulo m | Minimum CHILD_C(0,5) calls | Literal affine events |
| --- | ---: | ---: |
| Zero | 0 | 0 |
| Unit | 1 | 6 |
| Nonzero nonunit | 2 | 12 |

The alphabet consists of invertible ordered affine ADDRESS maps and the fixed
swap of fields0 and5. No other ADDRESS permutation or reordered field access is
free. Affine event counts are constructive upper bounds; only child counts are
optimal. [PROOF.md](PROOF.md) gives the all-size argument: a one-child word has
a unit top-right coefficient, while every residue over an odd modulus is the
sum of two units. The elementary triangular invariant and CRT are standard;
the contribution is their exact source-interface application and attaining
compiler, including the excluded composite-ring endpoint.

For k=+/-3*2^j, the nonunit branch uses the unchanged source words for
`+/-2^j` and `+/-2^(j+1)`. Their complete six-field maps compose to M(k).
This fixed dyadic split works on every odd modulus. At m=3 the query is
identity. On other multiples of3 the completed PR2593 pair has a literal
bill of **6 children,36 affine events,2 XOR scans**, versus8/48/4 for the
separate pair using the same adapter. Coprime moduli retain3/18/2. The
whole DATA shear at m=3 is identity and is omitted entirely.

The source DATA row and all arbitrary dirty spectators are preserved. The
target requires exclusive access until the completed boundary. There is no
clean or disposable full row. **The full fused-program optimum is not proved.**
Routing, coefficients, tape preparation, temporary storage, child workspace
and head returns remain separately charged in the typed bill in PROOF.md.
Growing j and the generic finite unit-split search do not have a claimed
uniform fast preparation bound. No selected supplier, physical runtime saving,
precision theorem or multiplication-theorem admission follows.

## Exact sources and evidence

Final base main is `b4560d9e7216f72b73c5aa940ac099c05e33ccf9` (guidance revision5).
The round began at revision4; the final refresh changed guidance only, and the
scientific input bytes are identical. The new family expansion gate was read.
[SOURCES.json](SOURCES.json) pins retained PR840 inputs. [VENDOR.json](VENDOR.json)
pins the byte-identical PR2593 program/proof/README/notice at public head
`77041f2d139276115ffa32ab876455d3a58ef2cb`. SHA256 and Git blob identities are
checked before predecessor code executes. Neither predecessor is edited.

[RESULT.json](RESULT.json) is rebuilt read-only by the primary checker:

* 5,250 classifications over all odd m=3..101 and every k=-m..m, with42,000
  complete active/spectator matrix columns and inverse checks;
* 110 signed triadic cases, including j=54 and composite rings;
* every address of `(Z/9)^6` for all four signed forward/inverse powers
  (-6,-3,3,6):2,125,764 ADDRESS-column checks, followed by every dirty DATA
  target/source/spectator column of the completed pair and its inverse;
* the original nonunit word's rejection and ten effective semantic/domain
  controls, plus a literal dirty BIT-row forward/inverse execution.

The separate [independent.py](independent.py) imports no new producer or
predecessor compiler. It rebuilds1,074 complete integer operators and their
inverses and exhausts111,520 small triangular double-coset pairs. Its enlarged
free-alphabet control demonstrates why an unordered free shear is outside the
theorem. [integrity.py](integrity.py) performs two Git-free optimized replays,
checks read-only execution and rejects seven source/CLI corruptions.

These finite checks validate implementation and source orientation. The written
proof, not extrapolation from the tests, establishes the all-modulus theorem.

## Reproduce

Standard-library Python3.12, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/triadic-nonunit-lowering
python3.12 -I -O -B research/triadic-nonunit-lowering/verify.py
python3.12 -I -O -B research/triadic-nonunit-lowering/independent.py
```

Expected markers: `PASS_TRIADIC_NONUNIT_LOWERING`,
`PASS_INDEPENDENT_NONUNIT_LOWERING`, `PASS_TRIADIC_NONUNIT_INTEGRITY`, and
`PASS_REGISTERED_RESEARCH_PACKAGE`. Primary `--write` creates a receipt only
when none exists and refuses overwrite. No network or Git is required for a
source export with the declared inputs; the registered wrapper additionally
checks historical Git provenance.

## Overlap and credit

PR840 supplies the exact dyadic word, completed pair and query lower bound;
PR2593 supplies the triadic specialization and explicit excluded-prime boundary.
We do not claim a new fusion identity or rediscover a bug in either source.
This result adds a different native lowering branch and proves its local
optimum. The full cached overlap covered815 open PRs and1,277 Discussion
records; a subsequent100-recent-PR scan and exact source-head check found no
competing nonunit-power lowering. [OVERLAP.json](OVERLAP.json) records coverage
and limitations; it is not a novelty certificate.

The declared milestone is a **local module**, with the decision **narrow and
stop at this handoff**. Local child counts are proved; literal affine/XOR
counts and the typed composed bill are constructive upper bounds. Complete
consumer embedding, preparation/routing/hosting costs, precision and a
favorable supplier allowance are unknown. Further dependent optimization is
not justified until a named consumer and complete allowance make the missing
module useful. This package closes the explicit arithmetic-admission boundary;
it does not claim that a downstream consumer will realize a net saving.

Prepared by ywz65 with substantial OpenAI Codex assistance in proof, code,
tests and writing, including separate AI review; no independent human or
proof-assistant review is claimed. Credit Wentao Li / VictorLiwentao for
PR840/PR2593, Karl Appel / applecrusher for PR521, commdata2338 for PR677,
and the retained OpenAI tape framework. New material is Apache-2.0; vendored
source notices and bytes are retained.

## Open next questions

1. Can a complete DATA program share child work across the local query
   boundaries on multiples of3? First specify its full dirty endpoint and
   allowed intermediate observations, then synthesize and charge the entire
   word. The local2-child floor alone does not give a6-child global floor.
2. Can this all-odd-modulus endpoint be embedded in an admitted BIT supplier?
   First bind common labels, exact source return and the real child domains,
   then charge routing, coefficient streams, tape, precision and dispatch.
   Neither a compiler embedding nor a favorable full supplier bill is supplied.
