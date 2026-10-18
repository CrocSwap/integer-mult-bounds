# One z target and one uz target cost exactly fourteen calls

This is a computer-assisted theorem in the formal UT4 model. The written rank
argument quantifies arbitrary finite dirty workspace and word length. The finite
census excludes the one remaining two-role call split. Neither part establishes
a physical supplier, a rational-frame translation, or a multiplication exponent.

## Model and predecessor boundary

Let `G=UT4(F2)` and `R=F2[G]`. Write

```
a=I+E12, b=I+E23, c=I+E34,
u=I+E13, v=I+E24, z=I+E14.
```

Every paid factor is `D_N(g)=I+([g]+1)N`, where `g` is one of `a,b,c` and
`N=xy^T` is a nonzero binary rank-one matrix on the scalar roles. Both
idempotent and nilpotent couplings are allowed. Every occurrence, including
restoration, costs one call. All roles have arbitrary initial data. Extra roles
must finish as the identity operator, with no contamination of target outputs.

Scalar GL operations are optimistically free. Conjugating them into the paid
couplings preserves rank one. Augmentation sends every paid factor and the target
to identity, so the scalar operation remaining at the end is identity. There are
no free address maps, clean roles, COPY, ERASE, higher-rank paid operations, or
unpaid inverses. Equality means the full formal group-algebra operator, not its
image at a sampled address size.

Gareth Davidson's [PR2027](https://github.com/CrocSwap/integer-mult-bounds/pull/2027)
proves the separate-letter bounds below and their sharpness when there are no
pure-central roles. Its explicit next question is one z role and one uz role.
ToikY's [PR1662](https://github.com/CrocSwap/integer-mult-bounds/pull/1662)
supplies the central-target middle quotient; PR1680 supplies the workspace-span
compression method. We use those methods and Aaron Wang's PR1690 profile-screen
method. The new statements are the mixed middle bound, its application to this
endpoint, and the exact exclusion of its thirteen-call split.

## A mixed middle bound

For the more general diagonal endpoint

```
diag([u^s_i v^t_i z^h_i]),
```

let `S,T,H` denote the binary diagonal matrices with entries `s_i,t_i,h_i`.
Let `d` count coordinates with at least one of these entries nonzero, and `k`
count pure-central coordinates, where `s_i=t_i=0,h_i=1`.

**Lemma.** Every such word has

```
n_b >= 2d+k.
```

This strengthens PR2027's `n_b>=2d` by charging each pure-central role once more.
It is only a necessary bound for the general family, not a general sharp tariff.

Use the predecessor quotient

```
Q=F2<A,B,C>/(A^2,B^2,C^2,AC-CA, all terms of degree at least four).
```

Its seventeen-element monomial basis and its group homomorphism are independently
reconstructed in `verify.py`. The program checks all 4,096 group products and
all 4,913 basis associativity triples. In this quotient,

```
u maps to 1+AB+BA+ABA+BAB,
v maps to 1+BC+CB+BCB+CBC,
z maps to 1+ABC+ACB+BAC+CBA.
```

Products of nonconstant root terms have degree at least four. Thus the endpoint
has coefficients `S` on the four u terms, `T` on the four v terms, and `H` on
the four z terms.

Number the b calls in chronological product order. Write their couplings as
`x_j y_j^T`. Let `P_j` be the sum of a couplings before call j and `Q_j` the
sum of c couplings after it. Define

```
X=[x_j], Y=[y_j^T], U=[P_j x_j], V=[y_j^T Q_j].
```

Here X,U have shape `r by n_b`; Y,V have shape `n_b by r`. Ordered expansion
without commuting scalar matrices gives

```
XY=0, UY=S, XV=T, UV=H.                         (1)
```

PR2027's same-label span argument applies unchanged. Coefficients BA,BC,BAC
force the column span of X to contain the union of the active target coordinates.
AB,CB,ACB force the analogous row span of Y. The two representatives BAC and
BCA both start with B; ACB and CAB both end with B. Consequently

```
rank X >= d, rank Y >= d.                      (2)
```

Let pi delete output coordinates in the support of S, and restrict the input
to `ker T`. By (1), `V(ker T)` is contained in `ker X`, and `pi U` annihilates
`im Y`. Thus `pi H` restricted to `ker T` factors through

```
ker X / im Y.
```

Its rank is exactly k because H is diagonal. Since XY=0, the quotient has
dimension `n_b-rank X-rank Y`. Therefore that dimension is at least k; (2)
proves `n_b>=2d+k`. This argument includes all restored identity roles.

For comparison, the necessary four-matrix relaxation is attained at five middle
columns for one z and one uz role. One explicit fixture is

```
X = [1 1 1 0 1; 0 0 0 1 1],
Y = [1 0; 1 0; 0 1; 0 1; 0 1],
U = [0 0 1 1 0; 0 0 0 0 1],
V = [1 0; 0 0; 1 1; 0 1; 0 1].
```

All X columns and Y rows are nonzero; both ranks are two. These matrices satisfy
(1) with `S=diag(0,1), T=0, H=I2`. They do not supply P_j,Q_j from paid
chronological paths or satisfy every quotient coefficient. In particular, this
fixture must not be described as a thirteen-call word. The tests check it and
reject a changed V entry.

