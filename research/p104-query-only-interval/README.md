# An E-free caller using only existing operations

Prepared for **@CubeJerry**, with substantial OpenAI assistance. Apache-2.0.
**No new kappa. No unconditional multiplication theorem.**

This package removes both QSELF operations from DreamingOfClouds'
[#6937](https://github.com/CrocSwap/integer-mult-bounds/pull/6937) E-free caller
without increasing its paid-query profile. The exact source interval 457..575
contains two separated QSELF(-1) events and one QUERY(-1). Its replacement
uses three QUERY(-1) events and existing ADD, SWAP and LAMBDA operations,
with no additional public/helper field, initialized scratch role, productive
credit or operation type. The whole caller has 3,095 events and zero QSELFs.

The construction applies to all independent inputs, with all 18 D variables
formal, under commuting Q,D and Q^4=I. It includes the full intervening source
operations, not only a same-cut pair gadget. Its basis changes use the source
phase unit lambda_+=((1+i)+(1-i)q^2)/2; no projection is inverted. The D9
operation is moved only across disjoint supports and is never inverted.

## Result and complete budget

The generated [complete caller](QUERY-ONLY-CALLER.json), exact
[interval patch](PATCH.json) and [proof](PROOF.md) are reproducible from the
pinned source. The full target and paid profiles remain identical at every
rank, hence their entire signed moment polynomial is unchanged. Totals remain
23,050 productive targets, 117,846 paid jobs, surplus 1,520 and paid rank
mass 317,324. The accepted selected certificate is untouched.

The replacement adds 104 A events and 28 A LAMBDA events while replacing 192
physical QSELF instances with 192 QUERY instances. All 416 outer jobs now use
the existing QUERY contract. The complete inherited ordinary invoice, including
the separate LAMBDA and 1125 conversion readings, is 826,265,904, with margin
173,734,096 below its 10^9 cap. These scalar/routing rates remain conditional;
they are not a new physical bit-tape or rounded precision certificate.

## Evidence and reproduction

The new interval checker compares exact 38-input matrices with unrestricted
formal D monomials, retaining repeated powers. The complete 76-input caller
also passes the unchanged public forward certificate and a separate backward
covector certificate with all D variables formal. Four exact q characters
together are faithful for the stated quotient. Eight new algebra controls
and a fourth-query paid-budget control detect incorrect modifications.

From the repository root:

```sh
python3 -B scripts/research_package.py --package research/p104-query-only-interval --check-only
python3 -B scripts/research_package.py --package research/p104-query-only-interval
```

The registered runner executes four bounded suites in normal and optimized
Python. A Git-free source export can directly run:

```sh
python3 -I -B research/p104-query-only-interval/verify.py --suite interval
python3 -I -B research/p104-query-only-interval/verify.py --suite formal
python3 -I -B research/p104-query-only-interval/verify.py --suite invoice
python3 -I -B research/p104-query-only-interval/verify.py --suite controls
```

`DEPENDENCIES.json` authenticates nine targeted unchanged input files by
SHA256 and Git blob. External fork commit objects need not be present in a
shallow checkout: runtime authentication uses the vendored bytes, while
canonical task and selected-state provenance are separately pinned in
`SOURCES.json`. Regeneration is explicit with `verify.py --regenerate`.

## Scope, novelty and credit

DreamingOfClouds owns the E-free root/caller and its earlier QUERY-only
feasibility observation in #6937, as well as the unchanged local native source
in [#6936](https://github.com/CrocSwap/integer-mult-bounds/pull/6936).
Its source README says the whole QUERY-only caller was not built and describes
a projected loss. This package instead supplies a complete actual interval
replacement preserving the paid profile, and emits and checks the whole caller.

The preceding public [owned QSELF package](https://github.com/CubeJerry/integer-mult-bounds/tree/4e2fd1b6abed49c202a057fd5c73ead0a460f976/research/p104-qself-owned-lowering)
supplies the exact source semantics, formal forward/backward engines and
invoice baseline reused unchanged here. Its paired-synthesis question remains
distinct from its single-QSELF determinant obstruction. Source inspection was
bounded to those exact predecessors and the lead's current #6936/#6937 refresh;
no exhaustive novelty search or universal query lower bound is claimed.

The three-query four-input identity, actual separated-source reduction,
generator and new interval certificate were prepared for @CubeJerry with
substantial OpenAI assistance. See [review notes](REVIEW.md) for the exact
cross-check scope. AI/code-assisted review is not human or proof-kernel review.

## Open next questions

The [proof](PROOF.md#open-next-questions) and `TASK.json` identify the remaining
source/compiler, common-format, signed-headroom, rounded-error, bit-tape and
historical-backing obligations. Existing opcodes do not automatically install
new source-specific provider records. The five selected foundational assumptions
remain; this exact source substitution removes one proposed new-op obligation.
