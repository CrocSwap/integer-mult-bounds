# The source query that a minor-log terminal must distinguish

The input-minor log changes the source block into a unit. It does not
make one sparse ordinary query sufficient at the terminal. This note
gives the exact source-query condition for a stated terminal class.
It explains the difference between a sparse log and a matched log.

## The terminal class

Use the unweighted ordinary suffix controller, the retained full first
shear, and the input-minor backward log. Either one or two selected
backward exchanges can be used. The forward word can be raw or use
the usual selected inverse-line prefix. Use ordinary Y bridges with
coefficients -I before forward and +I after forward.

The terminal can read all completed X and all retired selected Y. Its
only other information about retired ordinary Y is a fixed linear
query N. The terminal may then use arbitrary functions of these
observations. This includes a linear target-writing decoder and also
allows nonlinear postprocessing. The theorem does not restrict what
the terminal can write.

The query N in the theorem is written on logical retired Y contents.
If the actual query reads a set of physical ports, its line factors are
invertible and do not change the kernel of that port projection. The
theorem does not charge an arbitrary logical N as a native operation.

## A full-null family

At the first backward stage write B=B_s, D=D_s, M=M_s. Assume
BD=13I and MD=I, and put H=I-DB. Let v be an arbitrary ordinary field
vector. Set all original inputs after pair zero to zero. At pair zero
choose the original inputs

    original x_U=Hv,
    original y_U=DBv,
    Qa=-Mv,
    original b=-QBv+qMv.                            (1)

The retained first shear gives incoming ordinary Y v. It also gives
effective b=original b+a=-QBv, since a=-qMv. Therefore qb=-Bv.
The input-minor backward map gives

    d=Qa+Mv=0,
    h=qb+Bv=0,
    w=Hv-v+D(d-qb)=0.                              (2)

The second selected exchange, if present, exchanges zero values.
Both raw and corrected forward words then return ordinary Y r=v.
Their selected outputs remain zero. The next ordinary Y bridge adds
-v+r=0. Thus every later pair remains zero. The final ordinary X
triangle also remains zero.

Consequently every completed X and retired selected Y observation is
zero on (1). The only nonzero retired ordinary bank is v at pair zero.
The statement holds for every pair count, not just one pair.

## Necessary and sufficient separation of this family

The terminal must return the original selected physical X value -Mv
and the original ordinary Y value DBv. Since BD=13I, D is injective.
If Nv=0, these required outputs can agree with the zero input only if

    Bv=0 and Mv=0.                                 (3)

Thus a necessary condition for a complete terminal in this class is

    ker N is contained in ker B intersect ker M.    (4)

Over the finite underlying field space, (4) is equivalent to the
existence of linear maps L_B,L_M such that B=L_B N and M=L_M N.
Equivalently, the row space of the stack [B;M] must lie in the row
space of N. This condition is also sufficient to distinguish all
required outputs on family (1), including original b. It is not
sufficient to decode the full controller.

The argument still applies if N contains cross-pair source queries:
restrict N to the first retired ordinary bank. It does not apply to
a terminal that obtains other information through new native calls
on retired ordinary Y, unless that information is included in N.

## The actual sparse minor has two independent queries

Use the actual selected minor A and two disjoint ordinary minors T,T':

    A =[0,7,20,27,36,46,57,111],
    T =[21,37,47,76,81,87,92,110],
    T'=[1,6,22,28,33,49,58,109].

For M=(D|T)^-1 pi_T, let N_T embed D|T in T and let N_T' embed
(B|T')^-1 in T'. The actual orthogonal-minor identities give

    M N_T=I,       B N_T=I,
    M N_T'=0,      B N_T'=I.                         (5)

Hence the two block columns N_T-N_T' and N_T' form a right inverse
for the stack [M;B]. The stack has exactly 16 complete-field rows of
rank. The eight-port query pi_T cannot satisfy (4). In particular,
v=N_T' c is invisible on T, but Bv=c and the required ordinary Y
output is Dc, which is nonzero for nonzero c.

The identities persist in the routed chart: the port-diagonal routes
can be put on each inverse minor in their actual order. This uses no
commutation of Q with the routes.

For the matched log M=B/13, the stack [M;B] has rank eight. That log
removes the second independent query in (4). It does not make the
old-stage B query native-free. Its actual source support, line phases,
arithmetic coefficient 1/13, and implementation cost remain separate.

## Verification and scope

Run with one process from the workspace root:

    python3 -I -B work/centre-encoding-campaign-20261014/lanes/controller-followthrough-20261017/check_minor_log_source_access.py

The expected status is PASS_MINOR_LOG_SOURCE_ACCESS. The checker pins
the actual R matrix, verifies all three orthogonal minors, and checks
the two right-inverse blocks in (5) with exact fractions. It checks
all eight hidden-minor witnesses for one, two, four, and eight pairs,
with one or two selected exchanges and raw or corrected forward.
The first selected input is zero in these witnesses, so the native
assignment needs only qQ=I. The general family (1) retains both Q and
q in their displayed order.

This is an information theorem for the stated source-query class. It
is not a native child lower bound, a proof against a changed controller,
or an obstruction to a log with a different source query. In particular,
it identifies a benefit of the matched log that merits a native decoder
attempt.

The oblique-native lane supplied the input-minor log and its unit source
block. The native-escape lane is investigating the matched log. The
controller-followthrough lane supplied the full-null family and the
query criterion. This work used OpenAI Codex under the user's direction.
No independent human review is claimed. No PR, push, publication, or
commit was made.
