# Fast dense execution of the original paired P104 collector

I construct exact dense Gaussian monomial wrappers and retain the original
consecutive-order integer lifting map. For the first paired P104 collector,
at n=9lambda, N=2^n and linear working precision, I derive

    time: O(N lambda^(2-8003/6000000)),
    additional clean space: O(N lambda^(5991997/3000000))+F.

I include both native calls, four wrapper executions, source/query access,
grid handling and cleanup. The five dirty sources remain unchanged and
the private collector returns to literal zero. The query matches the
credited paired floor program at the same working grid.

I retain PR2287/3109's exact C-layer and physical/compiler premises. This
is a conditional standalone collector result, not a new multiplication
exponent or full P104 supplier. I charge the clean histories and do not
claim linear space or free dirty-workspace hosting.

## Two interface changes

First, I use the credited scalar-period identity at residue zero:
`L(2^g q)=2^g Uq`. On a sufficient power-of-two input scale, the fast
changed-order lift from PR3109 is an exact dense linear backend.
The standard character-conjugation word then gives exact whole-field
CNOTs and toggles, with exact output shifts and literal inverse cleanup.
No rounding recovery or uncharged address permutation enters this step.
I compile the actual fixed nine-field wrapper matrices into those gates.

Second, I use that exact backend inside a second, consecutive residue
partition. This preserves the original nonlinear word while bounding the
short-group and narrow-residue costs together. I choose outer exponent
`5991997/6000000`; the resulting saving is `8003/6000000` relative to the
quadratic scalar-reference rank factor. [PROOF.md](PROOF.md) gives the
uniform domain, complete ledger and error/cleanup arguments.

The physical interface uses field-major addresses
`index=sum_i v_i*2^(i*lambda)`. A caller requiring copy-major layout must
pay for that conversion. The construction applies to Gaussian payloads
with O(lambda) working component widths; it is not a faster width-one
Boolean interchange.

## Evidence and reproduction

From the repository root, use Python 3.12:

```sh
python3.12 scripts/research_package.py --package research/dense-paired-collector
```

I bind PR2586's fifteen collector events and both native occurrences. I
check 512 ideal round-trip columns, all four affine recipe maps, 2,610
offset interval plans, guarded dense address gates and original-order
lifting through 257-bit inputs. Four complete N=512 collector fixtures
match Tekalign's predecessor on query, grid and private return, including
70-bit dirty cancellation and a zero sum. Synthetic tensor wrappers cover
multiplicities one through three.

The finite model uses the frozen PR3109 direct semantic oracle. Its macro
counts do not measure fast physical time or certify a transition trace.
The all-size bound is a written construction under the named source
premises. `RESULT.json` pins complete typed receipts; the registered
commands include optimized execution.

## Scope, credit and stopping decision

I credit Tekalign's PR3025/3033 pair, adaptive grid, scalar-period identity
and paired collector; Ross Richardson's PR3072 residue-block construction;
Douglas Colkitt's direct-selected-XOR conjugation and earlier pricing
analysis; the PR2250 binary affine compiler; and the PR2287/2899/3109
selected-layer and physical-bit lineage. [SOURCES.json](SOURCES.json)
records exact pins and the retained source notices.

I preserve Vasek/flyingviper's frozen-consumer audit, following the earlier
Discussion2619 calculation. Its unmodified five-forward/four-dual bill is
at least599/584 even at zero saving. This execution result changes neither
that paid profile nor its coverage. Clean history is not a productive
family and does not enlarge the moment denominator.

Tekalign's concurrent [PR3122](https://github.com/CrocSwap/integer-mult-bounds/pull/3122)
reduces history storage for the unchanged PR3109 core. Its author leaves
native wrappers and collector integration open. I retain the conservative
space bound above; I neither import that implementation nor claim a minimum
collector-space exponent.

## Open next questions

- Find a changed complete P104 profile, coverage law or consumer that can
  afford the correction. First price its full bill against the inherited
  rejection; a faster implementation of this one collector does not
  remove its existing rank charges.
- Reduce the collector's clean history while retaining a useful time
  bound. First choose a named routine and price snapshots, recomputation,
  access and cleanup. An enclosing caller must use the resulting reserve,
  rather than reuse a linear-space allowance without proof.

I coordinated the work in
[2750#18986640](https://github.com/CrocSwap/integer-mult-bounds/discussions/2750#discussioncomment-18986640).
Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance,
including analysis subagents. Apache-2.0. I claim no independent human,
proof-assistant or full-supplier verification.
