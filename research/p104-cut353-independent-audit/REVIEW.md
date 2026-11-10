# Conditional two-sided cut and fresh-input surgery review

Verdict: the displayed algebraic surgery is **correct conditional on the premises below**. In particular the row and column identities are both needed, and the extracted suffix is D only because S commutes with the remaining fresh-stage target D. This note does not verify any actual prefix, endpoint, clock or physical address claim.

Source: thu-nmrc PR6716 head `a467457692bc9e11113d9b2e2e34ea8ffb553b58`, package `research/p104-common-idle-double-retirement`, PROOF Sections 1 and 4 and WITNESS.json. Source identity, current-main guidance and the preceding read-only scouting boundary are recorded in MATH-SCOUT.md. No checker or mathematical program was executed for this written review.

## Premises and operator order

Use column payloads; the rightmost matrix acts first. Let P be an invertible literal prefix on the closed main-field interface and L its remaining suffix. Assume the entire normalized endpoint is `E=L P`, diagonal in the original independent input fields. Any omitted native/helper fields must form the promised closed interface at these boundaries under the inherited LOCAL contract; omitting an actual coupling is not justified by this lemma.

Let e be the standard pivot column (source field 4). Let a,c be ordinary rational row vectors and b,d ordinary rational column vectors, satisfying

    ab=cd=1,    aP=S c,    Pd=S b.

Here S is an invertible common payload operator; ordinary scalar matrices commute with it. Suppose invertible ordinary matrices G,J, derived from their literal gates, satisfy

    e^T G=c,    Gd=e,    e^T J=a,    Jb=e.

Assume G is supported only on a group of original fields with the same complete endpoint target SD (source fields 4,20,21), and ordinary rational coefficients commute with this target. Consequently `GE=EG`. Also assume `SD=DS`. The latter is supplied in the source by the central operator/fresh disjoint-stage interface, rather than by the dual-pair identities alone. All of these are premises to be checked against the actual source representation.

## Exact block separation

Insert G inverse at input and J at the cut, giving

    P' = J P G inverse.

The pivot row is

    e^T P' = aP G inverse = S c G inverse = S e^T.

Since `G inverse e=d`, its pivot column is

    P'e = J P d = J S b = S Jb = S e.

Thus both off-diagonal pivot couplings vanish and, in pivot/rest order,

    P' = diag(S,K).

Invertibility of P and the ordinary bases implies invertibility of K. The conditions ab=cd=1 make the row/column pairs normalized ordinary dual pairs; once the four G/J identities are supplied they are also implied by those identities. They do not replace either of the identities involving P. No S-valued coefficient is needed in G or J.

The adjusted suffix is the literal composition of J inverse, the original suffix and the final G:

    L' = G L J inverse.

Its product with P' is `G E G inverse=E`. Therefore

    L' = E (P') inverse = diag(SD S inverse, E_rest K inverse)
       = diag(D,H).

The last equality uses `SD=DS`. Without that premise the first block is `SD S inverse`, not D; the abstract row/column identities alone would not justify the claimed plain-stage suffix. In the source the premise is stated explicitly: central q, its square and lambda commute with the fresh stage operators. No other commutation of P or K with S is required.

This also shows why both sided identities matter. A correct pivot row without the correct pivot column can leave other outputs depending on the completed pivot; a correct column without the row can leave the purported completed output depending on other independent inputs.

## Fresh-input substitution and independence

Let x contain all original independent inputs and introduce a genuinely new independent payload z in fresh field 34. The prefix and all input-basis gates must leave that field untouched. At the separated cut the abstract state is

    pivot = S x_p,    rest = K x_rest,    fresh = z.

Freeze the completed original pivot. In the entire literal suffix L', rename every pivot reference to the fresh field, including the J inverse and final G gates. The resulting suffix acts as diag(D,H) on (fresh,rest), so the final state is

    original pivot = S x_p,    rest = E_rest x_rest,    fresh = D z.

This is a direct-sum extension by an arbitrary input z. No duplication, equality, zero initialization or dependence on x is used. The other inputs retain their original targets because `HK=E_rest`. Intermediate suffix gates may mix fresh and other fields; only the complete suffix has the proved block form. Aggregate block separation alone does not establish that the original pivot is physically untouched: complete literal renaming and absence of address aliases are separate necessary checks.

For the source's clocks, a three-gate input basis and six-gate cut basis explain why the unretired prefix ending at event 353 can lead to a retired handoff ending at event 362. This is only a consistency observation. The actual event list, inclusive indexing, instruction ordering and absence of earlier field-34 contacts must be verified independently, not inferred from that arithmetic.

## Central phase and lambda return

The source assumes the exact global central operator q obeys `q squared=X`, where X is an ordinary phase-plus-one translation and `X squared=I`. Its lambda is

    lambda = ((1+i)I+(1-i)X)/2,
    lambda inverse = ((1-i)I+(1+i)X)/2.

