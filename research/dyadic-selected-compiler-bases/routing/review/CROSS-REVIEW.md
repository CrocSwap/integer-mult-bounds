# Independent review: finite dyadic route descriptors

**Decision: accept the scoped finite descriptor theorem and ledger.** No mathematical correction to the frozen author proof is required. This review concerns proof SHA256 `0fefb696f20f4e30ecf4f8ccefe564f70aaeee5498803877a8965e2534731e3d` and the 513-entry eight-dimensional catalogue SHA256 `fd605374cfeb851d3306e6e1778afffc51de508f32658a3d58c523bf066b5054`. No source factorization or author verifier is imported by the independent checker. This is separate model-assisted review, not external human or formal-kernel acceptance.

## 1. Exact accepted object

For each accepted complete image/kernel basis `B_P`, the catalogue fixes a same-rank reference `B_R` and emits an elementary word for

\[
S_P=B_P B_R^{-1}.
\]

Its operations and rational coefficients are fixed before the odd prime is chosen. Additions have dyadic coefficients; scale coefficients are units of `Z[1/2]`, namely signed powers of two; permutations are ordinary swaps. The exact word identities imply membership in `GL_8(Z[1/2])`. Therefore reduction of every operation and its inverse is defined over every odd prime-power ring. This eliminates q-dependent pivot selection for this catalogue without requiring an additional odd-prime exclusion list for these words.

The bases are the independently checked complete bases from the preceding dyadic-closure review, SHA256 `0ea69bbed0979ccbd8f9c2c53b6f74726281bb003c4707abc27fc3015e9c6975`. They include the full complementary kernel for each normalized nested difference. This review does not substitute a smaller frame kernel or arbitrary rational bases. The source native word and #7840 proof are authenticated at the pins in the receipt. The native semantic binding and admissible all-size closure theorem remain credited to the preceding package; the present contribution is the explicit finite routing word and its count/carry verification.

These are eight-dimensional routes for 513 fixed normalized catalogue differences, not a materialization of every larger matrix that a generated compiler may later use. The sixteen short pivot repairs are verified for this complete finite list; the search over coefficients `1,-1,2,-2` is not asserted to succeed for arbitrary dyadic invertible matrices. Enlarged compiler layouts and every resulting route require their own actual dimensions and expansions. No selected kappa or remaining machine/analytic assumption changes.

## 2. Elimination direction, pivots and lowering

The recorded elimination operations satisfy `E_k ... E_1 S^T=I`. Hence the column representation of a physical row transforms by

\[
S^T=E_1^{-1}\cdots E_k^{-1}.
\]

The forward chronological word is the reversed list of inverse operations; the inverse chronological word is the original elimination list. The independent checker reconstructs both matrices from the emitted words, and derives `S` directly from the accepted bases using a different exact inversion engine. It then separately expands upper additions and scale atoms and reconstructs both resulting endpoints again. 501 routes distinguish the correct chronology from using inverted operations in the unreversed order.

For an addition with target `i<j` and later source `j`, the legal lowering is `swap(i,j); add(j,i,c); swap(i,j)`. After the first swap the source value lies earlier, and the second swap restores the original coordinate roles. Every such lowering incurs two completed ordinary swaps; it is not a free relabeling. Original swaps are charged too. Every signed power-of-two scaling is expanded into atoms from `{-1,2,-2,1/2,-1/2}`, combining the sign with a factor when possible. Forward and inverse expansions have equal scale-atom and swap counts.

The checker witnesses every recorded short repair at its actual intermediate matrix. It verifies that no remaining dyadic-unit pivot exists before that repair, that the recorded two old entries match, and that their advertised linear combination is a unit. It finds all 16 repairs without rerunning the author's factorization search. Thus a correct final matrix is not the only evidence for those annotations.

A concrete rejection control uses pair `[11,266]`, rank three, referenced to `[2,270]`. A fixed-row elimination policy reaches the third pivot `3/4`, which becomes zero modulo three. The published word instead uses admissible swaps and unit scales. Rational nonsingularity does not justify division by the first available nonzero pivot at every odd prime.

The finite-only boundary is necessary even for unimodular integer matrices. The independent control `A=[[7,2],[17,5]]` has determinant one, but neither 7 nor 17 is a dyadic unit, and neither combination `7+c*17` nor `17+c*7` is a dyadic unit for `c in {1,-1,2,-2}`. This matrix defeats the advertised first-column short search. Identity extension embeds the same failure at dimension eight. The author already disclaims a universal short-repair rule; generated compiler nodes cannot inherit the measured catalogue counts.

