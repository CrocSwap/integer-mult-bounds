# Independent agent review: full-monomial two-FULL stability under dirty identity work

Status: **PASS for the stated written theorem**, subject to the source and scope premises below. This is a separate OpenAI Codex agent review with substantial AI assistance. It is not independent human review, proof-kernel acceptance, native scientific admission, a new multiplication exponent, or a physical consumer.

## Sources actually read and pinned

I read the complete #4920 proof, its separate full-routing grade proof, and its source manifest; the complete #4928 retained-helper proof, the independent review and its source manifests; and the current two-FULL contract map. The repository ref read was `a5df48c55ea806d7952b65acc9c76d878ff09b13`. `INDEPENDENT-SOURCE-READS.json` records exact Git blobs and SHA256 values of the seven proof/manifest inputs actually read.

- #4920: `research/two-full-central-obstruction/PROOF.md`, exact PR head `7eb4ef5251f7ba96c7e5d78c42fc98e66b7be4ba`, SHA256 `9babe77410543665f197cd1846d71d775d306c97716aedefc6f25f4256f5a699`. The main bytes read equal that PR-head proof byte-for-byte. Its separate `grade/PROOF.md` has SHA256 `8fd775a9903eca0f53b186d7fb684d9f5f74afc9c105082b3d4981bd950fca33`.
- #4928: `research/two-full-retained-helper-ceiling/science/PROOF.md`, exact PR head `6df6ed294614423836cbde182fb4368c9c346fe7`, SHA256 `63ec5034fb526dc9243de487f97477e51221773f4b7cae21b38df719ba1362c7`. The main bytes read equal that PR-head proof byte-for-byte. Its science source manifest has SHA256 `95e03830d931e2ac6843457a832a6f75c6227f85cae85d95095c65df7049c490`.

These sources bind the actual native source at `20bb93cd990d2ff683e4d0fc56b87a42cd5d3296`, and the dirty-helper protocol source #4712 at `b75a27bf07f1584b20babfddf887493981cd5949`. In particular the declared actual-word compressed SHA256 is `7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05`, Git blob `46d929df83817b85a5387bcdb9745e0627d6366e`. I read these pin declarations; this review does **not** claim to have rerun all eight native source checks or the full 632-field program. The predecessor native/main normalization is an inherited written premise here.

#4920's full-routing proof covered exactly two main owners. #4928 covered retained productive helpers under a separated address algebra. The proposed result is an extension of the former to restored dirty identity workspace. It does not combine the latter's transformed-helper permission with full routing.

## Statement reviewed

At a fixed sufficiently large tensor width, use the finite central-character twisted Clifford group algebra A over K, and its full monomial subgroup algebra B. All one-column matrices retain absolute phases. Let d=dim_K B. There are two main owners and s arbitrary dirty workspace owners, and each native call is `Tj=diag(Aj,I_s)`, where `Aj=diag(Djx,Djy) Ej`; each D has Fourier rank eight, and E is either triangular elementary shear with one pure central Clifford letter. The letters and D factors need not commute and may differ between calls. Arbitrary owner controls `L,W,R` lie in `GL_(s+2)(B)`.

The claimed target is `diag(g1,g2,I_s)` with each gj a single rank-seventeen Clifford word up to admitted monomial boundaries. No transformed helper output is supplied as identity workspace.

## Grade projection and arbitrary outer boundaries

Fourier rank is invariant under multiplication on either side by a monomial Clifford word. Consequently both projections

- rho: retain grades 1 through 16;
- Pi: retain grades 0 through 16

are B-bimodule maps, including in the phase-character twisted quotient. Neither is asserted to be an algebra homomorphism. Since rho kills both the rank-seventeen main targets and the grade-zero identity workspace, the target equation implies

    L rho(T2 W T1) R = 0.

Multiplying by the actual inverses of L and R is legitimate, even with arbitrary main/workspace mixing and zero divisors in B. Thus rho(T2 W T1)=0. This does not use a false assumption that L or R preserve the main/workspace block decomposition.

## Hand derivation for all four orientations

Use main indices 0,1. Let c be the input column untouched by E1, r the output row untouched by E2, and let j=1-c, i=1-r.

| E1 | E2 | c | r | j | i |
|---|---|---:|---:|---:|---:|
| upper | upper | 0 | 1 | 1 | 0 |
| upper | lower | 0 | 0 | 1 | 1 |
| lower | upper | 1 | 1 | 0 | 0 |
| lower | lower | 1 | 0 | 0 | 1 |

Write a for the first shear letter and b for the second; signs and orientations can be incorporated in those actual letters. For each scratch output/input index z, direct matrix multiplication, with no commutation, gives

    M_rz = D2r W_rz,
    M_iz = D2i W_iz + D2i b W_rz,
    M_zc = W_zc D1c,
    M_zj = W_zj D1j + W_zc D1c a.

