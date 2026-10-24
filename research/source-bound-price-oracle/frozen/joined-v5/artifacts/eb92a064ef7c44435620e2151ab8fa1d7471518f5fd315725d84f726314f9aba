# Conservative leaf-inclusive error count

This addendum supersedes only REPORT.md section5's sufficient error-site count
and the corresponding `approximation.error_site_log_bound` in CLOSURE-v1.json.
The exact frozen v1 files remain unchanged. No candidate physical word,
invoice, compiler endpoint or selected premise changes.

To include every direct leaf kernel as a hypothetical error site, in addition
to the finite-template scalar/child sites, use the still more conservative

```
J(e) <= (G+N+1)*e*(P+1)^(D+1),  D<=log2(e),  e>=1.
log2 J(e) <= (G+N+2*P+4)*e.
```

Indeed there are at most `(P+1)^(D+1)` stopped-tree nodes, at most G scalar/
native record sites per nonleaf and at most e direct one-axis kernel sites
at any leaf. The displayed product overcounts both. Integer log2 bounds give
`log2(G+N+1)<=G+N+1`, `log2(e)<=e`, and
`(D+1)log2(P+1)<=(e+1)(P+1)<=2(P+1)e`; summing proves the bound.
Exact movement/descriptor arithmetic introduces no roundoff, but the
overcount remains valid if those record sites are included as well.

With new S=Z+N+P+G+1, E=64S^3 and B=P+E, we have N<E, G<E, P<B. Hence

`4B+36+G+N+2P+4 < 8B+40 < 32*N*B^2 = C0`

for N>=2 and B>=64. The same allocated per-site error target
`2^(-p-C0*d)` and changed-word prefix/suffix bound therefore still imply
total output error at most `2^-p`. The explicit N and e factors remove any
need to rely on leaf kernels being exact when counting hypothetical error
injections. The selected source's exact fine-grid/no child re-encoding ABI
is separately retained; no residual-zero or independent-error cancellation
assumption is made in either version.

The remaining new thresholds, stock product, ownership and complete source
applicability proof are unchanged. This uniform inequality is valid for both
the independently reviewed #5383 and the separately bound #5387 template,
using each template's own N/P/G/B/C0 and all its new banks.

Review by Chris R / Clear1nsight with substantial OpenAI Codex assistance.
Ali Romman, Dugongue and all attributed predecessors retain their credit.
