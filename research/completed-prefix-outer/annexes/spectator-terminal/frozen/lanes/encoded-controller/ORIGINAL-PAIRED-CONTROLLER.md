# The original complex paired controller

The original complex paired local words have an exact nine-call joint
map. Their error injections do not change any later centre query. This
removes the centre feedback matrix, but it does not restore the arbitrary
mode inputs by itself. The retained source schedule also gives an exact
limit on mode reuse without another data read.

This note uses the emitted local pair in
`../residual-syndrome/physical-algebra/ORIGINAL-PAIRED-GAP.md`. Its
decompressed payload hash is recorded in the accompanying JSON file.
The old ordinary schedule and its source and response rows come from
`NILPOTENT-CONTROLLER.json`. The new proof does not use the mode-side
phase transport identities from the Walsh version of that note.

## Local and global maps

Let Q be the original port line operator, extended equally to the two
replicas. Set

```text
L_line=Q^2,  A=[[0,I],[L_line,0]],
T=QA=[[0,Q],[Q^-1,0]].
```

A is a port-dependent monomial map. It is not a map on the centre
indices. We have `T^2=I`, `AQ=QA`, and `A^-1=L_line A`. With the actual
stage routes and one-use mode gauges, set

```text
G_s=N_s^-1 R D_s(I-T),
H_s=(I+T)D_s^-1 K N_s.
```

The actual routes commute with T. Thus `G_s H_t=0` for every s,t.
The two local maps are

```text
F_s: x'=x,  v=-z-G_s x,    y'=y+x+H_s v,
B_s: y'=y,  v=-z-G_s y/8,  x'=x-y-8H_s z.
```

All modes and data inputs are arbitrary. Each paired local call restores
its 944 other helper inputs. Global owner admission is a separate check.

Let D contain the eight paired old data banks. Let U and V contain the
nine paired mode cohorts before and after the controller. Let P select
the five forward cohorts and Q_mode select the four backward cohorts.
For the exact source rows a_s and response columns b_s, put

```text
L_s=b_s tensor H_s,
T_query,s=beta_s a_s tensor G_s,
beta_s=1 for F and 1/8 for B.
```

The factor 8 for a backward response is already in b_s. The complete
joint map, including the retained ordinary terminal, is

```text
V=-U-T_query D,
D'=D-LU-LP T_query D,
T_query L=0.                                      (1)
```

For each later query, every earlier data error has a factor `G_s H_t`
and vanishes. This proves the first line. Propagation of the target
errors through the ordinary bank word proves the second line. The
checker verifies all 17 arbitrary input blocks in the free operator
algebra, with no relation between distinct R D_s row spaces.

The three output operations

```text
D1=D'-LPV,
U=-V-T_query D1,
D=D1+LQ_mode U                                   (2)
```

restore every input. There are 28 projected H blocks and 28 projected
G blocks. On a paired implementation their direct expansions have
100352 scalar terms with their explicit line and source-map factors,
and 144 mode negations. This is a finite algebraic expression. It does not price
the odd native line in any of those terms.

## The actual physical endpoint

Let W be Q on the four logical X banks and I on the four Y banks. The
raw old-data input is `xi=W D`. After the retained line-square
translations and signed exchanges, the physical output is

```text
(F W D', F V).
```

Here F is the common complete native transform. Mode preparation and
completion are the stated one-use histories. Conjugation by F changes
their N_s maps by the known monomial adapters.

There is a valid phase transport identity on the data side:

```text
Q H_s=A^-1 H_s,       G_s Q^-1=-G_s A.             (3)
```

It follows from `T H_s=H_s`, `G_s T=-G_s`, and `AQ=QA`. It does not
move A through R, K or N_s. Define the data-bank monomial maps

```text
B=diag(A^-1 on X, I on Y),
C=diag(-A on X, I on Y).
```

Then `W L=B L` and `T_query W^-1=T_query C`. After removal of the common
output F, the exact physical code on `(xi,U)` is

```text
[[I-BLP T_query C, -BL],
 [-T_query C,       -I]].                          (4)
```

Also `T_query C B L=0`, because CB is a bank sign and commutes with T.
Thus the same three-step decoder applies to `L_phys=BL` and
`T_phys=T_query C`. This records the physical endpoint without a false
centre action for A. The projected maps H and G still contain T. A
paired terminal that consists only of these even data maps has not
removed that access obligation.

## A limit on cyclic mode reuse

Keep the retained ordinary data word. Permit any finite collection of
mode cohorts. A local call can use any cohort after an invertible mode
change. Permit arbitrary invertible mode maps between calls and at the
terminal, including maps with cover and payload coefficients. Do not add
a new data-to-mode read. All local injections still have image in some
H_s, so every later G_t annihilates them.

For the initial X0 bank, the exact ordinary source coefficients are

```text
(a_0 X0, ..., a_8 X0)=(1,1,0,0,0,0,0,0,0).       (5)
```

Every mode query inserted at stage s is followed by invertible mode
transport. Its inclusion into the full mode state is injective. Call
that inclusion C_s. Mode restoration on all X0 inputs would require

```text
C_0 G_0 + (1/8) C_1 G_1=0                        (6)
```

up to invertible signs and mode gauges. In particular, (6) requires
`ker G_1` to be a subset of `ker G_0`.

That inclusion fails on the actual regular cover. Write
`R_s=R D_s`, with all 112 ports retained. Then
`R_s R_s^*=56I`. For any centre coordinate e_k, define the integer
cover vector

```text
h=(56I-R_1^* R_1) R_0^* e_k delta_identity.
```

We have `R_1 h=0`. The 112 stage-1 port routes are distinct involutions.
Hence the identity coefficient in `R_0 R_1^* R_1 R_0^*` is

```text
sum_p ||r_p||^2 r_p r_p^*=4 R R^*=224I.
```

It follows that `[R_0 h]_identity=(56^2-224)e_k=2912e_k`, which is
nonzero. There is no odd denominator in h.

Make the native payload constant and use paired X0 input `(h,-h)`.
The original Q fixes a constant payload, so T is the replica swap on
this input. Therefore `G_1(h,-h)=0`, but
`G_0(h,-h)=2N_0^-1(R_0h,-R_0h)` is nonzero. All other data and initial
mode inputs can be zero. After F0, the mode state has a nonzero signal.
B1 reads zero, and every later ordinary source is zero for this input.
The signal then passes only through invertible mode maps. It cannot
become zero at the output.

This excludes restoration by mode reuse and mode-only routing for the
stated ordinary source word. It does not exclude a changed data word,
another ordinary-to-mode read, a local injection outside the common
plus image, a mixed data/mode terminal, or a restricted zero-mode
supplier with a different contract. The argument also does not give a
native-child lower bound for a repair.

## Verification and remaining work

Run `python3 -I -O -B check_original_paired_controller.py` from this
directory. The expected status is
`PASS_ORIGINAL_PAIRED_GLOBAL_MAP_AND_REUSE_LIMIT`.

The checker pins the emitted paired payload, verifies (1)--(2) with the
existing free algebra, checks the physical identities (3), reconstructs
all 112 actual routes, and checks the integer witness coefficient. It
also checks (5) from the full schedule. This is a content and route
check. It does not admit the paired owner schedule or implement the
remaining projected boundary queries.

No complete supplier, kappa improvement, or unrestricted controller
obstruction is claimed. The result identifies a specific missing read:
the part of the first-stage query that the next-stage query cannot see.
