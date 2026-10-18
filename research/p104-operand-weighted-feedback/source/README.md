# Precision of the completed delayed-query P104 word

This supplies a finite local precision implication for Jose Manuel's
[PR2139](https://github.com/CrocSwap/integer-mult-bounds/pull/2139), exact head
`1df674ca8e9d9e0fb98ba4df402b648e9b3be0a4`. It does not supply a rounded
recursive implementation, an admitted supplier or a new exponent. The
predecessor's unfavorable fixed-profile cost screen remains unchanged.

Adam Gall's [PR2096](https://github.com/CrocSwap/integer-mult-bounds/pull/2096)
checks precision for the different `G/2` channel. Its next question 2 asks for
combined prefix/error maps once a corrected chronological word is available.
This result checks that implication on PR2139's completed forward identity
word, rather than transferring the old channel's constants.

## Exact result

The norm is the maximum of individual register Hilbert norms. It is not the
addresswise maximum norm. Let every independent initial register have norm
at most `B`.

| All-cut quantity | Exact coefficient |
| --- | ---: |
| Ideal input-to-register row norm `P` | 131072 |
| Accumulation of independent unit absolute defects `A` | 1394705 |
| Accumulation of independent weighted defects `K` | 2134050 |

All three first attain their maxima after combined event **33373**, in source
register **93**. Events are zero-based: 7686 initial compensation additions,
then the predecessor's 26647 actions. The attaining instruction is
`source93 -= 8*source103`. Its ideal row is

```
-65536 * input86 - 65536 * input93.
```

Input86 is one of the omitted source ports and is an arbitrary dirty helper.
The final source row is just input93. The final target rows are `Y_t + X_t`,
and all 628 dirty helpers restore their own inputs. Thus the ideal endpoint
maximum of two cannot replace the all-cut coefficient 131072.

[RESULT.json](RESULT.json) contains the complete 2-input and 29-defect
attaining rows, all-cut norm-stream hash and endpoint error maxima. The
checker visits every changed register after every instruction; untouched
registers retain their preceding norm. Exact adapters preserve Hilbert norm,
and exact resets cannot increase it. This covers the initial boundary and
all 34333 subsequent instruction boundaries, not sampled cuts.

There are 32722 defect sites: 28108 additions, 707 scales and 3907 positive
native transports. There are also 32 exact private resets and 1579 exact
phase/adapter annotations. The eight private copies are additions following
owned initialization, not eight uncharged extra operations. Their later
reset does not erase defects already propagated to another register.

The full paid profile stays
`2564 H1 + 547 H2 + 432 H3 + 142 H4 + 83 H5 + 128 H6 + 11 H7`,
with rank mass 6782. No precision or recursive charge is removed.

## Error contract and proof

### Literal scalar reduction

Use the predecessor's actual common unitary charts. A physical register at a
cut is `Gamma_W z`. Each exact native transport is
`Gamma_new Gamma_old^-1`; additions and scales have their literal rational
coefficients in logical coordinates. Boundary monomial factors are exact.
The inherited normalized Clifford factors are unitary in Hilbert norm; this
is not a claim of addresswise contraction.

An additive physical output defect at site `j` becomes
`eta_j = Gamma_after_j^-1 e_j`, with the same Hilbert norm. Therefore every
cut row has the exact form

```
z_r = sum_s a[r,s] * input_s + sum_j c[r,j] * eta_j.
```

The implementation retains signed dyadic coefficients until it takes the
row's absolute sum. At every updated row it checks cached input, absolute and
weighted norms against direct reductions of the complete coefficient maps.
It does not multiply positive majorants throughout the word. A separate
reverse-adjoint recurrence uses `Fraction` arithmetic and
agrees on the attaining rows. Sign-aligned forward executions attain `P`,
`A` and `K`. For arbitrary independent vectors, choose one unit vector and
align each input or logical defect with the sign of its row coefficient.
Unitary charts convert those logical defects to physical defects with the
same norm. This proves sharpness for **independent additive vector defects**,
not for correlated rounding errors.

Exact private reset replaces only its current row by zero. Existing error
symbols in other registers survive. Each later instruction has a fresh
error symbol, so reusing the private field cannot alias different lifetimes.
The replay independently checks all 844 initial columns, including the eight
private columns, against the completed endpoint and full frame contract.

### Absolute defects

If every defect has norm at most `delta`, every cut has error at most
`1394705 * delta`. This finite independent-defect coefficient is sharp.
For example, `delta <= B * 2^(-b-21)` suffices for all-role error at most
`B * 2^-b` for any integer `b >= 0`.

### State-relative feedback

Assume exact dyadic coefficients and a common `u >= 0` satisfying these
completed-instruction output-defect bounds on the actual perturbed operands:

- Native transport: `u * ||input||`.
- Addition `dst += a*src`: `u * (||dst_before|| + |a|*||src_before||)`.
- Scale `dst *= a`: `u * |a| * ||dst_before||`.

Resets and monomial factors are exact. A recursively implemented transport
must first meet this completed-output contract; its internal errors are not
analyzed here. For a copy expressed as an addition after exact reset, the
addition hypothesis is sufficient, but may overestimate its actual error.

Put `w_j=1`, `1+|a|`, or `|a|` respectively at those sites. The sharp weighted
independent-defect coefficient is `K=2134050`. If `M` is the maximum actual
register norm over the finite execution, then

```
M <= 131072*B + 2134050*u*M.
```

When `2134050*u < 1`, rearranging gives

```
M <= 131072*B / (1 - 2134050*u),
max_boundary_error <= 131072*2134050*u*B / (1 - 2134050*u).
```

For every integer `b >= 0`, **`u <= 2^(-b-39)` suffices** for all-cut error at
most `B*2^-b`. Indeed,

```
K*(P+1) = 279716335650 < 2^39,
P*K = 279714201600 > 2^38.
```

For `b >= 0`, `K*(P*2^b+1) <= K*(P+1)*2^b < 2^(b+39)`, which proves the
claim for all `b`, not only the tested examples. The second inequality means
38 uniform guard bits fail this particular sufficient feedback estimate.
It does not prove a minimal numerical precision requirement. This estimate also does not justify subtracting 39
bits from, or replacing, the selected production precision bill.

## Source binding and replay

[producer.py](producer.py) is byte-for-byte PR2139's original `verify.py`.
Its original README and source manifest are under [predecessor/](predecessor/).
`export_word.py` authenticates inputs before importing that producer, observes
only the return of its `main` function, and exports its actual initial frames,
final frames, every compensation coefficient, every action and frame basis.
It does not alter the producer's operations or checks. The registered replay
reconstructs and compares **every** exported field, not just a profile or hash
from a submitted receipt. Native mode also runs the predecessor's 241 new
recipe checks, all 421 bindings and its global-phase rejection control.
Original selected native recipes retain their inherited proof and pins; this
is not a fresh audit of every retained Clifford recipe.

The default precision replay reads only `WORD.json.gz` and `RESULT.json`,
needs neither Git nor network and writes nothing. It verifies the complete
uncompressed word SHA256 before parsing. Full producer rebinding requires
Git history for the original selected archive. Compressed bytes are not the
mathematical regeneration comparison.

From the repository root, standard-library CPython 3.12:

```sh
python3.12 -I -O -W error -B research/p104-delayed-precision/verify.py
python3.12 -I -O -W error -B research/p104-delayed-precision/test_verify.py
python3.12 scripts/research_package.py --package research/p104-delayed-precision --check-only
python3.12 scripts/research_package.py --package research/p104-delayed-precision
```

`verify.py --write NEW_PATH` and `export_word.py --write NEW_PATH` create new
files exclusively. The behavior suite checks seven separate endpoint adjoints,
dyadic coefficient extremes, private-defect survival after discard, missing
clear and baseline compensation, illegal charts, receipt/word corruption,
changed-producer rejection before import, no overwrite, capacity limits and
relocated read-only normal/optimized execution.

Observed locally on Linux x86_64 with CPython 3.12.15: the complete registered
replay passes, including new native phase checks and all nine behavior tests
in normal and optimized modes. The 65 repository research-workflow tests and
`python3 -B scripts/research_baseline.py` also pass. The latter checks selected
source bindings only, not the selected cold replay. No hosted CI pass,
proof-assistant run or independent human review is claimed.

### Implementation bounds

New replay loops have fixed stream bounds: 844 roles, 1008 frames of at most
nine generators, 34333 events and at most one defect symbol per event. Input
files are capped at 4 MiB compressed and decompressed. Receipt generation
observed at most 671250 live error coefficients and a maximum row denominator
of 54 bits. The optimized direct replay took 3.27 seconds with 114768 KiB peak
RSS on the stated Linux/Python environment. These are local measurements,
not portable resource guarantees. The registered commands have explicit
120/240-second limits.

Python requires dynamic allocation and dictionary dispatch. These are
managed-runtime deviations from Power of Ten rules 3 and 9, bounded by the
fixed domain above; there is no ambient registry or unbounded queue. Rule 8
also has a narrow replay-only deviation for importing the authenticated
producer and a return-profile callback with one known target, restored in
`finally`. The independent precision verifier does neither. All new functions
fit within 60 lines; Python warnings are errors in the registered checks.
No separate type checker or linter was available locally; strict compilation
and execution are the available diagnostics, not a substitute for type analysis.
The preserved producer and loader contain long functions and historical
library/control-flow patterns. They remain immutable predecessor inputs,
not refactored code. Their compensating controls are source authentication,
fixed input geometry, exact regeneration and bounded replay. A future
predecessor API change would require a separately source-bound successor.

## Open next questions

1. Bind an actual rounded rank-1 through rank-7 child to the completed-output
   Hilbert defect hypothesis. First test the exact rounding convention at
   `u <= 2^(-b-39)`. The missing implementation/interface, not native unitarity,
   blocks recursive precision admission.
2. Reduce the source93 transient while retaining the full dirty boundary and
   bill. First inspect the gauge/scalar cleanup interval around event33373,
   propose one exact resynthesis, and replay all columns and paid operations.
   Common-chart legality and arbitrary dirty restoration are required.

Global owners, the dual word, tape/all-size lifting and supplier admission
remain open. PR2139's fixed-profile cost obstruction still applies. Neither
finite precision implication nor automated verification is a complete
multiplication theorem or independent human review.

## Credit and freshness

Jose Manuel / PR2139 supplies the entire corrected construction. Adam Gall /
PR2096 supplies the Hilbert-defect and feedback method on the older channel;
no constants or code from that package are imported. Rohan Arun / PR1972,
Chafik Boukhalfa / PR1991, Ali Romman's source reconstruction and Gaussian
interpreter, Adam Gall / PR1940, Josie Elliston / PR1071, icekylinx's Clifford
lineage and the selected Hamming/dirty-helper contributors retain their
original attribution. See [NOTICE.md](NOTICE.md) and the retained source
manifest. New material is Apache-2.0.

The scientific base is canonical main
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4. The sole chooser
nonce is `159427fb87da401855d7b74679378fb5`. [TASK.json](TASK.json) records the
changed scope and overlap limits. The canonical coordination claim is in
[Discussion2121](https://github.com/CrocSwap/integer-mult-bounds/discussions/2121#discussioncomment-18934115).
No selected record, frozen predecessor or review disposition is changed.
