> Current evidence: independent conditional paper acceptance at the scope in [REVIEW.md](REVIEW.md). Historical author/pending labels below describe the frozen submission; imported predecessor hypotheses remain explicit.

# Reversed two-stage boundary bases: a width-39 data block

Author-paper increment, 8 October 2026. Prepared with substantial OpenAI assistance. Independent mathematical review and exact-byte acceptance are separate requirements.

## Result, scope and attribution

Instantiate the retained two-stage construction with first factor a=45 and second factor b=47, instead of the opposite order. The finite producer graphs are the same two graphs used by Dominik Scholz's PR33; their stages are interchanged. A new common controlled rational basis gives every data macro the profile

9 singleton children, and children of widths 43, 39 and 1933.

This replaces PR33's 11 singleton children and widths 43, 37 and 1933. No numerical exponent is claimed in this geometric lemma. The total role count, rank mass, maximum child, paid rank-one correction, and the multiset of all other child widths are unchanged. An independently checked assembly may consume this exact profile change.

The two-stage topology and paid correction are Aurel Prosz/Paureel's construction, adopted in Zhihao Chen/jacklightChen's PR29 after the development route credited to Swapnil Jain. The positive retained-total producers and controlled common-basis framework come from icekylinx's PR18/24 and earlier contributors. Rohan Arun's PR31 supplies the earlier two-block refinement and incidence rank-partition method. Dominik Scholz's PR33 supplies the selected 47/45 producer specialization and its 43/37 refinement. The retained semantic/bulk interfaces are Zhihao Chen's PR21/23 and RaD/hipotures PR20. Preserve eumemic, Douglas Colkitt, OpenAI, Harvey–van der Hoeven, all other dependency credits, notices and applicable licenses. The new contribution here is the reversed-order boundary family, its explicit uniform rank cuts, and its width-39 specialization. No worldwide priority, global optimum, practical speedup, or unconditional multiplication theorem is claimed.

The fixed finite-alphabet and fixed finite number of one-dimensional tapes, analytic recovery, Gaussian inverse, semantic precision, row stock, complete spectators, routing, bulk implementation, exact recovery and finite constructive preparation remain inherited hypotheses. This is not formal verification.

Pinned sources, independently checked as Git blobs and retained read-only:

- PR29, jacklightChen/integer-mult-bounds commit 9d963275075fa98f1da821e27757b238dafd6b3c, notes/two-stage-16-note.tex, blob f11e830cc7d72efa7da436e4a871521a97ff4097, local pinned/pr29-two-stage-note.tex.
- PR31, rohanarun/integer-mult-bounds commit 02f68f95369c39955c5ffcfddbd75cd83e26b305, notes/two-stage-corners-note.tex, blob 3034d36397b9d1c4aa7ac9f41e7ed72b03172097, local pinned/pr31-corners-note.tex.
- PR33, DominikScholz/integer-mult-bounds commit e0399d0e1a222bebf72e44ad374004bbcb7f2c64, notes/two-stage-47-45-note.tex, blob bb674d91902e6167d84858dcc45728ed45ae1f5f, local pinned/pr33-two-stage-47-45-note.tex.
- The same PR33 commit, notes/two-stage-corners-47-45-note.tex, blob 8f5c6685a1de319769ec336e8043fdabd2f4ed84, local pinned/pr33-corners-47-45-note.tex.

## 1. A compatible reversed boundary family

The structural argument is uniform for integers h≥7. Put a=h, b=h+2, m=ab and d=a+b−1=2h+1. Physical coordinates have index i=bα+β, with β fastest. Use the inherited controlled family

K=T₂(I_a⊗L_b), with T₂(u⊗e_β)=M_βL_a u⊗e_β,

where L_a and L_b remain arbitrary invertible rational matrices. Prescribe the first d row coefficient labels and last d inverse-column coefficient labels to be

R=[0,…,h−1; h−1; 0,…,h−1],
C=[0,…,h−1; 0; 0,…,h−1].

A row label r means e_αᵀM_β=e_rᵀ. An inverse-column label c means M_β⁻¹e_α=e_c, equivalently M_βe_c=e_α. Row residues are β_i=i mod b. Since m−d=h²−1≡3 mod(h+2), column residues are γ_j=(j+3) mod b.

All prescribed physical rows are in α=0,1. All prescribed physical inverse columns are in α=h−2,h−1. These physical positions are disjoint for h≥7. At a fixed β, the prescribed coefficient labels are also disjoint. The complete lists are:

- β=0: row labels {0,1}, column labels {h−1}
- β=1: row labels {1,2}, column labels {0}
- β=2: row labels {2,3}, column labels {0}
- 3≤β≤h−2: row labels {β,β+1}, column labels {β−3,β−2}
- β=h−1: row labels {h−1}, column labels {h−4,h−3}
- β=h: row labels {h−1}, column labels {h−3,h−2}
- β=h+1: row labels {0}, column labels {h−2,h−1}.