## Compression of the only possible thirteen-call word

The desired endpoint is

```
diag([z],[uz],I on every other role).
```

Here d=2 and k=1. PR2027's outer bounds give `n_a,n_c>=4`; the new middle bound
gives `n_b>=5`. Fewer than thirteen calls are impossible. At thirteen calls the
counts must be exactly `(4,5,4)`.

For each outer letter, its column and row spans contain the two active coordinate
directions. Their ranks sum to at most its call count because the first-order
sum is zero. Hence both ranks equal two. For b, the proof above gives
`rank X+rank Y<=n_b-k=4`, so both ranks also equal two.

Every one of these six spans is therefore exactly the active two-coordinate
plane. Each x_j and y_j is supported in that plane. Every coupling is its active
2x2 block, with zeros elsewhere. The entire word is already block diagonal with
identity on the dirty complement. Restriction to two roles preserves every
nonzero factor and its letter. No extra role, regardless of its initial dirty
value, can rescue a thirteen-call word. This is a special exact-span application
of PR1680's method, not a claim for longer words or arbitrary target families.

## Complete two-role exclusion

On two roles there are nine nonzero rank-one binary couplings. The first-order
coefficient of each letter is zero. The census covers all `(4,5,4)` words as
follows, without scalar conjugation or permutation symmetry reductions.

1. Enumerate all `9^5=59049` ordered middle sequences. Retain the 3,600 with zero
   sum. Every legal endpoint must be among them.
2. Enumerate all `9^4=6561` outer sequences. Retain those with zero sum. Place
   the four calls into all six chronological gaps around the five middle calls,
   using all 126 nondecreasing gap assignments. Retain every concrete realization
   and its prefix-sum profile. There are 9,721 distinct profiles.
3. For a profile P, the four one-sided coefficients are

   ```
   AB = sum P_j B_j, BA = sum B_j P_j,
   ABA = sum P_j B_j P_j,
   BAB = sum_{j<l} B_j (P_j+P_l) B_l.
   ```

   The A side requires all four to equal `diag(0,1)`. The same equations for a
   c-suffix profile require all four to vanish. Zero c total makes its suffix
   and prefix sums equal. The counts, summed over all middles, are 89,052 and 1,201,320.
4. Group retained profiles by the transported column and row vectors. Solve
   `ABC=I2` exactly by binary parity equations and then check `CBA=I2`. This gives
   68 key pairs and 152 profile pairs. The key grouping forgets no profile or
   realization.
5. Expand every concrete realization of each pair, including every A/C
   interleaving within each gap. There are 5,536 words. Multiply every word in
   the complete seventeen-dimensional Q and compare every coefficient with
   the target. **None passes.** The receipt records the complete expansion
   transcript digest and the first differing coefficient of each rejected word.

Every concrete word has a unique middle sequence, two outer sequences and their
ordered gap assignments. The construction enumerates these. Side and cross
screens impose only necessary equations, never heuristic thresholds. Full
quotient rejection at the final stage is therefore enough to exclude every
thirteen-call formal word. No formal endpoint is accepted from a quotient image.

The implementation intentionally reconstructs concrete gap placements directly,
unlike PR1690's recursive profile/gap reconstruction. Tests compare its formulas
with a separate dense truncated-word oracle and recover planted concrete words
from their profiles. An optional LOCAL-ONLY exploratory cross-check using PR1690's retained
helpers gave the same 3,600 / 89,052 / 1,201,320 / 68 / 152 / 5,536 census counts and zero quotient
survivors. That corroboration is not an additional proof premise, a proof-kernel
check or independent human review.

## Fourteen calls attain the bound

Apply `abcbabcb` to the first coordinate and `acbabc` to the second, using the
corresponding coordinate projector. Their literal group products are z and uz,
respectively. This is the predecessor direct construction, not a new word.
It has counts `(4,6,4)`, fourteen calls, and no extra roles or uncounted undo.

The verifier checks its full formal group-ring operator on both target roles
and a separately arbitrary dirty identity role. All fourteen one-call omissions
and a wrong-letter mutation fail. Combined with the uniform compression and
complete exclusion, the unit-price minimum is **fourteen for every finite r>=2**.
This does not prove the optimal weighted tariff, nor exclude longer words with
fewer b calls and more outer calls. It does not implement a physical address
alphabet or improve the selected multiplication bound.

## Credit and remaining obligations

Credit Gareth Davidson/PR2027 for the mixed family, sharp noncentral tariffs,
span unions and the explicit z/uz handoff; ToikY/PR1662 and PR1680 for the quotient
and compression methods; Aaron Wang/PR1690 for the profile-screen algorithm;
steph4n-gh/PR1573, Arham Tahir/PR1589 and Hanson Sun/PR1607 for the retained
zero-sum and coefficient-span lineage. All predecessor files remain unchanged.

The finite homomorphism and exclusion census are premises of this
computer-assisted theorem. Lean/kernel verification, physical letters,
rational-frame conversion, common-label realization, hosting, precision/tape,
all-size compilation and outer analytic transfer remain unproved here.
Apache-2.0. No literature-priority or independent human review claim is made.
