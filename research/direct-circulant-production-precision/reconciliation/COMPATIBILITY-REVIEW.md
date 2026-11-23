# Compatibility review of the reconciled #8093 supplements

**Disposition: accepted.** This is a short integration and preservation
review, not a new mathematical review or a replay of unchanged historical
claims. It supplements the separately frozen interval and selector reviews.
No files in the author's reconciliation checkout were modified.

## Exact integration boundary

Reviewed package:
`/workspace/scratch/e64488edfaad/reconcile-precision/research/direct-circulant-production-precision`.

The final reviewed intervening remote base is
`e040fedfd8fcc51480d2468f3fa07562c8bacbf0`, with tree
`fc5a918a95e2d853afbd99227d6ae17f7b28c129`. The local Git object independently
reports that tree identity. The published `compiler-cuts/` proof remains
`162dd4bb7a020dfb72dd3c80cb9a1de37212cc7f812f36fd4365d487d49b341b`.

An initial check used its parent
`0a1c14499407b103ae964f36551b0e9c11400197` and tree
`691d6a647e64c2b6d2084849fe4d2a7ff0273da6`. The subsequent four-file remote
delta changed only VERIFY output locations, an integration note and elapsed
fields in two receipts. No proof or checker changed. The complete protected
subtree was checked again against the newer actual Git tree.

The separate recovered interval proof is under `compiler-intervals/`,
retaining SHA-256
`e942012e66adc2d696cde3fedd6ae9c73df98e77a71b16e5004f5a74ccdfaa07`.
The sharper selector is under `spectral-downset/`, retaining proof
`0501a6a9a5f467fff4c998606965babc8157e74d98cf33b93f71fb10674d57bb` and
API `9c3e99219f741c5b08c0628c30784cf72c60b4421beae3373fa976aeffcd8e20`.

## Independent preservation checks

I compared the complete `compiler-cuts/` path set, Git blob identities and
disk SHA-256 identities against the actual Git tree at the intervening
commit. All **32 files** agree, including the already published source,
proof, independent review and elapsed-time receipts. This check does not
merely trust the new preservation manifest.

I separately compared the relocated additions against their original
frozen workspace files:

| Relocated subtree | Frozen files matched byte for byte |
| --- | ---: |
| `compiler-intervals/` author package | 23 |
| `compiler-intervals/review/` | 5 |
| `spectral-downset/` author scientific files | 5 |
| `spectral-downset/review/` | 5 |

The original parent README is an exact byte prefix of the reconciled
README. The integration appends the new chronology rather than rewriting
the earlier published account.

## Claim boundaries and dependency binding

The appended parent README and `compiler-intervals/INTEGRATION.md` correctly
identify the earlier complete-gate Result A as overlapping source context.
They identify the additional mathematical claim as Result B: cancellation
along one common legal linearization of nested completed downsets, yielding
`B^2 H^2/(1-theta)<2B^2 H^2` for the interval and its exact inverse.

The source requirements `lambda>=1` and `Q>=1` are stated individually.
The text does not replace them by the weaker product-only condition.
The earlier #5940 conditioned interpolation and #5240 event/partial-write
precedents are credited explicitly. The selector credits #4852 and retains
its spectral-versus-component distinction and unchanged per-P allocation.

The new selector's path adapter and the registered replay both pass
`compiler-intervals` explicitly. The independent selector oracle still pins
the exact e942 interval proof and the original parent proof. It therefore
does not accidentally consume the differently hashed published
`compiler-cuts` proof after the folder reconciliation.

Historical author-stage labels remain inside frozen scientific files.
The new README explains that their separate reviews subsequently accepted
those exact bytes. This preserves provenance without misrepresenting their
current review disposition.

## Registered replay compatibility

The exact seven original verification commands are retained in
`reconciliation/REMOTE-VERIFY.json`, which matches the intervening Git
object. The first three registrations are unchanged. Registrations 3–6
invoke the original source programs and flags, including the two optimized
modes, through disposable copies. The copies prevent regenerated elapsed
fields from rewriting published receipts; their proof-relevant output is
compared after dropping only the top-level `seconds` field.

The newer remote reviewer commands already write outside the package.
The adapter explicitly redirects their `--output` argument into its private
temporary directory and compares that freshly produced receipt. It does
not compare the untouched copied receipt with its own frozen original.
Both updated legacy runs were observed to use and compare the private
`legacy-normal.json` and `legacy-optimized.json` outputs successfully.

An eighth registration runs the added author and independent interval and
selector methods, explicitly selecting the frozen interval dependency.
Both normal and optimized independent modes are present. The replay
authenticates protected files before and after its isolated execution.

I observed the owner's completed registered-replay log, ending in
`PASS_RELATIVE_INTERVAL_AND_SHARP_SELECTOR_ADDITIONS` and
`PASS_REGISTERED_RESEARCH_PACKAGE ... outcome=completed`. I did not count
that owner's execution as a second independent mathematical replay.

Two small nonblocking refinements were sent to the author and applied:
the selector README now describes both independent modes, and all ten
unchanged review files are included in the new authentication inventory.
The inventory covers all 38 frozen additions. The original remote VERIFY
file is itself SHA-256 authenticated. Neither refinement changes a
scientific proof, dependency pin or acceptance result.

Prepared as a separate model-assisted integration check for Jerry Chen /
@CubeJerry. This acceptance is limited to the observed reconciliation;
publication and remote reconciliation remain the parent agent's task.