## 3. Independent operation ledger

Each elementary row word is executed on all eight rows of the cover address matrix. Its low/high carry correction includes all 64 high coordinates, retaining zero slots in the conservative count. The maxima over the 513 catalogue entries, per directed route, are:

| Operation | Maximum |
| --- | ---: |
| Completed ordinary swaps, including both brackets of every upper addition | 472 |
| Ordered additions and all 64 carry translations | 496 |
| Fixed dyadic-unit scalings before expansion | 64 |
| Signed dyadic scaling atoms after expansion | 128 |

These maxima need not occur on the same entry. Across the entire catalogue in one direction, the totals are 89,088 ordinary swaps, 116,672 ordered additions/carry translations, 18,280 fixed scalings and 25,096 signed scaling atoms. Inverse routes are charged separately and have the same counts. A route between two arbitrary same-rank catalogue members composes the appropriate representative route and inverse route, so it incurs both component ledgers.

The counts describe full eight-row address operations. They do not price low selection/unselection, coefficient evaluation, record scans, scratch, tape motion, fresh stock or growing compiler dimensions. Those costs remain within the retained explicit physical contracts. The generic predecessor bounds for `N=8` are consistent with these smaller direct counts; the measured eight-dimensional maxima cannot be substituted for a later enlarged `N`.

## 4. Representative carries and complete coordinates

Let `g=g0+qX`, using fixed representatives for `g0 mod q`, and let `h0` be the representatives of `g0S mod q`. The only correct carry here is the exact localized rational matrix

\[
C_S(g_0)=\frac{g_0S-h_0}{q}.
\]

Each entry lies in `Z[1/2]`: after placing it over a power-of-two denominator, its numerator is divisible by the odd prime `q`. It need not be an ordinary integer. The physical address formula is `rho_S(g0,X)=(h0,XS+C_S(g0))`, reduced in the high cube modulo `q^(w-1)`. It reconstructs the same `gS mod q^w`. The complete matrix `S` acts separately on all eight high rows, and the carry translates all 64 high fields. Dropping high fields because only a smaller image rank is active would break this complete route.

Direct expansion gives

\[
C_{ST}(g_0)=C_S(g_0)T+C_T(h_0).
\]

Thus the inverse carry is transported by `S^{-1}`; merely negating an untransported carry is not valid. The inverse recomputes the correct low representatives and restores the entire high matrix. At `w=1` the high cube is a singleton. Its coordinate transformations are identities and may be omitted; a physical caller must branch around zero-width high primitives as the author states.

The independent scalar witness `S=1/2,q=3,g0=1,X=1,w=2` has `h0=2` and carry `-1/2`. Correct reconstruction yields 2 modulo nine. Omitting the carry yields 8; flooring it to -1 yields 5. This checks the distinction between q-integrality and ordinary integer carry. Reduction at prime two is explicitly rejected.

Each complete route is a bijection of the full fresh-address cube and leaves independently adjoined coordinates fixed. Therefore opaque payload and exterior spectators are preserved under this address permutation. Turning that mathematical identity into machine transport relies on the called complete-record primitive contracts; it does not erase private buffers, prove owner restoration by itself, or establish a fresh-stock supplier. The common-route requirement for coupled scalar contacts in #7840 also remains necessary. A family of individually correct route matrices does not authorize different routes on coupled roles.

## 5. Signed scaling interface and credit

I read the retained #5052 proof at SHA256 `f53db166a3bc3865c08426cf520b402028e34e1e9da2262ae19afa0b157a1c55`, pinned by the author to JoyboyBrian's head `02a3cedb301e072bc5d991c7e36086daa8cd5c40`. Its contract is a supplied complete Boolean stream in lexicographic `[P] x [Q] x [S]` order, with positive descriptor extents and odd `Q`. It gives five signed scale coefficients, original physical owner return, preserved descriptors and spectators, and restoration of the assigned initially blank private tapes. `Q=1` is included. The arbitrary full-route address packet is not automatically already in this representation.

The quoted `2048 V_j` transition and `64 V_j` visited-space bounds are the source's stated sufficient allowances, not measured maxima of this route review. Once each complete stream and ownership interface is supplied, summing transitions over scale sites and reusing the restored private regions gives scaling-only charges `2048 sum_j V_j` and `64 max_j V_j`. At a common site volume `V`, 128 scale atoms permit `262144 V` transitions. These arithmetic substitutions are correct. They do not include the route's other operation classes, descriptor generation or caller representation conversion.

