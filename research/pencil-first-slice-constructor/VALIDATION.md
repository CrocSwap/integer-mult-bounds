# Validation and limits

PROOF.md supplies the quantified algorithm and arithmetic bound. Separate AI
static review checked minimality, equal-degree missing factors, q-Frobenius over
prime powers, the supplied-field model, row-pivot exact division, one-branch
Berlekamp splitting and cost. Before freezing, two cost clarifications added
the dependence on n when deg f exceeds q^e and the reference's Fermat extension-
inverse overhead O(n e^3 log q). Neither changes construction or receipts.
No independent human or proof-kernel acceptance is claimed.

The primary uses raw polynomial Bareiss, explicit infinity/base points,
Frobenius gcds and fixed-space splitting. It self-checks every accepted census
answer and all named witnesses. The separate oracle uses trial-division field
definitions and literal projective matrix evaluation. Its first source/output
were sealed and executed before reading any primary result. After both blind
seals it reads RESULT.json only, never primary code: all census status/degree
streams and ALL17 named returned moduli, points, literal slices and BOTH inverse
products pass. Different valid moduli occur in the q5 case. It does not check
every primary census inverse. No predecessor executable or census is run.

| Raw domain | Cases | Singular | First degree1 | First degree2 |
| --- | ---: | ---: | ---: | ---: |
| F2 dimension0, empty calibration | 1 | 0 | 1 | 0 |
| F2 dimension1, all | 4 | 1 | 3 | 0 |
| F2 dimension2, all | 256 | 64 | 192 | 0 |
| F3 dimension1, all | 9 | 1 | 8 | 0 |
| F3 dimension2, all | 6561 | 513 | 6048 | 0 |
| F5 dimension1, all | 25 | 1 | 24 | 0 |
| F2 dimension3, diagonal only | 64 | 37 | 21 | 6 |
| Total | 6920 | 617 | 6297 | 6 |

Input order and domains were frozen before execution. Seventeen named checks
exercise first degrees2/3/4, infinity-only success, nonmonotone degree3 success/
degree4 failure, actual polynomial row swaps, Berlekamp splits and the large-q
branch without dense expansion. Original and strict-equivalent scrambled
versions are included; they are not claimed disjoint from the census. The
attaining/nonmonotone examples remain credited predecessor examples. Root
also checked the fixed prime1,000,003 by 999 trial divisors through1000.

Primary controls are 12 actual rejections and five computed positive boundary/
instrumentation checks. A genuinely invertible later-degree slice is rejected
for not being first. Changed slice/inverse coefficients, reducible modulus,
bad types/domains, malformed JSON and changed source bytes reject. The oracle
has five actual witness/singular rejections and computed infinity-only and zero-
polynomial controls. Exact details are in the receipts. A broad negative-helper
exception catch does not identify the rejecting guard by itself; static review
checked the actual semantic paths. External corruption checks are separate.

Every first and final normal/optimized emission/strict run passes with exit0
and empty stderr. Per-engine output is byte-identical between first and final
modes. The oracle's only post-first edit requires primary provenance labels to
match the hard source/input pins; computed output is unchanged. Its blind first
source and receipt are preserved externally. No scientific execution failed.
Root's exact seven-domain comparison agrees.

| File | SHA256 |
| --- | --- |
| verify.py | 6d4918c0752eff0d5dd34f3104b1f6e83985e22108da453ab4ffd00d4e028627 |
| RESULT.json, 163885 bytes | e7672e624528c120eaf70ffceb5055e03b8bef92248969273bf7c75071e71239 |
| oracle.py | 2a355faebea93a71eca09c1523b1988ba043cec3724d5cd8bfadea6e49bbe619 |
| ORACLE.json, 20418 bytes | 656a28dd1a256a81c284e2c13527c539a43c8a3f92bf042b658fd6ddf2039de8 |
| PENCILS.json | 955e6a7de7dbff3727829d1e3489c954a3197701dd37fcc859744a8d725aaff3 |
| SOURCE-PINS.json | 457cd888ff00f2ac9726027b77b2ba5714f10cc92e533e87db7a778e490c930e |

Direct runs measure about0.5–1.1s here, with no speed comparison or timing gate.
The operation bill is a written arithmetic upper bound, not a measurement of
every Python coefficient operation, memory instruction or bit. Authentication
precedes input parsing; retained JSON rejects type aliases/malformed data under
both modes. Runtime is package-local; canonical catalogue/selected entries are
provenance. Submission/export/cold/hosted checks are reported after execution
in the PR and handoff.

Remaining: nonprime executable backend, concrete representation/bit/tape cost,
field descent/original-field SL transport, an actual native consumer, dirty
physical restoration and a complete coefficient/access/precision/stock/compiler/
outer invoice. All five selected assumptions remain. No new kappa, selected-
frontier change, human or kernel acceptance follows. See README.md and NOTICE
for predecessor and classical-method credit.
