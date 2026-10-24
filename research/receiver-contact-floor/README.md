# Arbitrary-length contact floor for PR4470 receiver windows

**Result (author-checked scoped proof and exact certificate):** none of the 128
eligible forward receiver windows of the pinned PR4470 construction admits a
cheaper paid rank profile through a finite scalar-shear word on the same three
persistent fields, with the same monotone entrance/exit frame contract. This
holds for **every price `r^t`, `0 < t <= 1`**, including the predecessor's
`t = 1 - 0.00302015`. Word length and nonzero scalar coefficients are unrestricted.
The original two-shear word attains the lower bound in each window.

This closes the explicit arbitrary-length gap in
[#4567](https://github.com/CrocSwap/integer-mult-bounds/pull/4567), following
[#4546](https://github.com/CrocSwap/integer-mult-bounds/pull/4546). It uses necessary
information-flow contacts and graph bridges, rather than another word census.
It is **not** a global supplier ceiling, a new kappa, or supplier admission.
Overlapping window conclusions cannot be added.

Concurrent investigations [#4572](https://github.com/CrocSwap/integer-mult-bounds/discussions/4572),
[#4573](https://github.com/CrocSwap/integer-mult-bounds/discussions/4573), and
[#4577](https://github.com/CrocSwap/integer-mult-bounds/discussions/4577) pursue
the same conclusion through finite-state relaxations. They appeared after the
initial overlap snapshot and were found before publication. This package is a
parallel static-contact proof/checker with no priority claim; it does not claim
to have reviewed their code or to provide independent human review.

## Contract and statement

Fields are `a, b, x`, numbered `0, 1, 2`. They contain arbitrary independent
initial data. The logical endpoint is

    a' = a + ca*x,  b' = b + cb*x,  x' = x,   ca, cb in {-1, 1}.

A candidate uses any finite sequence `y_i += c*y_j`, `i != j`, with nonzero
scalar `c` (over the rationals, or any characteristic-zero field), and has that
same endpoint. Each field has an initial binary subspace `S_i` and final
subspace `E_i` of `F_2^9`. Its frames grow by inclusion. Both operands of every
shear occupy one common frame. Every positive dimension increment, including
the last movement to `E_i`, is charged as a separate child rank. Additional
nonnegative scalar costs are omitted in the candidate's favor.
The scalar endpoint is evaluated in transported logical coordinates: a frame
movement changes representation, preserving the field's scalar coefficient
vector. This is the common-frame model used in #4546/#4567.

Only these three fields are available. Extra or owned fields, a decreasing
frame step, a changed boundary, internal warps, and changes across nonadjacent
or multiple windows are outside the statement. This package does not claim a
backward-orientation result or recheck the full native/phase/outer construction.

More generally the proof works for any nonnegative concave price `f` on integer
ranks `0,...,9`, with `f(0)=0`. The machine check uses only exact set operations
and integer inequalities; no logarithmic approximation or sampled exponent
stands in for the quantified price statement.

## Proof

**1. Admissible contacts and forced edges.** A contact between fields `i,j`
has a common frame `F` satisfying

    S_i + S_j <= F <= E_i intersect E_j.                         (1)

Define the undirected admissible-contact graph `G` by including `ij` exactly
when the left subspace is contained in the right. Every used contact lies on
an edge of `G`. The graph of contacts actually used must connect `x` to both
receivers: otherwise the component not containing `x` cannot acquire any
coefficient of the arbitrary initial `x`. Thus it is a connected spanning
subgraph of `G`. Every bridge of `G` must be used at least once. For such an
edge, each incident field must visit a contact dimension in

    [dim(S_i + S_j), dim(E_i intersect E_j)].                    (2)

This conclusion is independent of word length, coefficient size, cancellations,
and the direction of a contact. The source windows have either a triangle
(96 cases) or a two-edge tree (32 cases).

**2. A contact carrying original `x`.** At any time, if a field's current
logical value has a nonzero coefficient of initial `x`, its current frame
contains `S_x`. This is an induction: it is true initially; monotone moves
preserve it; and a shear's common frame contains the old frames of both
operands. A newly nonzero coefficient must come from an operand with a nonzero
coefficient. Cancellation can remove a coefficient but cannot violate the
implication. The source and target of a shear have distinct roles; all data
are arbitrary, so this coefficient argument is legitimate.

Each receiver starts with coefficient zero and finishes with coefficient
`ca` or `cb`, which is nonzero. At a contact where it first acquires original
`x`, the common frame contains `S_x`. The field `x` itself must participate in
some contact, or no receiver could acquire its initial value; any such contact
also contains `S_x`. Consequently **each of the three fields** has at least
one contact on an incident edge `ij` with dimension in

    [dim(S_i + S_j + S_x), dim(E_i intersect E_j)],              (3)

where the interval is included only when the subspace containment holds.
For a field, take the union over its incident edges. This is a necessary
dimension set, not an assertion that every dimension choice is realizable.

**3. Finite coarsening of every arbitrarily long path.** On each field select
one witness contact for (3), and one for every incident bridge requirement
(2). Different requirements may use the same contact. Retain their dimensions
together with the entrance and exit dimensions; sort and remove duplicates.
Successive differences give a partition of `dim(E_i)-dim(S_i)`.

The actual paid path refines that partition. For a concave `f` with `f(0)=0`,
`f(u)+f(v) >= f(u+v)` for nonnegative `u,v` in the domain (apply concavity
between 0 and `u+v` twice). Therefore coarsening cannot increase the bill.
Enumerating the finite dimension choices from (2),(3) contains a coarsening
of every actual path, regardless of its length. Ignoring simultaneous frame
incidences, scalar endpoint feasibility, and contact order only enlarges this
relaxation. The checker never asserts those relaxed choices are constructions.

**4. Exact comparison for every concave price.** Let `P` be the incumbent's
list of positive ranks and `Q` any relaxed coarsened list. The certificate
checks equal rank mass and, for every integer `k=1,...,9`,

    sum_{r in P} min(r,k) <= sum_{r in Q} min(r,k).              (4)

These inequalities imply `sum f(P) <= sum f(Q)`. To see this without any
numerical exponent calculation, set `d_k=f(k)-f(k-1)` and use

    f(r) = r*d_9 + sum_{k=1}^8 (d_k-d_{k+1})*min(r,k).

Concavity makes every `d_k-d_{k+1}` nonnegative. The linear term cancels by
equal rank mass; (4) handles the rest. The checker can stop at the largest
rank in either list, since subsequent inequalities are equal rank-mass
identities. Combining steps 3 and 4 gives

    incumbent cost <= relaxed coarsening cost <= actual cost.

All 128 reconstructed incumbents have legal nested frames, the required
two-shear endpoint, and an attained partition in the relaxation. Thus the
minimum is attained by the incumbent. This last assertion is per window;
it does not combine incompatible changes in overlapping windows.

## Why both necessary constraints matter

Window 10557 has entrance dimensions `(0,0,1)` and exit dimensions `(2,1,1)`.
Merely requiring each field to participate would allow a spurious `(2,1)`
bill in place of the incumbent `(1,1,1)`. The contact that supplies original
`x` must already contain its rank-one entrance, forcing the split.

In window 11073, the receiver/source entrance dimensions are `(2,4,2)` and
exit dimensions `(3,4,4)`. The first receiver cannot meet the second, whose
entrance has dimension four. The two source-receiver edges are both bridges.
The source must pass through dimension three to reach the first receiver and
then dimension four to reach the second, so its rank-two growth cannot be
merged into one payment. Dropping the bridge constraint again admits the
false optimistic partition `(2,1)` instead of `(1,1,1)`.

## Evidence and reproduction

Base: canonical main `f626db5c3a3d781d8f7695038776c621651f75e1`, priority
revision 7. `SOURCES.json` pins the seven executable/data inputs needed by
`research/joint-helper-lattice/native_joint.py:construct`, including its two
compressed original artifacts. They are authenticated **before** construction
in an isolated Python process with a fresh bytecode cache. No #4546/#4567
acceptance, enumeration, interval, or relaxation function is imported.

The source constructor is reused for data, so this is not an independent
implementation or validation of that constructor or the complete supplier.
The new window extraction, floor, concave comparison, and controls are separate
code. The pinned constructor is small enough for this bounded replay; its
expensive full native/phase `run()` path is not invoked.

`CERTIFICATE.json` contains every window's index, phase, roles, signs, actual
binary bases, incumbent partition, admissible contacts, bridge requirements,
and every coarsened partition. The normal verifier compares every field to
fresh output and does not rewrite the certificate.

```sh
python -B scripts/research_package.py --package research/receiver-contact-floor
python -I -O -B research/receiver-contact-floor/verify.py
```

CPython 3.12.0 on Windows; standard library only. Direct replay is about two
seconds on the contribution host. Expected status: `PASS_RECEIVER_CONTACT_FLOOR`.

Registered and optimized replays passed, as did committed-byte comparison and
an isolated Git-free export replay. In the private exported copy, changing a
rank, changing a certificate boolean to an integer, deleting a certificate
field, and modifying/removing the constructor were all rejected. These are
local validation results, not a claim about upstream CI or formal acceptance.
The portable replay can be repeated with `scripts/export_research_package.py`
as described in `docs/research/package-export.md`, followed by the second command
above in the extracted tree.

| Evidence | Coverage |
| --- | --- |
| Source windows | 128 total: 123 phase B, 5 cleanup_tail |
| Admissible graphs | 96 triangles, 32 two-edge trees |
| Price check | Exact integer (4), every relaxed partition in every window |
| Geometric controls | All 84 unit-shear words of length at most four with endpoint `a+=x; b+=x`, against three small frame contracts |
| Actual control paths | 106, 15 and 2,868 (2,989 total), each with checked source-information invariant and an admissible coarsened lower bound |
| Essential-rule ablations | Remove (3) at 10557 or bridges at 11073: the claimed floor fails |
| Scope-positive fixture | With all entrances zero and exits the same plane, `(2,1,1,1,1)` can improve to `(2,2,2)`; the checker admits it |
| Rejections | Decreasing frame contact and omitted rank mass |

The tiny word enumeration tests the lemma's geometric relaxation; it is not
the reason the all-length statement follows. That statement follows from the
proof above plus the finite boundary comparisons.

## Selection, overlap, limitations and credit

Canonical investigation: [Discussion #4574](https://github.com/CrocSwap/integer-mult-bounds/discussions/4574),
taken from the #4567 all-length gap in the central handoff. The initial helper
refresh covered 355 open PRs and 3,470 Discussion records, with incomplete
sparse local-note coverage. The nearest results are #4546 (first twelve
windows through four unit shears), #4567 (all 128 through bounded lengths and
coefficient alphabets), and #4504 (chronological frame and invoice audit).
No claim of exhaustive historical novelty follows from that search.

The submission refresh at 2026-10-22 08:06 UTC covered 357 open PRs and 3,489
Discussion records. Canonical main was still the pinned base. In addition to
the concurrent claims credited above, #4567 had advanced to
`5ac594d1bc1e6d91f20ef8157f38bb9b29768bfd`, adding nonadjacent and single-contact
tests. Its all-length explanation remained unproved in that version. This
package retains its original adjacent forward-window scope and earlier
predecessor attribution; no scientific input was repinned.

This is a refined `independent-moment` task: prove a previously unproved
cost implication at a specific newer caller, rather than recompute a root.
The family decision is to stop length/coefficient expansion within this
model. Reopening requires a changed boundary or operation model. This is
research guidance from a scoped result, not a change to the task catalogue,
the selected frontier (still conditional kappa 0.0023), or maintainers' decisions.

The default orientation baseline was attempted but could not run in the sparse
checkout because the full selected package was omitted. The selected record,
review, source manifest and reproduction entry point were read; selected
cold replay, full native phases, backward windows, hosting, stock, precision,
and compiler/outer admission were not checked. No global lower bound or
practical multiplication speedup is established. The proof is author-checked,
not formally verified or independently reviewed by another agent or human.

Credit Chris R / **Clear1nsight**, #4546 at
`55b8d34c82fc4df6499c5037e156db6e990b96fe`, for the fixed-boundary model and
initial ceiling; **Ryanson Jonathan / pinterbanget**, #4567 at
`50fedd98cda709707e4291c542e20ead96bcc786`, for the all-window extension and
explicit all-length question; **Cinna Davis / 1337isnot1337**, #4470 at
`b9a13c1673e0e9697de410de16e8bbf3207a7363`, for the retimed native data;
**zxv** for receiver sharing and productive helpers; and the original native,
Clifford, geometry, mixed-target (Jacob Alan Sussman), and outer contributors
retained in the source notices. The package-generator and replay infrastructure
retain Douglas Colkitt and their credited contributors' attribution.

Prepared for **Mihir Srivastava**, with substantial **OpenAI Codex** assistance
for the argument, code and checks. Apache-2.0; predecessor files remain unchanged.

## Open next questions

- Can one additional, explicitly priced field avoid these mandatory contacts?
  This matters because extra workspace changes the information paths. First
  specify its entrance, exit, ownership and restoration, then test an optimistic
  four-field floor on one window. Its costs are unknown, not zero.
- Can changing one boundary jointly with its actual neighboring consumer yield
  a saving? First price a concrete combined interval, including the movement
  paid outside these two gates. The fixed-boundary theorem does not cover that
  contract, and overlapping local gains cannot simply be summed.
- An independent proof review can check steps 2 and 3 against the same common-frame
  model and replay the seven pinned inputs. No further length census is needed
  unless that review finds a gap or changes a hypothesis.
