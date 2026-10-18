# Selected BIT calls on complete local-ring packets

We prove an exact-stream integration statement for the selected PR589 word and
an explicit sufficient row layout. We assume completed address callees with
the spectator, restoration and work contracts below. We do not prove their
recursive implementation cost or admit a new exponent.

## Domain and conclusion

Fix an odd prime q, w >= 1, R = Z/q^w and m = 64. A payload is an arbitrary
Boolean function of two complete address blocks and complete spectators.
We compute payload XOR over F2; we use R only for addresses. At a given
recursive node, fix a diagonal unit matrix A whose entries depend on exposed
ancestor fields, but not on this node's family, cover coordinates or unused
descendant row field. We may fix each ancestor tuple separately in the proof.

Use the pinned 288 call descriptors and both literal local programs, the
fixed data charts rho, and the helper completions in section 3. For each low
cover class, execute the whole local word on its complete high packet before
advancing to the next low class. Use fresh private work and the literal
transported-source ERASE guards. Assume that address callees act on the whole
specified packet, preserve its complete spectators, restore row coordinates
and close their work before returning.

Under these hypotheses we obtain the selected local endpoints and chronological
hosting identity over GL64(R), on arbitrary correlated dirty payloads. After
the global bridges, idle remainders and terminal stream exchange, we obtain
the full weighted reversed interchange on each live family. We also give a
restricted-fibre XOR procedure and a compatible row divisor for these calls.
We retain their stated scan, route and workspace charges.

We reuse alephnan's PR1627 literal replay and chronological proof. Eumemic
already gave a whole-owner GL local-ring argument in PR490. Our contribution
binds that domain to the selected literal word, distinguishes point owners
from complete-packet owners, supplies a selected live-row layout, and gives
physical restricted-fibre and wrong-geometry controls. We make no novelty
claim for generic conjugation or the common-label induction.

## 1. Split projectors over R

For a projector P on the head block and the fixed reversal C on the tail,
write

    D_C(P) = [[I-P, P C], [C P, I-C P C]].

We need P^2=P, without a symmetry requirement. Multiplication gives
D_C(P)^2=I. For nested projectors PQ=QP=P, multiplication gives
D_C(P) D_C(Q)=D_C(Q-P). For disjoint commuting projectors, it gives
D_C(P) D_C(Q)=D_C(P+Q). Conjugate by diag(A,I) to obtain the weighted maps.
For a variable g in GL64(R), conjugate P by g P g^-1. Use the inverse of g;
its transpose generally differs.

PR1627 reconstructs the 636 rational frame projectors from the selected root
lines, and checks exact idempotence, nesting and dyadic final entries. These
identities hold in Z[1/2], so we specialize them to R. For a rank-r rational
idempotent, the characteristic polynomial equals T^(m-r)(T-1)^r in Z[1/2].
After reduction modulo q, diagonalizability of an idempotent gives rank r.
We do not infer rank from the trace modulo q.

Choose r independent columns of P and m-r independent columns of I-P modulo
q. Lift those same columns to R and concatenate them into T. The determinant
of T is a unit because its reduction is invertible. The equations
PT=T diag(I_r,0) then give P=T diag(I_r,0) T^-1. This proves split rank r
over R, including q dividing r. We apply the argument to frame projectors,
their nested differences and the ambient stage embeddings.

For completeness, write P=B V with V B=I_r. Then

    D_C(P)-I = [-B; C B] [V, -V C].

The first factor has left inverse [-V,0], and the second has right inverse
[B;0]. Thus the address residual has split rank r. Unit conjugation preserves
this factorization and rank.

We check 636 frames and 531 distinct residuals over Z/9, Z/25, Z/49 and
Z/27: 4,668 exact image/kernel bases, including 760 positive ranks divisible
by q. These finite checks audit the specialization argument; the argument
above covers arbitrary odd q and w.

## 2. The selected local word and its rank-seven guards

For the common invocation d, give each logical role the address label

    Gamma = Q_A Q_d D_C(P_frame + E_s) Q_d^-1 Q_A^-1,
    Q_A = diag(A,I),  Q_d = diag(d,C d C).

For the reflected orientation replace the local P_frame by I_8-P_frame.
The exterior E_s occupies the first s seven-coordinate blocks. A MOVE from
label Gamma_a to Gamma_b uses Gamma_a Gamma_b^-1. An ADD between equal
labels performs XOR at the common address. COPY creates a private copy with
the relative transport. Equality of the decoded temporary and source implies

    f_temp = f_source composed with Gamma_source Gamma_temp^-1,

which is the physical ERASE guard. Bijectivity equates zero decoded and zero
physical payload. Apply induction to the literal chronological events, using
the owner separation from section 3 to exclude indirect writes to a source.

The imported PR1627 replay propagates all 661 initial Boolean columns through
both 27,234-event programs, checks centre immutability and the nine literal
COPY/ERASE episodes per orientation, and returns x'=x, y'=y+x, h'=h in local
role order. Arbitrary substitutions for those columns allow correlated
payloads. Each event acts separately at each high cover coordinate after
owner alignment, so the same induction applies to a complete high packet.