Because q commutes with its square, these give `lambda squared=X`, `lambda lambda inverse=I`, `S=lambda q`, and `S squared=I`. Returning lambda inverse on the original completed S pivot produces exactly `q x_p`. The fresh field receives D and must receive neither this lambda inverse nor an additional S/q target. Returning lambda on the original normalization group must preserve the source's exact direction/convention and exclude the fresh field. The literal audit, not this lemma, settles which opcode implements lambda inverse.

The phase-plus-one premise is substantive: substituting an operator with `q squared=-X`, silently replacing X by I, or using one-column tensor-normalization identities would invalidate this derivation. At positive column multiplicity f the argument applies to the actual global q_f and its own square. It does not assert `S_f=(S_1) tensor f`, and it does not move exterior lambda coefficients inside a tensor power.

## What remains unverified

Neither `aP=S c` nor `Pd=S b`, nor the literal complete endpoint E, has been computed in this note. The earlier prose inspection checked only the displayed small ordinary G/J witness under target-first ADD. The actual main interface closure, common endpoint on fields 4/20/21, exact stage/central algebra, clock, complete suffix renaming, independent field-34 allocation and absence of native/helper/owned aliases remain obligations for the primary and independent literal audits.

Paid LOCAL calls, thin queries, idles, ordinary bases, returns and job chronology must still be accounted for under their actual unchanged contracts. The lemma supplies no free call, no productive copy, no reusable owned bank, no new primitive and no invoice. Source-native all-column correctness, owned erasure, compiler, precision/tape and analytic recovery remain quantified assumptions. The complete signed price, claimed kappa, compiler completion and outer bounds are outside this review. No selected-frontier or scientific-admission change follows.

Credit: thu-nmrc for the new source-specific witness and construction; PR6545 and the PR5599 lineage for the two-sided dual-pair method; DreamingOfClouds/PR6702 for the unchanged native source; Ali Romman/PR6348/PR6398 and Cinna Davis's retained query/controller lineage for the supplier and normalization framework. This is a separate written application audit using classical invertible linear algebra, with OpenAI Codex assistance, not a new general theorem or independent human review. Only this note was intentionally written; no source/package file was changed.


---

# Static implementation review: cut353 audit

Verdict: **no material correctness or acceptance defect found in the reviewed scope**. The implementations compute both cut vectors and every cell of the retired formal main-field endpoint by distinct propagation methods. This is conditional LOCAL-contract evidence, not a physical-address/owned-bank audit or complete source-price validation.

Read after root confirmed both blind firsts were sealed: package `research/p104-cut353-independent-audit/{verify.py,oracle.py}`, its six inert inputs, CASES/SCHEMA, and the two first RUN records. No checker, import, source generator, mutation or scientific program was executed by this reviewer; this note is the only intentional write.

## Methods and exact ring

Primary `verify.py:129–146,163–188,381–400` constructs the full 34-field prefix matrix chronologically, forms aP and Pd from that matrix, and separately propagates the full 35-field retired matrix. Oracle `oracle.py:161–217,248–299` instead pulls a backwards covector for aP, pushes a forwards vector for Pd, and pulls each of the 35 final output covectors independently. Its reverse routine is a row pullback, not a literal inverse program. This is the correct operation for obtaining aP.

Both implement exact rational-Gaussian coefficients and independent commuting stage exponents, reducing only the central exponent modulo four. The primary stores `(u,t1,...,t18)` in a 19-coordinate monomial; its shift by stage index accesses the corresponding stage coordinate, and serialization emits all 18 stage exponents. The source's 20-entry target convention is `(u,dummy,t1,...,t18)`. Both explicitly require the dummy coordinate to be zero and omit it when constructing expected monomials. There is no accidental stage-zero variable or conflation of stages 1 and 18. Neither engine substitutes stage samples or collapses u squared to one.

The stored central variable is source Q=u, whereas proof q=u inverse. Both therefore implement the normalized S as lambda(u squared) times u cubed. The oracle explicitly checks S squared=1, u to the fourth=1, S differing from bare u cubed, and u squared differing from one. This retains the exterior lambda phase rather than treating S as the one-column tensor power.

## Conditional LOCAL order

The inert `inputs/caller.py.txt` gives LOCAL(stage,src,dst) as a query `dst += u inverse src`, followed by the same fresh stage factor on both src and dst. Primary `verify.py:178–182` implements this exact chronological order. The oracle's forward column routine matches it; its backwards LOCAL step maps a row to `src := t_stage*(old_src+u inverse old_dst)` and `dst := t_stage*old_dst`, which is the correct pullback. ADD is target-first throughout both engines, consistent with the literal source and witness.

