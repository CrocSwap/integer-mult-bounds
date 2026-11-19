# One singular paid omission and one helper surrender

On the published `bd3d` rational word, every strictly cheaper original helper chart pair fails a necessary rank condition after a single singular paid omission. The checker excludes all **53,438** combinations of a singular paid row and a lower-grade helper chart pair. The roster includes all 88 distinct chart pairs occupied by the 884 declared helpers. It permits independent choices of the surrendered direction at each end, together with invertible ordinary basis changes within every public chart.

| Missing support | Paid row and helper chart pair combinations |
| --- | ---: |
| Input kernel and output cokernel | 10,359 |
| Input kernel only | 24,152 |
| Output cokernel only | 18,927 |

The scope fixes one paid deletion, the remaining paid rows, all 400 main owners, and the original helper chart pair for the one surrender. It uses the published 48-call rational caller at the target κ of `0.00387981257853`. The original rational shortfall is 4.283801810418420331023466–4.283801810418420331023467 signed units. [Expected evidence](EXPECTED.json) · [Published price receipt](../independent-price.json)

## Exact rank test

Let \(M\) be the invertible public map, \(f\) the old producer form of the omitted row, and \(v\) the public response to a unit impulse on that row. Chronological propagation gives the cut map \(N=M-vf\). Set \(u=M^{-1}v\) and \(g=fM^{-1}\). The checker obtains both exact contractions \(fu\) and \(gv\) and requires them to agree. A singular deletion has \(fu=1\), so \(N=M(I-uf)\) has rank 1,283, kernel spanned by \(u\), and image equal to the hyperplane \(\ker g\).

For a surrendered helper at input chart \(A\) and output chart \(B\), retain an input hyperplane \(\ker n\) with normal \(n\) supported at \(A\). Quotient the output by a line spanned by \(y\) supported at \(B\). The restriction can be injective only if \(n(u)\ne0\). In that case its image is all of \(\ker g\), so the output quotient is injective on that image only if \(g(y)\ne0\). These tests require some coordinate of \(u\) at \(A\) and some coordinate of \(g\) at \(B\). A chart-local invertible coordinate change preserves whether either chart component is zero. Granting arbitrary independent \(n,y\) includes the more constrained choices that join the two ends of one helper direction and preserve the main owners.

The checker reconstructs the literal forward and adjoint operators on 1,284 owners, verifies every column of the inverse, and checks strictly nested geometry for every paid transfer and every helper return. It finds 5,652 singular deletions and 59 regular deletions. For each singular paid row, bit sets on the old helper chart pairs count the missing kernel and cokernel supports. A single lower-grade chart pair passing both supports would fail the replay.

## Tariff and passing control

For a removed paid grade \(r\) and a surrendered productive grade \(h\), the signed gain across 48 calls is \(48(r^{1-\kappa}-h^{1-\kappa})\). At the fixed target it can be positive only for \(h<r\). Directed interval arithmetic over all integer grades up to nine gives a conservative lower bound above **47.4185** for any positive difference on that grid. The largest actual paid grade is eight. The checker reconstructs the complete price from the literal native rank histograms and the pinned fixed-caller histograms. With every price-positive slot and chart pair excluded, the saving in this family is at most zero.

The incidence test accepts equal-price cases. The checker deletes paid slot 0 and suppresses helper 1260 on charts \((243,1101)\). Both grades are three. The identity \(\operatorname{adj}(N)=\det(M)\,u g\) gives the corresponding principal minor a determinant ratio of one relative to the uncut reference. Direct tape evaluation recovers every retained public coefficient. Keeping helper 1260 on the same cut tape leaves a nonzero kernel. The two controls distinguish successful rank recovery from a paid improvement.

## Reproduce

From the checkout containing this checker, create a detached checkout of the immutable input and prepare the public source cache with Python 3.12.

```sh
checkpoint="$(mktemp -d)"
git worktree add --detach "$checkpoint" 172475c2ca321d3496fda7a2a71478ada5acb948
cache="$(mktemp -d)"
python3 -IB "$checkpoint/research/p104-iterated-returns/prepare_sources.py" "$cache" --fetch
python3 -IB research/p104-iterated-returns/evidence/helper-minor/check.py \
  --cache "$cache" --checkpoint "$checkpoint"
```

An existing cache verified by `prepare_sources.py` can be reused offline. Omit `--checkpoint` if the package containing this checker already contains the pinned `bd3d` word, layout and price inputs. The checker verifies its two imported source files by SHA-256 before loading them, binds the published word and layout by canonical payload hash, and authenticates the two existing application and price receipts by their file hashes. It compares the entire deterministic result with `EXPECTED.json`. An optional `--out` writes the reproduced receipt. [Source lock](../../SOURCE-LOCK.json) · [Application receipt at the pinned head](https://github.com/CrocSwap/integer-mult-bounds/blob/172475c2ca321d3496fda7a2a71478ada5acb948/research/p104-iterated-returns/evidence/application.json)

## Open next questions

Can a changed paid word or a simultaneous multi-row deletion change which helper charts meet both support conditions? A first check is to derive the new kernel and cokernel on the exact edited tape and compare their chart supports before pricing all newly deleted legs and surrendered targets. Such a change requires a fresh operator and invoice replay.

## Credit

Clear1nsight prepared the helper-minor screen and independent replay with substantial OpenAI Codex assistance. The exact rational replay interface is from Clear1nsight's #7781, and the tested word is the published #7786 successor. The supplier operations and fixed rational caller derive from Ali Romman's #7776. The directed interval implementation is pinned from the inherited paired-query package. Its source attribution and the inherited caller, compiler and proof credits are retained in the package notice. [Notice](../../NOTICE) · [#7781](https://github.com/CrocSwap/integer-mult-bounds/pull/7781) · [#7776](https://github.com/CrocSwap/integer-mult-bounds/pull/7776)
