# Encoded setup and ownership of a complete high cube

This package audits the unchanged retained PR2915 `high_route.extents/execute`
boundary. It closes the encoded setup and intermediate-disposal component left
by [PR3233](https://github.com/CrocSwap/integer-mult-bounds/pull/3233), without
assuming that the kernel or native B1 work is free. The source-level invoice
retains both B1 swaps around every reversed-field ADD and the three payload
banks simultaneously live during that operation.

The arithmetic input's physical width and the number of numerical roles are
real costs. For `Q>1`, high-bank initialization, preparation, loading, Ring
creation and teardown cost exactly `10K + 65 bit_length(Q) + 159` physical reads, writes and
unit moves. Here `K` counts numerical roles, not bits of word capacity.
The caller's default and the replay fixture can have different `K`.

## Contract and invoice

Let `d` be the matrix dimension, `Q` the positive high-field modulus, `F` the
positive canonical fibre count, `H=Q^(d*d)` and `V=H*F`. Write
`L=bit_length(Q)` and let `I` be the common physical width of the context's
numerical words. The source contains exactly one dense `V`-bit cube. Source
and borrowed counts begin at their canonical origins. The route comes from
the retained compiler, so every high-field index is in range and paired
indices are distinct. The initialized pool has enough free roles; the high
bank enters erased and empty, as established by `stage.Adapter`.
Every charged kernel or adapter call must preserve its borrowed input and
restore that head, returning a distinct dense `V`-bit output at its origin.
The invoice is conditional on these callee contracts; finite fixtures do not
establish their all-width correctness.

This is a successful-execution contract. Resource exhaustion during setup
is not claimed to be exception safe. Entry context construction, permanent
pool/marker provisioning and enclosing-caller residents remain separate.

Let `R(H,F)` be the source-derived `copy_rows` invoice in [PROOF.md](PROOF.md).
The entry copy, modulus Count construction and disposal, context comparison
and source rewinds cost exactly

```text
R(H,F) + 4V + 27I + L + 61.
```

On the active high-field branch, add the bank bill above, every encoded
extent-construction/closure bill, and `5V+7` for each disposed intermediate.
Each operation disposes its old input; a reversed ADD disposes two additional
intermediates inside `apply`. Every kernel call and every complete
`adapter.swap` call is charged at its actual entry/exit boundary. In
particular, the complete adapter toll includes its encoded setup, native call,
copy-out, cleanup and Count disposal. Closing the final returned output adds
another `5V+7`.

For `Q=1`, the caller copies the source and skips all high operations and
bank initialization. For `Q>1`, the source argument covers arbitrary valid
compiled operation sequences. The exact extent recurrences and the complete
partition proof are in [PROOF.md](PROOF.md); they do not extrapolate a constant
from small fixtures. The actual Ring requires exactly one high zero margin;
arbitrary extra padding is not a valid source-context construction. With an
outer modulus `q^w`, its source relation is `I=bit_length(q^w)+1` and
`Q=q^(w-1)`. Keep that relation or the observed `I` explicit in composition.

There is also a deliberately loose uniform bound on this surrounding work.
Put `N=d*d`, `J=2 bit_length(N)`, and let `s` count executed factors. The
source-derived setup and disposal cost, excluding the separately paid kernel
and complete adapter calls, is at most

```text
27I + 10K + [373 + s*(3*(716 + 933J) + 36)]*V.
```

The proof bounds each canonical encoded extent bill by
`(716+933J)*bit_length(V)^2` and uses `bit_length(V)^2 <= 3V`.
It does not claim that the displayed constant is sharp, or remove the
explicit `I,K` terms by assuming the fixture's sizes. For fixed `q,d,K`, the
stated outer-modulus relation makes this a linear-volume bound for the proved
surrounding work; it still leaves the data-call tolls charged separately.

## Ownership boundary

During an ordinary operation, the route owns its current input and the newly
returned output. During reversed ADD, the old input remains live while the
first swapped output and ADD output coexist; the same occurs when swapping
the ADD output back. Thus three route-level payload banks are necessary at
these cuts. This excludes the externally borrowed original source, internal
kernel/native scratch and other enclosing residents. After success, only
the returned output remains owned by this route, and the high bank is erased.
This is not a total allocator/backing or whole-stage stock bound.

## Reproduce and limits

Ten unchanged-source fixtures cover all six compiled operation kinds, the
inactive `Q=1` branch, different fibres and radices, and an empty active route.
The raw Tape meters and the separate observer agree on every complete bill.
For the 81-bit fixtures:

| Compiled route | Total physical traffic | Setup and disposal outside data calls | Caller-owned payload peak |
| --- | ---: | ---: | ---: |
| Ordered ADD word (two factors) | 59,701 | 8,951 | 2 |
| Reversed ADD word (two factors, four native swaps) | 175,505 | 10,599 | 3 |
| Mixed word | 431,027 | 42,889 | 3 |

All native fixtures use the elementary B1 branch. The complete receipt is
[RESULT.json](RESULT.json). Seven behavioral control groups pass normally and
with `-I -O -Werror` on CPython 3.12.15; the complete registered replay passes.
On the active branch, one extra numerical role adds exactly 10 operations.
Legal radix-3/radix-5 width-one contexts have the same `Q=V=1`
but differ by one input digit and exactly 27 operations. Extra physical traffic,
missing bank erasure and changed source bytes are rejected. A one-hot payload
distinguishes an omitted first swap; a periodic payload would miss that fault.

From the repository root, using standard-library Python 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/high-route-setup-invoice
```

[SOURCES.json](SOURCES.json) pins the unchanged implementation and its complete
activated input closure. The replay reuses the authenticated observer/fixture
support from `high-route-prefix-cost/runtime.py`, substituting only its source
authentication callback with this package's checked input map. It does not
replay that predecessor's broad manifest or modify the executed caller.
The selected record is an input because the retained loader actually reads it.

The currency is physical reads, writes and unit moves. It excludes host
bookkeeping and finite-control allocator selection; this is not a complete
machine-step constant. Native B1 and kernel tariffs remain explicitly charged
dependencies. No selected cold replay, all-width native admission, whole-stage
stock coefficient, independent human/formal review, new kappa or complete
multiplication theorem is claimed. The selected frontier is unchanged.

## Open next questions

Can the paid kernel and native B1 components be composed into a uniform
single-cube bill? Begin with the existing ordered ADD, scaling and prefix
invoices on the same source domain; retain both reversed-ADD swaps and every
intermediate. The native contracts and any remaining component tariffs must
be discharged before claiming the complete bill.

What reserve does the actual selected caller require? Map these chronological
ownership cuts to physical backing and the enclosing recursive lifetime,
including entry residents and marker provisioning. A local traffic formula
or count of route-level payload banks does not determine a stage coefficient.

## Sources, coordination and credit

The released handoff is [Discussion2319 comment19002824](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-19002824).
[This investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-19003396)
tracks the scoped claim and final artifact. Base canonical main/fork is
`463113d675af7410ac91d53a4fed51ec6494eb9a`, priority revision 6.
[TASK.json](TASK.json) retains the original stock card, changed scope and
overlap evidence. The adjacent PR3246-to-PR2899 stock-selector composition
remains with its owner.

Jose Manuel (`jmbarrancoml`) supplied PR2915's reached caller and PR2899/2809
dependencies; David Arias supplied PR2753's logical caller. Nick Petalas's
PR2982 supplies the outer prefix invoice and released composition question;
PR2951/2968 supply scaling invoices. commdata2338's PR3233 supplies the ordered
ADD scratch and physical-I/O bill. Arham Tahir's PR2877 countdown identity,
ywz65's PR2473 audit, Ross Richardson's PR2810 numerical bound and the retained
PR2157/PR589/source lineage retain credit. Those component results are not
claimed as new here.

Prepared by thakrarsagar with substantial OpenAI Codex assistance in derivation,
implementation, independently derived proof, controls and review. Separate AI
executions are not independent human review. Apache-2.0.