The first and third expressions are supported purely in grade eight: each W entry is a sum of monomial words. Rho therefore retains them exactly. Their vanishing and the group-unit D factors imply `W_rz=W_zc=0`. The other two expressions then simplify to pure grade-eight terms, forcing `W_iz=W_zj=0`. This kills both cross blocks for every s and every orientation pair. It does not divide by a general B coefficient.

Hence W is block diagonal. Since W is invertible in the full matrix ring, both diagonal blocks Wmm and Wss are units: the corresponding diagonal blocks of an inverse give two-sided inverses. This step is valid over a noncommutative ring with zero divisors.

## Rank-domain audit and alternative proof

Before the intermediate-grade step, low-grade main entries need not lie in B. The final author proof now first establishes rho(M)=0 and explicitly concludes Pi(M)=pi_0(M), so its B-valued endomorphism rank argument is justified. The following more general K-linear formulation is an alternative proof, not a required correction to that final version: view the projected matrix as a map

    B^(s+2) -> A^(s+2),

not as a B-valued endomorphism of B^(s+2). This is sufficient. Right multiplication by R is an invertible map on the domain; left multiplication by L is an invertible map on the A-valued codomain, with its inverse still given by L^-1 over B. Both preserve K-linear rank.

After the cross blocks vanish,

    Pi(M) = diag(Pi(A2 Wmm A1), Wss).

The projected target has K-linear rank exactly s*d. The Wss block already has rank s*d on B^s. Its image and the main image occupy disjoint output coordinates, so additivity of rank forces the main projected block to have rank zero. Evaluating it on the two vectors with the unit of B in one coordinate shows that every main-low entry is zero. No semisimplicity, domain assumption, positivity or division by a zero divisor is needed.

The main-only #4920 contradiction now applies to Wmm. Its untouched corner is

    (A2 Wmm A1)_rc = D2r W_rc D1c.

Every word has grade at most 8+0+8=16, so Pi retains this corner and forces W_rc=0. The other entry in the same main input column becomes `D2i W_ic D1c`; it too is retained by Pi and vanishes. An entire column of Wmm is zero, contradicting that Wmm is a unit.

## Independent finite corroboration completed

`independent_symbolic.py` was written separately and imports neither another checker nor a Clifford implementation. It uses exact integer-coefficient noncommutative free words. Its default invocation is read-only and prints JSON to stdout. I ran

    python3.11 -I -B independent_symbolic.py
    python3.11 -I -O -B independent_symbolic.py

from this directory, retaining the externally redirected outputs as `INDEPENDENT-SYMBOLIC.json` and `INDEPENDENT-SYMBOLIC-OPTIMIZED.json`; they compare byte-for-byte. The twelve fixtures cover all four orientation pairs and s=1,2,3. They check 72 cross-row identities, 72 cross-column identities, scratch-block preservation, exact block-diagonal reduction, and 36 untouched-main-column formulas/zero substitutions. Noncommuting-order and incomplete-cross-zero controls discriminate the key algebraic shortcuts.

These fixtures corroborate symbolic matrix expansion only. They do not compute actual Clifford grades, exhaust arbitrary s, prove the B-bimodule assertion, prove tensor faithfulness, authenticate every native source, or establish scientific acceptance. Universal quantifiers come from the written argument above.

## Scope limits and unresolved obligations

- Dirty workspace must represent independent arbitrary inputs returned as the stated identity jobs, and all free global controls are invertible over B. A construction correct only at owned-zero entrances, rectangular COPY/DROP, noninvertible CLEAR, main-dependent garbage, or a nonidentity transformed workspace target requires another argument.
- Actual native helper targets, including already transformed helper states and copied producer-prefix observations, are not I_s. This theorem does not rule out a correctly charged changed producer/consumer using them.
- The same finite columnwise Clifford alphabet and its full monomial subgroup are retained. The separating tensor-power argument of #4920 supplies faithfulness for every sufficiently large width after the correct scalar-phase specialization. Arbitrary s, even depending on width, does not enlarge the address alphabet. A growing or noncolumnwise width-specific address grammar is outside that premise.
- The target main jobs must be pure rank-seventeen Clifford words. An approximate target, a sum-valued endpoint, a changed target invoice, extra interleaved nonmonomial work, or a different paid native source is outside the statement.
- No complete native caller, compiler reserve, precision propagation, outer transfer, BIT assembly, Lean kernel check, or new kappa was run or claimed.

The review finds no remaining mathematical blocker for the stated dirty-identity stabilization. It does not promote this scoped negative result to an obstruction for every intended research direction.

## Final author-proof addendum

