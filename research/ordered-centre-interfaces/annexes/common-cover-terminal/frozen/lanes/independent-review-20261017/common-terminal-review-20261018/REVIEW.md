# Independent review of the common-cover terminal

The finite terminal passes this review. It returns FULL of the raw input
`(Qx,y)` from the stated common-response controller. The cover address,
two positive line transforms, FULL translations, and final bank sign
are correct. The result uses admitted native children and array maps.
It does not supply their recursive hosting or complete execution cost.

The source terminal proof is `COMMON-TERMINAL.md`, SHA-256
`d57d298a6b5394270fa2360d15d867b406f7fbc5e69d62829b978edda29b05ad`,
in `encoded-controller/common-monomial-terminal-20261018/`.
The source program SHA-256 is
`c87e99deeffa12b30b37f633c784118623aba1a4680ad3ae925d29be4f91a4d6`.
The source freeze SHA-256 is
`e342c8d646a5c7cb5ee8cfd53d231c91a572b24894b9217a3a9533c00cce09f0`.
No source file was changed. No material proof error was found.

The common-response controller has an all-pair proof. Put `a=Ex` and
`b=y`. Every local F becomes `b <- b+a`; every local B becomes
`a <- a-b`. Each retained bridge also has its unit-response form because
the same E acts on every X bank. This change of variables does not move
E across Q.

For a direct induction, let `c_-1=0` and
`c_i=-b_i-c_(i-1)`. Just before B on pair i, its state is
`(a_i,b_i+c_(i-1)+a_i)`. B sets its X field to `c_i`. If there is a next
pair, the plus bridge, F, and minus bridge leave this pair at
`(c_i,a_i+a_(i+1))` and prepare the next Y field as
`b_(i+1)+c_i+a_(i+1)`. On the final pair, F leaves Y at `a_i`.
The descending final bridges therefore give X_i=`c_i+c_(i-1)=-b_i`
and Y_i=`a_i`. This proves the endpoint `(-E^-1 y,Ex)` for every pair
count and arbitrary inputs. The independent checker also uses reverse
columns to verify the actual pinned nineteen content events and ten
idle sites for four pairs. Its coefficients are free integer Laurent
polynomials in E; it does not use `E^10=I`.

At the physical terminal input,

`U=-F E^-1 y` and `V=F Q^-1 E x`.

Let `M_I=F E^-1 F^-1` and `M_E=F E F^-1`. In time order, the V branch
uses `Q`, then `M_I`, then `Q`. Its value is successively `F E x`,
`F x`, and `F Q x`. The U branch uses `M_E` and becomes `-F y`.
The signed exchange gives `(F Q x,F y)`. This uses commutation of
payload line transforms with F. It makes no claim that E commutes
with Q. The same equations apply to every tensor coordinate copy.

The literal cover maps agree with this order. At output cover h, the
V source is at `h L^-1`. Its intrinsic line is therefore `h L^-1 q`.
For every actual port, `L^-1 q=v_8`, with `v_8=2^65` in the binary
coordinate encoding. Thus the two positive lines are `h q` and
`h v_8`, not two copies of `h q`. The U source is at `h L`. The source
cover compositions with the preterminal E and E^-1 are both the
identity. All 112 actual cycle matrices and both inverse orders pass.

The independent phase check uses full polynomial coefficients modulo
four, rather than the producer's character probes. For a binary
column matrix A, the polynomial `weight(A eta) mod 4` has linear
coefficient `weight(A e_i) mod 4` and quadratic coefficient
`2 (A e_i)^T (A e_j) mod 4`. All higher coefficients vanish modulo four.
For orthogonal A, the off-diagonal coefficients vanish, and every
linear coefficient is odd. Thus its difference from `weight(eta)` is
an even linear polynomial. It is exactly a payload translation, with
no constant phase.

This calculation checks the complete forward and inverse FULL
translations in the source payload. It also checks every coefficient
of the final X and Y phase equations. In particular,
`L epsilon=delta`, with the output-coordinate convention used in the
literal maps. Omitting either FULL translation, using q twice, or
omitting either line gives a different phase polynomial. The wrong
cover direction gives a nonidentity address composition.

