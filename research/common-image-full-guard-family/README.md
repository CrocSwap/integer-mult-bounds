# Common-image binary full guards, for any family size

For independent normalized covectors v_i and a nonzero common column u over
F_2, this package counts uniform complete headers that pass every proper
leading principal minor of each corank-one complement I-u v_i. The written
proof covers all m>=2 and 1<=k<=m. With A_j=0 for j<k-1 and otherwise
A_j=2^j product_(r=0)^(k-2)(2^j-2^r), the joint probability is

    sum_j binom(m-1,j) A_j / ((2^m-1) A_(m-1)).

The added result is the k>=3 family law. The k=1 marginal and k=2
transpose-dual of Nick Petalas's PR4807 are prior results. At (m,k)=(7,6),
u=e7 and v_i=e7^T+ei^T give six distinct, noncommuting common-image kernels.
Their joint probability is 22/2667, strictly greater than (729/8128)^6;
each individual marginal remains 729/8128. I7 passes all 36 proper minors.

This takes the shared-direction continuation in [PR6694 question 3](https://github.com/CrocSwap/integer-mult-bounds/pull/6694).
The operator boundary matters: these are full guards on CORANK-ONE complements,
not rank-one first-pivot requests. All six kernels share one line. The narrower
PR6515 interpretation with one coupled pair and four otherwise orthogonal
kernels remains open. This counting result supplies no physical header producer,
paid caller, supplier admission, new kappa or frontier change.

## Evidence

[PROOF.md](PROOF.md) gives transitivity, equal fibers, the binary prefix
equivalence, rank/support count and exact m7 example. [RESULT.json](RESULT.json)
and [ORACLE.json](ORACLE.json) agree on every proof-relevant field: 135 pairs
2<=m<=16,1<=k<=m; complete GL2/GL3/GL4 censuses; exact example and ratio.
The primary uses binomial/full-rank products. The oracle independently uses
column-rank/support DP and literal quotient-span states (374 subspaces at7,6).
Both also implement literal conjugation and every proper determinant for all
20,334 small headers. After independent blind first seals, the oracle compares
all submitted [SMALL-GL.json.gz](SMALL-GL.json.gz) records as data, in normal
and optimized Python. Regeneration compares decompressed canonical values;
gzip container equality is not a mathematical acceptance condition.

Eight authenticated predecessor prose/metadata files stay inert in inputs/.
No predecessor executable or peer code is imported or executed. Neither engine
read the other's results before its first seal. Subsequent data comparison is
explicit. [RUN-RECORDS.json](RUN-RECORDS.json) and [VALIDATION.md](VALIDATION.md)
distinguish direct runs, independent review and later transport checks.

## Reproduce

From the repository root, CPython3.12, standard library only:

```sh
python3.12 -I -W error -B research/common-image-full-guard-family/verify.py
python3.12 -I -W error -B research/common-image-full-guard-family/oracle.py --check-primary research/common-image-full-guard-family/RESULT.json
python3.12 -W error -B scripts/research_package.py --package research/common-image-full-guard-family
```

The registered manifest adds both optimized modes. Direct verifiers need no
Git, network, source checkout, compiler, Lean or Docker; provenance/committed-byte
checks separately require Git history. SMALL-GL is a declared runtime input.
Runtime authentication binds source, cases and schema bytes in both engines.
Receipt checks reject duplicate/nonfinite/float/boolean aliases and compare
actual typed values. The proof-relevant artifact is bounded at8MiB decompressed.
Fixed execution domains include at most65,536 candidate matrices of order4,
135 family rows and a fixed 374-span oracle domain. New functions stay below60
physical lines. Explicit checks remain active under -O. CPython dynamic
allocation, arbitrary-precision integers and bounded recursive JSON-value type
comparison are managed-runtime deviations from fixed allocation/no recursion;
no stronger hard-real-time or formal-verification claim is made.

## Open next questions

Structured copies are in [TASK.json](TASK.json).

1. What is the joint law for exactly one coupled pair plus four orthogonal
   kernels? This isolates the narrower reading of PR6515 Q2. First write a
   normalized partial-Gram fixture and its precise full-guard predicate. The
   current all-six-common-line orbit is different, so its law cannot transfer.
2. Can a named physical caller use this family? Pin its actual header domain
   and producer, then charge selection, emission, dispatch, restoration, stock
   and precision. Those resources and the full caller invoice are unknown.
3. What changes over odd fields or restricted header sets? First characterize
   the new prefix/orbit distribution. Binary vanishing-prefix and uniform-fiber
   assumptions are essential here; no broader sign or applicability claim is made.

## Credit and limits

Nick Petalas supplies the released6694 question and4807 common-covector pair,
4275 binary full-guard context,4227 marginal and4261 partial sums. unpaidmoon
supplies6515's six-orthogonal theorem and nonorthogonal question, with its
Cursor/Grok disclosure retained. Ryanson Jonathan's4607 and the retained4599,
5146, Cinna Davis/source527/commdata2338/Jose Manuel/normalizer/compiler lineage
remain predecessor credit, not newly rerun evidence. See [NOTICE](NOTICE) and
[SOURCE-PINS.json](SOURCE-PINS.json) for exact immutable sources. Classical
rank-one determinants, orbit-stabilizer and finite-field rank counts are used.
Prepared for ToikY with substantial OpenAI Codex assistance and separate AI
primary/oracle/static review. Apache-2.0. Human acceptance, formal kernel
checking, GL7 enumeration, historical spectra, physical caller admission and
selected replay are unclaimed.
