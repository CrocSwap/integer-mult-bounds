# Publication and scope of the exact native output-grid interface

This sibling package extends the numerical proof chain in #8093. It adds no
files inside `research/direct-circulant-production-precision`; every previously
committed file remains byte-identical. The scientific author files are frozen
by `FROZEN.json`, whose original pending-review status records the author-stage
snapshot. The completed independent decision is `review/CROSS-REVIEW.md`.

The exact parent is `8559a122f55614163c037b3c20a21f449a0531f6`; canonical main
and the selected certificate are pinned at
`e54523517d0f03e58352e647c403a5af3e525a57`. The latter still selects
`kappa = 0.00363005817` and explicitly retains all five framework assumptions.
This package claims **no new kappa** and no complete assumption discharge.

## Precise new implication

For a complete P-grid array within radius `2^E`, the actual raw h-bit Hadamard
call is reproduced exactly using the retained normalized native contract with
`R=E+1` and requested output grid `Q=P+R+h`. The entrance integer left shift
is h bits; the returned integer numerators are used directly on the P-grid.
Final truncation is transparent. A signed basis witness loses its output at
`Q-1`, for this fixed scaling and return contract.

The proof includes the source's absolute C/S/b phases, spectators, dirty padded
holes, actual address strides, and the completed-endpoint divisibility/parity
needed for terminal normalization. Conditional on the retained C-interior
common-grid premise, the temporary width is `P+E+3h+31`. Production parameters
give `Q<=4807p` and temporary width `<=4839p`, with a logarithmic parameter
increase at most 13. Actual direct-circulant geometry gives eventual scale
compatibility; the source's unspecified reservoir constants remain inherited.

This removes a format/truncation implication from the outstanding native
adapter obligation. It does not implement a native supplier, prove its stock
or geometry admission, join all historical arena backing, or price its full
tape movement. The conversion window is counted separately and reused serially.

## Reproduction and independently executed checks

From repository root, run:

```sh
python3 -B scripts/research_package.py --package research/direct-native-grid-interface
python3 -B scripts/check_research_commit.py --package research/direct-native-grid-interface --check-modes
```

The registered launcher authenticates all frozen author bytes and runs both
normal and optimized child interpreters with fresh private bytecode-cache
directories. It compares newly produced JSON against frozen receipts without
rewriting them. The author suite covers 1,829 adapter cases, 132,460 macro
components, 180 sharp witnesses, 107 pack cases, 84 selectors and 12 controls.
That suite is regression evidence. The separate reviewer imports no author
adapter/checker and uses a dense sign kernel, Gaussian rational algebra and
exact integer parameter bounds: 360 full fields / 32,004 components, 5,460
phase entries, 5,460 terminal entries, 240 signed sharpness witnesses and 430
parameter enclosures. Corrupted source, nonendpoint divisor/parity, omitted
normalization and insufficient requested precision are detected.

These finite checks corroborate the universal proof; they are not native
execution, full CI equivalence, or proof-kernel verification. Eight retained
sources were independently compared with their exact Git commit/path bytes.
No full-history ancestry claim is made by the byte-transport check.

## Credit and remaining work

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance and
separate author/reviewer execution roles. #7849, earlier #8093 numerical work,
the retained normalized-H identity, common-grid proof and
`compiled-root-clifford-precision` endpoint parity lemma retain their original
credit. See `SOURCE-BYTES.json`, `PROOF.md` and the independent review for exact
dependencies and the review finding that led to the terminal-normalization
repair. Remaining work is a concrete native implementation with actual caller
admission and a joined historical-storage/movement account.