Thus each M_β has a permutation completion. Fix any such completion. This leaves the same irreducible free GL_a×GL_b rational family needed for simultaneous nonvanishing. The certificates give explicit permutations at h=45 and h=53.

Absorb L_a,L_b into local line projectors pξ,vν, with ξp=νv=1. The inherited direct contraction formulas apply:

(A⊗vν)ᵢⱼ=v_{β_i}ν_{γ_j}A_{R_i,C_j},
(pξ⊗B)ᵢⱼ=p_{R_i}ξ_{C_j}B_{β_i,γ_j}.

On the first a rows and last a columns, the coefficient labels are both 0,…,a−1 in the same order. Every axis-a local projector is therefore represented up to nonzero diagonal scalings; I_a gives an invertible diagonal corner. On the first b rows and last b columns, the residues are both 0,…,b−1 in the same order. Every axis-b local projector is represented up to nonzero diagonal scalings; I_b likewise gives a diagonal corner. The repeated coefficient labels at these latter boundaries cause no problem: only their line evaluations must be nonzero.

Consequently both auxiliary profiles (a,m−2a) and (b,m−2b), every inherited ordinary local projector profile, and both physical growth profiles are retained in one family. This statement uses the actual physical order; it does not gather or reverse any pivot interval.

## 2. The normalized data corner and incidence bound

The data residual is (I−pξ)⊗(I−vν), with nullity d. Its normalized null corner is

Mᵢⱼ = x_{R_i}[R_i=C_j] + y_{β_i}[β_i=γ_j] − 1,

where x_r=(p_rξ_r)⁻¹, y_s=(v_sν_s)⁻¹. The normalizations are Σ_r1/x_r=Σ_s1/y_s=1. Dividing the actual corner by nonzero row and column factors, and its overall sign, does not change pivot positions or zeros.

Let F_i=(e_{R_i},e_{β_i},1) and G_j=(e_{C_j},e_{γ_j},1). Then M=F diag(x,y,−1)Gᵀ. For any selected coefficient set S, initial row interval U and terminal column interval V,

rank M[U,V] ≤ rank F[U,S] + rank G[V,Sᶜ]. (1)

This is the standard partition identity used in PR31: split the diagonal product into its S and Sᶜ parts, and bound each product by one factor. It holds for every choice of weights, so all upper zeros below are identities.

Ignoring the constant column, F and G are bipartite tree incidence matrices. For any forest and selected vertex columns S, their rank is the sum over nontrivial components T of min(|S∩T|,|T|−1). Indeed signing one color class converts to oriented incidence, and a tree has exactly one full-support dependence among all vertex columns. The constant column increases this rank by one exactly when some component has omitted vertices on both color classes. To prove the last assertion, a constant edge value one requires z_left+z_right=1; on a tree this has z_left=t and z_right=1−t. Coordinates omitted on both colors make such a representation impossible, and otherwise an appropriate t exists componentwise.

## 3. Uniform upper-rank proof of the two runs

Consider the following proposed rightmost-pivot permutation π:

- π(0)=2h
- π(i)=i+h+1 for 1≤i≤h−2
- π(i)=2h−i for h−1≤i≤h+4
- π(i)=i−h−3 for h+5≤i≤2h−2
- π(2h−1)=1 and π(2h)=0.

For each i take U=[0,i] and V=[π(i)+1,2h]. We need rank M[U,V] no larger than the number of earlier pivots strictly to the right of π(i).

On the first increasing run choose S to contain all first-factor labels greater than i, all second-factor labels greater than i, and the constant. The row restriction has rank one, coming only from the constant. All columns of G on Sᶜ vanish, since V lies in the final coefficient-label block and its residues are two greater than those labels. Equation (1) gives rank at most one, exactly the number of earlier rightward pivots.

On the second increasing run write i=h+5+t, π(i)=2+t, with 0≤t≤h−7. Choose

S_left=[3+t,h−1], S_right=[5+t,h+1], and exclude the constant.

The row-prefix forest has one component with red vertices 0,…,t+4, blue vertices 0,…,t+4 and the additional blue vertex h+1. Exactly three selected vertex columns occur there, giving rank three. Its end component {red h−1, blue h−1, blue h} is wholly selected and contributes two. The remaining h−t−6 components are wholly selected isolated edges, contributing h−t−6. Therefore

rank F[U,S] = h−1−t.

The column-suffix forest has one component with red vertices t+3,…,h−1, blue vertices t+5,…,h+1 and blue vertex 0. Only blue vertex 0 is selected by Sᶜ there, giving rank one. The component {red 0, blue 1, blue 2} is wholly selected and contributes two. The remaining t+2 isolated-edge components are wholly selected and contribute t+2. Since the first component omits vertices on both colors, the constant column, which belongs to Sᶜ, adds one. Thus