I read the complete final author `PROOF.md` with SHA256 `99b3b4233891519fd741ea20cfe985c09bef576a94154e6b146db87f9b857200`. Its rank section explicitly uses rho(M)=0 to obtain Pi(Mm)=pi_0(Mm), and also derives Pi(M)=L^-1 P R^-1 in Mat(B). Therefore its regular-module endomorphism rank comparison on B^(s+2) is legitimate. This version resolves the rank-domain concern noted during the earlier draft review; there is no outstanding correction requested on that point. The B-domain to A-codomain argument above is retained as an independent alternative formulation. The final proof also preserves the actual noncommutative factor order, all four shear orientations, full outer mixing, and the stated identity-scratch scope. No new blocker was found on this final read.

## Final simultaneous-main-bank addendum

I read the complete repository proof at `/tmp/imb-frontier-20261023/research/two-full-dirty-stability/PROOF.md`, SHA256 `5c9331d51246ec9f3c6aabcb11b25eb6e438a3db4aee15cb61a9d24f55bfdf2f`. This is the final all-m version reviewed here, superseding the earlier two-owner-only author draft pin for the scope of this addendum. **PASS within its stated model:** no new mathematical blocker was found.

The same proof extends to every m>=1. Let C be the first stage's m untouched main input columns and U the second stage's m untouched main output rows; their complements contain the other m columns/rows. For each scratch index z, the U-to-scratch and scratch-to-C entries are pure grade eight, forcing `W[U,z]=W[z,C]=0`. The remaining cross entries are sums involving exactly those zeros plus a pure grade-eight term, so both complete cross blocks vanish. The prior rank argument then gives `Pi(Mmain)=0`. Its U-by-C corner is entrywise `B_r W[r,c] A_c`, entirely grade at most sixteen, forcing that corner of W to vanish. All other rows in the same C columns then become pure grade-at-most-sixteen terms, so those entire m columns vanish. This contradicts invertibility for any m>=1.

This direct argument allows different first/second partitions and pairings; it does not require a common port ordering, matching orientation, or commuting query entries. Each stage's disjoint directed pair shears can separately be relabelled by a free owner permutation. The two permutations are absorbed in the already arbitrary L/W/R; diagonal D factors are merely relabelled and retain rank eight. The author proof states the more general arbitrary partitions directly.

The arbitrary dense `Q1,Q2` blocks over A are a valid relaxation. No decoder or physically realizable query primitive is needed to prove this exclusion: the argument never evaluates the query entries, never commutes them past D, and removes every term containing them by a previously established W zero. Their square-zero off-diagonal block support alone ensures the relaxed shear factors remain units. Granting this larger query class strengthens the exclusion without introducing a positive supplier claim.

`independent_multipair.py` is a separate standard-library checker that imports no other checker. Its 36 exact noncommutative-freeword fixtures use m=1,2,3, scratch=0,1,2, all four global upper/lower orientation pairs, and genuinely dense independent query-letter matrices. They verify strict zero substitutions, whole cross-block reduction, unchanged Ws, pure untouched m-by-m corners, and whole m-column vanishing. Default execution only reads/compares `MULTIPAIR.json`; explicit `--write` is authoring. Normal and optimized runs pass with byte-identical reported output. The checker source SHA256 is `11a9bbf47358d14754fc48624bccb8a013a0c29212dfd7c16de81d5085c6076b`. The finite fixtures do not establish the universal quantifiers or independently prove actual Clifford grade invariance.

### Actual 112-port application and retained limits

The m=112 application is conditional on the inherited, already normalized actual source main interface: a simultaneous bank of 112 disjoint triangular main-pair maps with rank-eight pure Clifford diagonal factors, all represented in the same fixed 17-axis columnwise alphabet. It covers arbitrary joint L/W/R mixing of the full 224 original main owners and any identity dirty workspace. It is not a theorem about arbitrary access to all 632 native fields.

I additionally inspected the exact pinned predecessor `research/two-full-central-obstruction/independent/native-WRAPPERS.json` from main, Git blob `7d8ae034a093ddf590bd97e43aa548d7d744f18c`, SHA256 `bd3d02645c2bfc1fdb6c44a2484abf7269c26d5514c248168a0fa792c99d30ca`. It contains 112 port records and explicitly states that the 632-field source's helper outputs are autonomous, with its owned centers initialized, erased and uncredited inside each native invocation. Its records retain the per-port raw-D0 translation warning and exact shared-axis phase wrapper scope; no false commutation of raw D0 with central phase is needed in this proof.

These source records are inherited pins, not a new 632-column native replay. The source wrappers and all nonrecursive costs would still need to be implemented and charged by an actual caller. This obstruction neither consumes nor returns any productive helper as a freely usable state: helper operations remain external, autonomous and unavailable for mixing. A helper-prefix observation, changed producer, changed main target invoice, extra paid nonmonomial operation, noninvertible COPY/DROP/CLEAR controller, or a noncolumnwise/growing address grammar is outside the all-m theorem exactly as it was outside the identity-scratch theorem. No frontier value, selected result, or scientific acceptance is changed by this review.