The independent checker also verifies the underlying doubling bucket/interleave identity and inverse on complete opaque records for 16 small odd-modulus cases, including modulus one. That is algebraic corroboration, not a new execution of #5052's fourteen-tape transition table or an independent audit of its entire instruction ledger. Physical original-owner and blank-workspace restoration are inherited source contracts here.

Credit remains with #7840 for full-GL routing, representative carry, common-route semantics and the N-dependent interface; #8092's dyadic-basis package for complete localized bases and closure; #5052 for the complete signed-scale machine; and #6950 for the hidden ordinary-swap accounting boundary. The author distinguishes #6954 and #7092 rather than claiming a universal short-factorization result. This review accepts that limited novelty statement and does not establish exhaustive novelty across unrelated work.

## 6. Executed evidence and independence

The independent `independent.py` imports only Python's standard library. It does not import or run `route_words.py`, `verify_routes.py`, the preceding lattice engine, or any author scientific code. It authenticates the frozen proof, exact catalogue, complete bases, compressed native data and retained proofs before and after execution. It reads source data and interprets the emitted descriptors with its own Fraction arithmetic, inverse elimination, operation expansion and modular reduction.

Normal and optimized runs check:

- All 513 route and inverse matrices and both lowered words, with 16 witnessed short repairs and 501 reversed-chronology rejection witnesses.
- The raw 636-frame reconstruction, all 2,380 distinct MOVE/helper endpoint pairs, exact equality with the 513 accepted normalized differences, and all 135 differences that are not raw frame projectors. Each accepted basis satisfies the source image/full-kernel identity.
- 6,156 complete low/high matrix fixtures at `q=3,5,7,11`, `w=1,2,3`, covering 393,984 individual high-address coordinates and inverse restoration. Of these, 2,052 are the `w=1` singleton cases.
- 2,052 exact localized carry cocycle identities. There are 1,952 fixtures with a noninteger localized carry and 1,964 with a nonzero carry among the distinct route/prime pairs.
- 2,060 complete opaque records in 16 small scale-modulus cases, including singleton moduli.
- Explicit controls for incorrect carry, forbidden prime two, the actual nonunit fixed pivot, reversed chronology and the unimodular matrix outside the finite short-repair scope.

The matrix fixtures do not exhaust `GL_8` or the full `q^(64(w-1))` high cube. Universal q,w and arbitrary-record correctness follows from the exact word identities, localized carry calculation and coordinate bijections; finite fixtures detect binding and interpretation errors. The author's separate exhaustive one-row and opaque-record evidence is recorded in its own receipt and is not counted as an independent reviewer execution.

From this review directory, `SOURCE` is the directory containing the frozen author proof, catalogue and retained inputs:

```sh
python3 -W error -I -B independent.py --source "$SOURCE" --output EVIDENCE.json
python3 -W error -I -O -B independent.py --source "$SOURCE" --output EVIDENCE-OPTIMIZED.json
```

Every rejection uses an explicit exception and remains active under optimized Python. The completion receipt records equality of all proof-relevant result fields after removing only elapsed seconds.

## 7. Integration and remaining premises

Integrate this scoped descriptor/carry appendix into the existing dyadic package in #8092, preserving the preceding proof and source credits. Do not publish a second copy of the earlier dyadic-closure theorem merely to attach this review. The new finite words and independent evidence are the material increment.

Generated compiler matrices may be much larger and have different elimination words, coefficient heights, ordinary-swap counts and scale expansions. Dyadic closure guarantees that suitable arithmetic is defined at every odd prime; it does not bound an arbitrary factorization by 472/496/64. The unimodular short-search counterexample makes this boundary concrete. The actual source's general q-dependent route construction keeps its separate, actual-dimension interface unless another q-independent construction is proved and charged.

Outer prime-size and fine-prime hypotheses also remain. Testing arithmetic at q=3 demonstrates valid reduction of these dyadic identities, not permission to use q=3 in a caller that requires `q>2^45 N^5` or stronger analytic conditions. No ownership, nonzero erasure, tape precision, complete stock supplier or analytic recovery premise is discharged by the finite word ledger. Scale-only transition constants are not a total route runtime.

The next concrete interface is installation of the descriptors and complete scale streams in an actual recursive owner bank, with charged low selection, carry generation, ordered shifts, previous-stage ordinary swaps and output restoration. That work must retain whole-record payload and spectator identity and the coupled-role common-route condition. The author proof correctly leaves these tasks open.

Review completed 2026-11-23 UTC by a separate OpenAI agent for Jerry Chen / @CubeJerry. The accepted result is a finite exact construction with a universal odd-prime-power interpretation, not a complete physical multiplier.