rank G[V,Sᶜ] = 6+t.

Their sum is h+5. Exactly h+5 earlier pivots lie strictly right of 2+t. This proves the desired upper bound uniformly in all weights and throughout the complete family. Outside the two runs, every column in V is already a pivot column, so the number of columns alone gives the required bound.

## 4. Exact nonvanishing at the selected dimensions

The preceding rank cuts are uniform in h, but they alone do not assert nonzero pivots for every h. For the selected cases h=45 and h=53, use the exact rational line coordinates

p_r=v_s=1,
ξ_r=(r+1)² / Σ_{j=1}^{a}j²,
ν_s=(s+1)³ / Σ_{j=1}^{b}j³.

Every coordinate is nonzero and both rank-one normalizations hold. The standard-library checker certify_reversed.py constructs the normalized corner with Fraction arithmetic and performs exact rightmost elimination. REVERSED_45_CERTIFICATE.json records all 91 nonzero pivot values, and REVERSED_53_CERTIFICATE.json records all 107. The checker also constructs every permutation completion, checks every prescribed row and inverse column, and verifies all initial-row/terminal-column rank cuts by the forest rule. No floating-point estimate or modular sample certifies this conclusion; no supplier code is executed.

Equivalently, each initial-row minor on columns {π(0),…,π(i)} is nonzero at the displayed specialization. Induction combines this with the uniform rank upper bounds: the bounds forbid a residual entry right of π(i), and the nonzero minor forces a nonzero pivot at π(i).

Any fixed rational rank-one projector is conjugate to the displayed normalized pair by GL_a, independently by GL_b for the second factor. Thus, for each actual data pair, these minors are nonzero rational functions on the free GL_a×GL_b family. All ordinary, auxiliary and line-coordinate requirements are also individually nonzero there, by the retained ordinary-projector argument. After clearing denominators, their finite product is nonzero on this irreducible family. One rational pair of bases meets every condition simultaneously. The displayed witness need not itself work for every physical data pair. Finite rational enumeration and the inherited eligible-prime selection remain valid.

## 5. Physical children and exact transfer

The first run has h−2 rows and h−2 equally ordered consecutive columns. The second has h−6 rows and h−6 equally ordered consecutive columns. The other nine corner pivots are singletons. The large-projector Schur identity leaves the untouched central identity of width m−2d=h²−2h−2. Its rank and the corner ranks add to

9+(h−2)+(h−6)+(m−2d)=m−d=(a−1)(b−1).

At h=45, the width-43 block uses rows 1,…,43 and physical columns 2071,…,2113. The width-39 block uses rows 50,…,88 and physical columns 2026,…,2064. The central width-1933 block uses rows/columns 91,…,2023. These are disjoint intervals in the inherited order. The exact lower-triangular partial-swap conjugation from PR18/24/29 converts each increasing run to one child interchange. Diagonal factors are absorbed in its allowed triangular wrappers. No free gathering, transpose, reversal or boundary adapter is introduced.

The change from 47/45 to 45/47 instantiates the two-stage topology with the same two producer graphs in the other order; it does not physically transpose a completed stream. The topology's proof uses only the first-factor producer, second-factor producer and their common rank-one line interfaces. Its framed output equations and rank-one copy correction are valid for either dimension order. If N=v_av_b, the role count is the symmetric expression 2N+v_bR_a+v_aR_b. Each axis-h ordinary histogram is replicated by the other axis's v. Its auxiliary contribution is (h,m−2h), replicated by R_h times that v; the physical growth profile is the ordinary rank-(h−1) profile, replicated by 2N. These complete multisets do not change when the axes are interchanged. The two-stage data residual and N paid rank-one corrections are likewise unchanged in multiplicity and rank.

There are 2N data macros. Relative to PR33, remove 4N singleton calls and 2N width-37 calls, and add 2N width-39 calls. The total rank change is 2N(39−37−2)=0. For every τ in (0,1), the moment numerator strictly decreases by

2N(39^τ−37^τ−2)<0,

because x↦x^τ has derivative strictly below one for x≥1. This is a strict whole-interval comparison, not a comparison of two sampled moments. Maximum child and W are unchanged, so inherited bit halving depths, complete-row/spectator contracts and nested stock bounds persist. All exact arithmetic, any chosen new saving, and final analytic assembly are separate explicit certificates.

## Reproduction and verification boundary

Run python certify_reversed.py for h=45. The optional --h 53 --output REVERSED_53_CERTIFICATE.json reconstructs the original discovery dimension. All certificate arithmetic is exact; the elapsed-time display is operational metadata only. Independent review should check the written finite-family and physical-transfer arguments, not merely matching checker output. The exploratory cyclic/modular searches are not proof dependencies and need not be published.