This reads the declared endpoint semantics of an abstract LOCAL event. Neither implementation reconstructs the source native word, its helpers, its actual physical maps or all-column realization. The distinction is explicit in the oracle docstring and CASES exclusions and must remain explicit in publication.

## Literal cut, fresh input and endpoint coverage

Primary `verify.py:322–338` checks the complete serialized surgery, including inverse input G, the inclusive source prefix through event 353, J, renamed J inverse and suffix, intervening normalizations, renamed final G and original-group return. It checks the source cut event itself and requires the first formal fresh-role contact to be event 363. Oracle `oracle.py:256–285` independently checks the first-contact boundary, the literal input-basis/prefix/J segment and six ordinary pairing/basis identities. Both compute all 34 entries of each cut vector, for **68 cut cells**, not 63.

Both derive the new expected target from the authenticated old diagonal declaration, replace old pivot 4 by bare u cubed, and append the stage-only target t10*t11*t12*t13 for field 34. All **1,225** final output/input cells are computed and checked, including every off-diagonal zero. The matrix basis supplies 35 formally independent arbitrary inputs, so this evidence does not assume a copied or zero fresh input. Primary also checks that the paid LOCAL-stage, QUERY-sign and idle-stage sequence is unchanged; this is not a complete physical price invoice.

One scope distinction matters: the authenticated unretired diagonal is a declared source endpoint; these routines do not independently recompute the entire unretired 34-by-34 final endpoint. They do recompute the full cut vectors and the entire changed 35-by-35 endpoint. The latter gives direct formal endpoint evidence even though the general surgery explanation also uses the old endpoint as an inherited premise.

Formal role 34 noncontact and consistent indexed renaming do not prove physical address disjointness from implicit LOCAL helper/owned banks. No actual ownership lifetime or common-idle physical noncontact is independently checked by these routines. This is correctly outside CASES. Avoid promoting this result into an audit of those premises.

## Rejection guards and controls

The primary authenticates metadata bytes, the six declared source hashes and source-path closure before computation. Its JSON loader rejects duplicate keys, booleans, floats and nonfinite numbers globally; recursive typed comparison checks the complete actual packet and retained receipt. The oracle authenticates exact frozen metadata/input hashes, source commit and Git blob identity. Its packet validator (`oracle.py:302–334`) enforces exact artifact keys/schema, dimensions, integer types excluding booleans, reduced positive-denominator Gaussian fractions, bounded exponents and strictly sorted unique nonzero monomials. It then compares the complete canonical artifact to its own recomputation, not merely an asserted packet hash.

The oracle loader (`oracle.py:48–56`) rejects duplicate keys and named nonfinite constants but does **not** globally reject finite floats during JSON parsing. I found no proof-relevant acceptance gap from this: every numeric packet field has an exact integer-type guard, all source inputs/metadata are byte-authenticated, and the entire receipt is compared as canonical JSON bytes to the recomputed object (`oracle.py:439–444`). Thus 1.0 or true cannot pass as integer 1 in either the packet or receipt. Nevertheless, the precise claim should be proof-relevant typed/canonical rejection, rather than saying the oracle loader itself globally rejects all floats. No execution was performed to demonstrate or alter this behavior.

Primary controls run three genuine source-word endpoint failures (query central sign, input G coefficient, extra fresh central factor), plus loader/type/pairing cases. The endpoint controls bypass the constructor equality guard and require the intended endpoint diagnostic. Oracle controls independently mutate the first query central sign and input basis coefficient, execute the actual reverse engine until it finds a nonzero wrong endpoint cell, and retain that witness. It also checks malformed fractions, duplicate/unsorted monomials and loader failures. These are meaningful semantic controls rather than solely digest rejection. They do not constitute a proof of arbitrary address-level/native mutations.

## Retained execution evidence and limits

I read, but did not recreate, the primary first RUN (19:59:36.374856–19:59:36.570176 UTC, exit 0, code SHA256 `882e13a044c22c37e2c93f048f70262b82fc16a8a0de7788ee9b39d38d8d21b7`) and oracle first RUN (19:59:44.985449–19:59:45.115717 UTC, exit 0, code SHA256 `348be3d563af88307198479ef843b414e0069f31a6752a58937e6aa7a709a211`). Both record Python 3.12.14, frozen metadata/input hashes, no peer-data read, empty stderr and completed artifacts. Their differing pretty/container artifact bytes are not a mathematical disagreement; root separately compares complete canonical packet values.

No request for a core change follows from this review. Publication should retain the conditional LOCAL boundary, the formal/physical distinction, the old endpoint declaration distinction, and the exact float-validation qualification above. Source author thu-nmrc and all PR6702/PR6348/PR6398/PR6545/PR5599 predecessor credit remain unchanged. This separate static AI review is neither formal proof-kernel certification nor independent human scientific acceptance.
