# Four inherited partner-source corrections cannot be reassigned away

This is a scoped obstruction for [Mason Hale's PR2696](https://github.com/CrocSwap/integer-mult-bounds/pull/2696), head
`5a42add713e09a8798a84d0be7a8276626d9e785`. Its released handoff asks whether
another assignment of the eight recovered sources can remove the four remaining
centre splits. The answer is **no under the separated-source and fixed-reader
contracts below**. Changing those contracts remains open.

The new evidence is an independent four-source projection, a rank-four
correction matrix and a sharp conditional cut bill. This is not another root
calculation, a packing optimum or supplier admission. The selected result is
unchanged. [RESULT.json](RESULT.json) records the exact replay.

## The separated-source family

Let the partner sources be `P = (33,55,74,85)` and the eight reassigned sources be
`R = (49,83,98,101,68,80,88,31)`. Original source inputs are independent, including
sources that occur together in an intermediate recovery row.

The theorem allows arbitrary simultaneous helper assignments and invertible
charts for R, subject to these hypotheses:

1. Keep the original recovery operations and inherited P-source helper paths.
   At each new handoff the lender is exactly its original R input. Replacing a
   helper changes its incoming independent dirty value to a chart of that input.
   Deleted early echo reads contain only that helper's incoming dirty value.
   Consequently these substitutions have zero P-source projection.
2. Apply the resulting additive target compensation at the beginning of A.
   Its additional source-dependent terms use only original R inputs. The
   target-to-target linear continuation from that boundary is unchanged.
   No continuation operation reads a target into a non-target. All target
   scales are nonzero and target ADDs have distinct endpoints.
3. The original P-source response in the uncompensated continuation is retained.
   Hypothesis 1 gives this by linearity and induction through the helper updates.
   It is also an explicit boundary condition, not an assumption that arbitrary
   changed source programs preserve that response.

This family includes reassignments of the eight pure recovered inputs with
unchanged inherited partner corrections. It does not include changing the four
partner aliases, mixing a partner input into a new lender, moving compensation
past its boundary, or changing the target continuation. Physical feasibility
of an arbitrary assignment is not claimed.

## Exact projection and proof

Write `q_i = K_(47+i) x_(P_i)` for `i = 0,1,2,3`. The four binary chart matrices
are invertible and send their source port to line 30. Each q_i can therefore
vary independently. At the prelude boundary the correction on target order
`(23,34,50,108)` is

\[
 Qq=\frac14
 \begin{pmatrix}
 -1&1&-1&2\\
 1&1&1&-2\\
 -1&1&1&2\\
 1&1&1&2
 \end{pmatrix}q,
 \qquad \det Q=-\frac1{16}.
\]

All other target rows have zero P-source correction at that boundary. Omitting
these corrections and replaying the literal word gives this exact output
error, with every other target error zero:

| Target | Error without the partner correction |
| --- | --- |
| 23 | `-(q_0+q_2)/2` |
| 34 | `-(q_1+q_2)/2` |
| 50 | `-q_0/2+q_3` |
| 108 | `-q_1/2-q_3` |

The checker derives both tables from each complete published word. It does not
import the predecessor's generator, audit code, reported matrix or paid profile.
It checks that all eight new lenders have zero P projection at their handoffs.
With the prelude retained, all 112 target rows have their exact desired P-source
response. Noncommuting chart operators are formal words with adjacent inverse
cancellation. These identities therefore do not rely on unproved coincidences
between chart operators.

Let T be the target-to-target continuation and F_P its output response when the
partner correction is omitted. T is invertible: its target block is a product
of elementary ADDs and nonzero scales, with no target feedback into other rows.
For the checked word,

\[
 F_P+TQ_P=I_P.
\]

Here Q_P embeds the displayed four rows, including their separate invertible
source charts, into all 112 targets. Any valid member of the stated family has
unchanged F_P and T. Its early correction C must therefore satisfy

\[
 F_P+TC_P=I_P,\qquad C_P=Q_P.
\]

Terms depending only on R vanish under P projection. They cannot cancel any of
these four nonzero rows. The determinant also proves that the inherited
correction has rank four, so an equivalent correction cannot use fewer than
four independent target rows even after an invertible target-coordinate change.
That last rank statement does not pin their physical locations after a changed
coordinate contract.

This is a linear-algebra proof for arbitrary inputs and assignments satisfying
the hypotheses, not an exhaustive search over assignments or a theorem about
all possible helper mechanisms.

## Sharp cut bill, with its extra hypotheses

The support result above does not alone prove a private-copy cost bound. For
that bound additionally retain the four targets' **exact line-30 cut frames**,
the pinned centre-to-target cut incidences, and at least one zero-frame reader
per centre. Retain rank-eight producers and the descending private-copy model
used by PR2696. No target chart changes or nonmonotone target frame paths are
allowed. These are material restrictions.

The forced incidences are:

| Forced targets | Centres that read them |
| --- | --- |
| 23, 50 | 240, 9 |
| 34, 108 | 92, 224 |

Thus four centres must pass through rank one and then zero. The other four
must at least reach zero. For `0 < p < 1`, strict subadditivity gives
`(u+v)^p < u^p+v^p` for positive u,v. Combining all positive decrements before
and after the required rank-one stop proves the cut lower bound

\[
 \boxed{4(7^p+1)+4\,8^p},
 \qquad \text{equivalently }4H_7+4H_1+4H_8.
\]

The actual published chains attain it in both providers. The cut rank mass is
64. Additional intermediate stops cannot reduce this bill. RESULT.json records
one actual zero-reader witness for each centre, the literal invoice, and the
forced centre set `{9,92,224,240}`.

**The extra zero-reader hypothesis must not be dropped.** If every reader of a
centre were instead lifted to line 30, its cut could end at rank one and omit
H1. Its target-lifting and continuation costs would need a new complete bill.
Likewise, enlarging the forced targets' frames or changing their coordinates
escapes this particular cut theorem. We do not assign those costs zero or claim
that the support theorem rules out such changed contracts.

## Replay and verification limits

```sh
python3.12 -B scripts/research_package.py --package research/t74-inherited-centre-floor
python3.12 -O -B research/t74-inherited-centre-floor/verify.py
python3.12 -B -m unittest discover -s research/t74-inherited-centre-floor -p 'test_*.py'
ruff check --select E,F,B,I,UP,SIM research/t74-inherited-centre-floor
```

The registered replay is offline and uses only the standard library. The two
compressed fixtures are byte-for-byte copies of PR2696's words, authenticated
before parsing. INPUTS.json supplies their exact upstream paths, Git blobs,
compressed hashes and decompressed hashes. Upstream notices are preserved in
`inputs/`. SOURCES.json separately pins the assignment's main-branch provenance.

Each provider has seven rejection controls: a correction sign, a chart operator,
target feedback, a singular target scale, a lowered forced target, a changed
producer frame and removal of all zero readers. The omitted-correction replay is
an additional exact semantic failure control, not just a stale-invoice check.
The unit tests also mutate the continuation and verify the CLI's real output.

Only four independent source columns are checked, not all 646 live inputs.
No native phase, physical ownership, precision, cleanup, global invoice, outer
inequality or all-size multiplication theorem is reverified. PR2696 remains a
pending dependency, not an admitted supplier. This package establishes the
stated source-column and cut facts without endorsing its headline kappa.

Python 3.12.15 on Linux reproduced the receipt in this session. The normal and
optimized runs use explicit exceptions, not assertions. The checker has no
recursion, network operations, dynamic code generation or predecessor imports.
Each source word has a 20,000-event capacity; there are 704 rows, at most 4,096
terms per row, 128 operators per term and 256 bits per rational numerator or
denominator. Source hash checks precede decompression. All functions are under
60 lines.

Power-of-ten rule 3 has a managed-runtime deviation in `verify.py`: Python
allocates sparse dictionaries and rational objects during replay. The fixed
source sizes and executable event/row/term/word/integer capacities bound live
work; every process ends after the finite replay. No claim of allocation-free
execution is made. A native fixed-pool port is appropriate only if this small
checker becomes a production component. Static diagnostics and fault tests
cover the present scoped implementation.

## Open next questions

- Can a changed recovery or assignment involving `{33,55,74,85}` remove one
  forced correction? First derive its exact original-input identity at a legal
  retirement cut and the new target response. Its source lifetime, restoration
  and complete frame bill are blockers. Further eight-lender-only assignment
  search cannot answer this question under the proved boundary.
- Can a different target-coordinate or cut-reader contract avoid the conditional
  cut floor affordably? Start with one explicit compensated caller and charge
  every changed target lift and eventual restoration. No complete constructive
  upper bound is available here.

Expansion decision: narrow this branch of the assignment handoff to changing an
inherited partner path or a target/cut contract. The result does not preclude
other A/B savings or owner-fill improvements in the same supplier.

## Credit

New proof and independent checker by Nick Petalas, Apache-2.0. Mason Hale's
PR2696 supplies the concentrated assignment and both fixtures. Retain zxv's
PR2530 source-partner recovery, Tekalign's PR2436 lifted compensation, Jeremy
Kothe's PR2462/2588 words and PR2673 hosting, and the source, native, bit and
owner lineage credited in the unmodified upstream notices. No independent human
review is claimed. The canonical investigation is
[Discussion2612](https://github.com/CrocSwap/integer-mult-bounds/discussions/2612#discussioncomment-18955188).