The serialized child wrappers pass a separate affine address and
Gaussian kernel check. Their matrix G is orthogonal, its first columns
are `(q,v_8)`, and the stored inverse is exact in both orders. The two
stored even-vector transvections and the input-axis swap reconstruct
G exactly. If the output address is w, the wrappers read

`V(h L^-1, w + h epsilon + h G tau)`,

where tau runs over the four first-two-axis shifts of the rank-two
child. The four coefficients are `i/2, 1/2, 1/2, -i/2` at shifts
`0,q,v_8,q+v_8`, respectively. This is exactly the product `C_q C_v8`,
including its global phase. The checker verifies all affine address
coefficients and all four coefficients of this kernel. These are
complete finite descriptions of the maps on all `2^73` payload
addresses. Multiplication by an arbitrary orthogonal cover h preserves
the equations, so no equality of contents at different cover labels
is assumed.

The terminal needs 448 positive rank-two children, native rank mass
896, 896 child wrapper maps, and 448 additional FULL cover/translation
maps per four-pair replica. The total map count is 1,344. The old
terminal's 448 line-square maps are removed, so the net map increase
is 896. The signed exchange remains `(X,Y)=(V,-U)`. Three unit complex
ADDs implement it: `U+=V`, `V-=U`, `U+=V`. Its 10,752 real primitives
are retained work. The new translations and cover permutations have
no scalar coefficient multiplications. This statement does not give
their finite address-execution time or the recursive cost of a child.

The standalone rank claim is correct in its stated class. After
removal of the cover permutation and translation, the X branch has
binary upper-right Clifford block `q q^T+v_8 v_8^T`. It has rank two.
For a product of Clifford matrices,
`B_product=A_left B_right+B_left D_right`, so its rank is at most the
sum of the two B ranks. Monomial Clifford views have rank zero and
preserve B rank on the left or right. Thus a one-field Clifford word
needs total native rank at least two here. The emitted child attains
this bound. This does not bound a circuit that mixes fields or changes
an earlier native call.

I also checked the symbolic proof in the separate frozen
`cover-line-terminal-limit-20261018/LIMIT.md`, SHA-256
`5e71f90893fafd7e85a7fd49617f6982dfada8079e1223a29135bb957f0707c3`.
For any orthogonal L with `Lq=v` and `q^T v=0`, put `w=L^-1 q`.
Then `q^T w=(Lq)^T q=0`, while q and w both have norm one. Hence they
are distinct. The same rank-two conclusion holds for every such L.
The actual 112 cycles satisfy these hypotheses. This rules out a
smaller standalone terminal merely from a different orthogonal
extension of the same cover-only line map. It does not rule out a
payload response, a different first cut, or fusion with an earlier
operation. I did not rerun that addendum's separate exhaustive
dimension-three and dimension-five enumeration.

The native-moment conclusion remains conditional on the full path and
idle ledger. If the productive paths have total rank `2mn(D-1)` and
this terminal adds `2mn`, the total is `2mnD`. For `b>0` and each child
width `r<=D`, `r^(1-b)>=r D^-b`. Their total native weight is therefore
at least `2mn D^(1-b)`. A different partition of that same rank cannot
give a positive saving in this model. This review does not verify the
complete hosted path ledger or claim a lower bound for broader
supplier constructions.

Run from the workspace root:

```text
python3 work/centre-encoding-campaign-20261014/lanes/independent-review-20261017/common-terminal-review-20261018/check_terminal.py
python3 -O work/centre-encoding-campaign-20261014/lanes/independent-review-20261017/common-terminal-review-20261018/check_terminal.py
```

Both runs print `PASS_INDEPENDENT_COMMON_COVER_TERMINAL` and produce
byte-identical receipts. The checker imports no producer module and
does not run the producer checker. `CHECKS.json` pins the inputs;
`REPRODUCTION.json` pins the equal receipts.

The terminal is an exact finite operation under the stated map and
child contracts. Fresh local native words, whole-cover scheduling,
recursive workspace hosting, array-map execution cost, the complete
supplier invoice, and finite precision remain separate obligations.
No PR, push, publication, or commit was made. This review is
AI-assisted.