The source copies frames 510 through 518 to frame 0. Their relative swap has
rank seven in both orientations; the common E_s cancels. We check weighted
transport for the actual frame pairs and twelve ambient 64-dimensional COPY
cases, including charts that mix local and exterior axes. We reuse PR1627's
literal guard checks rather than treating a rank number as an ERASE proof.

## 3. Complete owner packets and chronological sweeps

Let F_d0 = {d0 + q G : G in [q^(w-1)]^(64*64)} for a fixed invertible low
matrix d0. A matrix over R is invertible exactly when its reduction is.
For a fixed unit chart sigma, right multiplication is a bijection

    F_d0 sigma^-1 = F_(d0 sigma_bar^-1).

The bijection includes the carries in the chosen low/high representation.
At one low invocation, two helpers in the same family therefore have
disjoint complete packets precisely when their owner low classes differ.

For port p let A_p be the retained dyadic orthogonal family chart. For a
hosted support S of size eight, start from D={0,...,7}. Pair the sorted sets
D\S and S\D and exchange each pair of axes, obtaining pi_S. If S meets D,
set sigma_S=A_p pi_S; otherwise set sigma_S=pi_S. This is the support
completion used in PR2157. It has image A_p E_S on the local block, since
A_p is the identity on exterior axes. Its full basis order need not match
PR1627's completion: the full local endpoint depends on this image projector.

Within a selected call, the supports of two helpers in the same family are
disjoint. Their images remain nonzero disjoint subspaces modulo each odd q,
because A_p is invertible there. Hence their chart reductions differ. Left
multiplication by d0 preserves that difference, proving complete-packet
separation. The 222 data families are distinct and outside the helper
families. The private family lies outside the live inventory.

We check the prescribed images of 124 completion types and the supports of
181,056 same-family pairs across 288 calls. The selected word includes
11,072 same-family ADDs across these calls. For example, stage 0, replica 0,
event 19422 adds role 244 into role 243 in family 451, on supports 9..16 and
1..8. A whole-family XOR would act on more than the specified owned packet.

Finish the whole word for a low class before the next class. Distinct low
invocations may reuse a physical packet through different roles. The local
endpoint theorem accepts its current arbitrary dirty value, so this reuse
does not require fresh or independent inputs. We reduce complete calls to
their endpoints before commuting any hosted residuals.

For each fixed slot, d -> d sigma^-1 permutes the full GL64(R) cover. Thus
one full sweep places that slot's residual once on each physical class.
For a fixed family and physical g, the images g A_p E_S A_p^-1 g^-1 of
disjoint supports are commuting disjoint idempotents. PR1627 checks the
selected untouched intervals between a slot's host stage and its nominated
idle child. Its chronological argument therefore applies in these charts:
move the completed slot endpoints inside those intervals, then multiply
them with the exact remainder to recover each full idle child.

We also replay the global eight-role Boolean schedule, including its eighteen
bridge shears and terminal pair exchange. It returns the identity on decoded
data. The terminal exchange moves frame labels with stream values. On an
original source family the entry projector is the port line P and the final
projector is I-P; on the other family the endpoints are 0 and I. Their
relative operators give the full F_A. We check the 111 weighted ambient
source endpoints and the 888 data-chart boundary cases over Z/9 and Z/25.
For f-atom blocks, tensor these identities with I_f and retain the specified
tail reversal convention. We do not charge a new full-tail pass for a
coordinate convention, or assert that an actual required pass would be free.

## 4. Restricted-fibre XOR and its cost

The stream model in `upstream/build/sections/02-streams.tex`, lines 24-26,
60-96 and 98-118, permits fixed selectors, split/merge passes and work
copies, with charges for scans, counters, rewinds and erasure. At fixed q
there are finitely many low classes. Use the following procedure for a
same-family ADD on two distinct owned low packets:

1. Scan the family and copy the target and source packets to work streams.
2. Align both complete high fibres to d=g sigma and XOR them there.
3. Invert the target alignment. Scan the original family and replace only
   its target packet, copying the other packets unchanged.
4. Erase the fresh work copies and reset their heads.

Keep the original source intact. Its work copy needs no inverse route before
erasure. With packet volume V_f and whole-family volume V_F, charge

    C_select(q) V_F + T_target(V_f,w) + T_source(V_f,w)
                   + T_target_return(V_f,w) + C_XOR V_f.

There are three route actions. An invocation over every low class multiplies
the finite q-dependent constant; it does not introduce a loop of scans over
the growing high-cardinality set. The fixed-route lowering in PR2157 can
implement each route under its completed ordinary-callee and preparation
contracts. Its cost must enter the selected numerical invoice before use in
an admitted bound. PR490 likewise retained a separate B_GL allowance.

