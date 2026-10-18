# Gaussian E8: independent replay and a stronger certificate ceiling

**Extension:** nonnegative weighting of any inclusion-maximal
nonorthogonality cliques in the 60-line Gaussian E8 geometry cannot prove a
copy floor above **40 Gaussian units**. This includes nonuniform weights and
mixtures of maximal cliques of different sizes. Uniform weighting of the
640 maximum cliques attains 40, so the method optimum is exactly 40.

The matching copy lower bound was independently reported in **Sagar Thakrar /
@thakrarsagar's [PR #738](https://github.com/CrocSwap/integer-mult-bounds/pull/738)**,
discovered during the final overlap refresh after this package's proof and
code were developed. We claim an independent replay and the broader method
ceiling, not a new discovery of its floor. At the inspected #738 head, its
sharpness proof covers uniform maximum-clique weights; its bound for general
nonuniform clique weights is 48. Our extension reduces that ceiling to 40
for inclusion-maximal cliques. Non-maximal-clique certificates remain outside
this extension.

Two complete replays confirm **40 Gaussian units = 80 rational units** for
every fitting binary scalar-total decoder, with asymmetric reader/source
sets and arbitrarily many totals. Every fitting matrix has a charge-60 row
decomposition, leaving its optimum in **[40,60]**. The replays cover 2,582,128
unordered pairs of the 2,272 root-span flats. The difference from #738's
nonempty-pair count is only inclusion of empty-support pairs, not a stronger
mathematical domain. Method optimality does not construct a charge-40 decoder.

**No new kappa or physical supplier is claimed.** The normalized floor 2/3
does not reach the predecessor's approximate 0.71 comparison threshold.
The mathematical model, unresolved interval and conditional accounting are
specified in [PROOF.md](PROOF.md).

## Reproduce

From the repository root, use Python 3.11 or later with only its standard
library. This command runs both complete replays in separate processes and
stops if either fails:

```sh
python -I -B -c "import subprocess, sys; base='research/gaussian-e8-copy-bound/'; [subprocess.run([sys.executable, '-I', '-B', base + name], check=True) for name in ('verify.py', 'independent_check.py')]"
```

Expected output:

```text
PASS_GAUSSIAN_E8_COPY_BOUND lower=40 upper=60 flats=2272 pairs=2582128 controls=8
PASS_INDEPENDENT_GAUSSIAN_COPY_BOUND lower=40 pairs=2582128 maximal_cliques=8704 controls=10
```

Both replays check pinned source bytes and compare their freshly computed
receipts with the committed receipts. The first computes exact pairing ranks
in eight rational coordinates. The second uses four Gaussian-integer
coordinates, independent flat enumeration and exact rank certificates. Both
run their rejection controls by default. They need no network, solver,
third-party dependency or predecessor-code import. Their checks remain
active with Python's optional `-O` flag.

## Review map

- [PROOF.md](PROOF.md): model, closure reduction, lower bound, upper bound and
  proof-method ceiling.
- [RESULTS.json](RESULTS.json) and [INDEPENDENT.json](INDEPENDENT.json):
  deterministic receipts from [verify.py](verify.py) and
  [independent_check.py](independent_check.py).
- [SOURCES.json](SOURCES.json): SHA-256 source pins; exact repository base
  `66849e1475c930fd7732b1a0067ffee7e1e95f60` and inspected #703 head
  `358383e2f1b0f292d4d6eb897c06fd8558a4f5e6`.
- Concurrent [#738 proof](https://github.com/CrocSwap/integer-mult-bounds/blob/9671c5d72f3119ba26f3774f40aa7130c67bcf77/research/gaussian-clique-copy-bound/PROOF.md):
  overlap comparison at `9671c5d72f3119ba26f3774f40aa7130c67bcf77`.
- [CLAIM.md](CLAIM.md): seed-6 sprint scope and overlap check.
- [VALIDATION.md](VALIDATION.md): actual replay environment, rejection checks
  and verification limits.
- [NOTICE.md](NOTICE.md): predecessor attribution, AI assistance and license.

The result concerns this fixed geometry, binary scalar totals, its fitting
pattern and the stated pairing-rank charge. Vector-valued totals, rational
sub-line supports, different geometries or supplier formats are outside
scope. The written argument extends the finite certificate to arbitrarily
many totals. It is not a proof-assistant formalization, a full multiplication
proof or an independent human review.