Our physical fixture executes this procedure on the full GL2(Z/9) family:
3,888 rows, three unused classes per row, seventeen payload bits per class.
It performs two full-family scans and two ordered high shifts on 198,288
bits. The target and return charts are identity in this fixture; the source
chart is [[1,1],[0,1]]. It needs no ordinary callee. The independent oracle
uses full-ring matrix multiplication, and we compare the whole payload,
including the 47 unowned low-class packets. Omitting a carry changes the
payload. The meter counts payload reads, writes, head movement and erasure;
it does not measure Python controller arithmetic or certify all selected
64-dimensional routes.

## 5. An explicit live-row layout compatible with the physical count

The selected emitter counts W=28,416 live families and P=W+9=28,425 physical
slots. Its private COPY register starts at zero; the copied-centres lemma
uses a work stream with the same logical volume as its source. We must
allocate and charge that work separately. We cannot clear arbitrary input
rows merely by assigning them a private-slot label.

Keep w fixed down the coarse recursion. Set N=|GL64(F_q)|,
H=q^(4096(w-1)), and

    M=lcm(W,P)=269241600,  K=M N H,
    D(n)=0 for n<64;  D(n)=1+D(42 floor(n/64)) otherwise,
    S(n,w)=K^D(n).

At an internal node take a row count R_rows=t S(n,w). Decode its complete
range as

    [W] x [N] x [H] x [U],
    U=R_rows/(W N H)=t * 9475 * K^(D(n)-1).

All original rows carry live payload. Allocate the private and selector work
streams outside this coordinate split, with the complete packet shape of
their sources. A fixed family and low class has exact logical volume
V/(W N), since we retain all H high coordinates and all U unused rows.

For a child of width r floor(n/64), 1<=r<=42, monotonicity of D gives
D_child<=D(n)-1. Fallback children of width at most floor(n/64) obey the
same inequality. Thus K^D_child divides U. For each fixed parent high
matrix, the child receives an identical complete fresh row range inside U;
parent high coordinates and inactive atoms become complete spectators.
After k active levels the unused count is t * 9475^k * K^(D(n)-k).
The compatibility factor remains complete unused stock.

This induction requires routes to fix U and generated child descriptors
to read exposed ancestors rather than fresh child roles. It also requires
the child to restore its row field pointwise. At leaves we use the completed
ordinary contract, whose own workspace obligations remain separate. We
prove sufficient coarse row stock, not a full allocation of recursive work
tapes. The retained depth-first parking procedure in `04-swap.tex`, lines
222-242, is a starting point for that allocation and its scan bill.

Since M/P=9472, S is also divisible by the P-based packet power. This is
an explicit alternative layout with an overreserve. We do not identify its
live rows with arbitrary P-slot input rows or claim that divisibility alone
discharges PR2084's physical interpretation premise.

For the eligible prime domain q>2^80, M<q and N<q^4096, so

    log_q K < 4096 w + 1 <= 4097 w.

Thus this layout fits the existing per-level logarithmic envelope. We do
not claim the earlier numerical stock constants as new. If a parent has
R_rows>=S without divisibility, the outer wrapper may pad its row range to
ceil(R_rows/S) S<2 R_rows. It may remove that padding only after the completed
parent restores its full row coordinate. We have not supplied the outer
borrow, finite-cutoff or time admission here.

The executable layout test enumerates a complete small model with W=2,
P=3, q=3 and GL1 high/low fields: 1,296 original rows, 324 rows in a selected
low packet, and unused count 108 containing the child divisor 36. We check
exact coverage and decoding, child independence from the parent high field,
and rejection of P as the live-volume denominator. This is a layout test,
not a small simulation of the full selected recursive algorithm.

## 6. Controls and limits

For the selected port-eight root r=(0,1,1,0,1,0,0,1), take g=I+3E_12 over
Z/9, with zero-based indices. The wrong transpose conjugate g P g^T agrees
with g P g^-1 modulo 3 but fails idempotence: entry (1,1) of its defect is 6.
The corresponding partial swap fails involution with defect 3 at (1,1).

An orthogonal projection onto each transformed range does not repair this.
Let u=g r and v=g^-T r. The projectors uu^T/(u^T u) and I-vv^T/(v^T v)
have split ranks 1 and 7, agree with the correct pair modulo 3, and each
defines an involution. Their product still differs from the full swap:
head entries (1,4) and (4,1) have defects 6 and 3. We need the complementary
oblique projectors uv^T/4 and I-uv^T/4.

For a separate weak-owner countermodel over GL2(Z/9), take sigma_0=I and
sigma_1=I+3E_01. The 81 owner pairs differ at each fixed d, but both image
packets are the same high fibre. The alias permutation has 27 three-cycles.
A simultaneous snapshot XOR has Boolean rank 54; the serial fixed-d XORs
have rank 81. On an all-one payload they leave zero and 27 ones respectively.
This refutes point-owner injection as a sufficient high-batching argument;
the selected low-separated completions pass the stronger condition.

We leave completed weighted child implementations, their recursive scratch
allocation, bad-class integration, a selected finite routing invoice and
the outer analytic transfer as obligations. We prove neither an unconditional
integer-multiplication theorem nor a change to the selected kappa. We prepared
this written proof and executable certificate with substantial OpenAI Codex
assistance; no independent human or proof-assistant verification is claimed.
