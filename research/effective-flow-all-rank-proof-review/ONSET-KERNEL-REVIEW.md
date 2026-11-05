# External written review: symbolic onset and kernel transfer

Reviewed source: alephnan PR6713 at `cd666f05c4e9006025b634687cc493911c8371c8`. Exact inert inputs are LOCAL_LIMIT.md SHA256 `07702eabadefa4e2c435d6ea7e60c781aaa786fa875cab773a5962d8d2a2efe3` and PROOF.md SHA256 `e7dbe4e1705a307e9eb32f6f06b340fb2c49948cc749110d6be2c6fb3da94ea9`.

**Result: no correction required in the reviewed onset/kernel steps, conditional on the stated interval estimate and numerical/model premises.** In particular, the source uses monotonicity on each finite window, not an invalid global monotonicity claim, retains singleton/half-open conventions, and keeps the unbounded leaf tail charged. This note is a source-aware written derivation and adversarial review, not execution of any source or new scientific program, an independent Fourier theorem, or a full recurrence/physical admission.

## 1. Exact scope and inherited premises

I inherit LOCAL_LIMIT §§3–7's interval estimate (1)/(2) under (H), which has prior external review in PR6723; I do not re-prove the Beurling–Selberg/Fourier argument. The exact tilt/centering and finite-H premise bridge has the separate S9 review. This note checks the algebraic simplification in §8, layer-cake/Stieltjes implications in §9, and their compatibility with PROOF §§4–7's finite mixed windows and entire leaf half-line. The finite flow decomposition, strict capacity margin, late-layer numerical bounds and final induction are separate review responsibilities.

## 2. Symbolic onset

Let w=ln(n). The hypothesis n>=2^100 and ln2>2/3 gives w>=200/3>60. Substituting B_n into A_n+bB_n+b^2/(4 sqrt(n)) gives

```
1/w + [3(b+4/w)+b^2/4] exp(-w/2)
    +(b+4/w) w exp(w/2) exp[-exp(w/2)/320].
```

For b<=5000 and w>=60, b+4/w<5001 and
3*5001+5000^2/4=6265003<2^23, proving source (12). No dependence on the interval's location was introduced.

After multiplying its first remainder by w, the function w exp(-w/2) decreases for w>=60. The positive exponential series gives e^3>16, hence e^30>2^40. Its value at 60 is therefore less than 60/2^17<1/2 after the 2^23 coefficient is included.

The other remainder multiplied by w is bounded by 5001*w^2*exp(w/2)*exp[-exp(w/2)/320]. Its logarithmic derivative is 2/w+1/2-exp(w/2)/640, which is negative for w>=60. At 60, u exp(-u/320) decreases for u>320, and u=e^30>2^40. The bound is consequently below

```
5001*60^2*2^40*exp(-2^40/320)
 < 2^65*exp(-2^31) < 1/2.
```

Thus both remainder terms sum to less than 1/w, yielding 2/ln(n). The exact-Gaussian-interval estimate is smaller because it lacks the nonnegative b^2/(4 sqrt(n)) term. This reasoning includes b=0 and every inherited endpoint convention.

At n>=2^(10^12), c_sigma<5 follows from v<=3 and pi<4. Hence c_sigma*2/ln(n)<10/ln(n)<=15/10^12<10^-8. The onset is a symbolic exact integer expression. No large integer or convolution is constructed or claimed to have been tested.

## 3. Layer cake, shifts and endpoint atoms

For a nonnegative bounded function monotone on a finite interval and zero elsewhere, every positive superlevel set is an interval, possibly empty or a singleton, with one of the permitted endpoint conventions. At each positive level t, apply (1) to the reflected/translated set under u=c-Z_n. Its interval length is unchanged and the estimate is uniform in location. Integrating the absolute bound over t gives

```
sqrt(n)*|E f(c-Z_n)-E f(c-G_n)|
 <= ||f||_infinity*A_n + B_n*integral f.
```

This is source (13). It holds for every shift c with the same right side. Endpoint atoms cannot be discarded: the inherited interval theorem includes them, and its singleton term A_n remains even when the Lebesgue length is zero. Layer cake uses those actual level sets rather than replacing their endpoints by a Gaussian convention.

For g(u)=exp(-tau*u)1_[0,infinity)(u), tau>0, use the increasing truncations g(u)1_[0,M](u). Each has interval superlevel sets and integral at most 1/tau. The two expectations converge monotonically and the inequality passes to the limit, giving A_n+B_n/tau. Equivalently each positive superlevel of g is already finite. No tail cutoff is necessary for this Gaussian-comparison step.

The subsequent flat-density replacement is a different estimate. Direct Gaussian integration gives the scaled expectation as

```
(1/c_sigma)*integral_0^infinity exp(-tau*u)
                    *exp[-(c-u)^2/(2nv)] du.
```

Its difference below 1/(c_sigma*tau) is bounded using 1-exp(-z)<=z. Integrating (c-u)^2 exactly, then replacing -2c by 2|c|, gives (14). The resulting bound depends on c^2 and |c|. Thus (14) is valid for all c but is not a shift-uniform small error. It cannot be used to flatten arbitrary distant mixed layers. PROOF instead bounds early-layer shifts, uses interval probabilities for middle layers and trivial bounds for the end layers. The leaf shift delta lies in [0,ln5), so it is bounded.

## 4. Capacity kernel, singular endpoint and Stieltjes transfer

For 0<s<1, Q_s(x)=1-(1-x)^s is convex, Q_s(0)=0, and convexity implies x Q_s'(x)>=Q_s(x) for 0<x<1. For x=c exp(-u), differentiation on that open range gives

```
d[exp(alpha*u)*Q_s(x)]/du
 =exp(alpha*u)[alpha*Q_s(x)-x*Q_s'(x)] <=0
```

when alpha<1. If x=1 at an included left endpoint, the derivative can diverge but Q_s itself is continuous and finite. Monotonicity extends to that endpoint by continuity. The resulting function has finite total variation; Stieltjes or level-set integration needs no bounded derivative. For source windows [ln r,ln k), x=(rk/121)exp(-u)<=k/121<=1, so the formula never enters x>1. Boundary kernels decrease because tau>0.

The kernels need only be monotone on their own windows. With all ranks positive, each window lies inside [0,5), and all its subintervals have length below five. A half-open right endpoint remains half open. If a signed measure has discrepancy at most d on every such interval, writing a decreasing continuous kernel v as its terminal constant plus its decreasing Stieltjes part bounds its integral discrepancy by

```
d*(v(right)+total_decrease)=d*v(left).
```

The source explicitly includes the terminal-constant whole-window term. Summing absolute errors separately over all weighted positive and negative windows gives Q*d without assuming cancellation or monotonicity of their signed sum. The possible x=1 endpoint singularity does not alter that argument.

PROOF §5's conditioning produces u_h=v-Z_ell with bounded v for h<=3000; reflection preserves the interval lengths and endpoint conventions. Its discrepancy from Lebesgue measure includes both the interval-theorem error and the nonconstant Gaussian-density error. Applying the finite-window Stieltjes bound is therefore compatible with (13), rather than silently replacing a discrete probability measure by a density.

The leaf g is not supported in [0,5). PROOF §7 uses [0,5000) only for its first part, then explicitly sums the remaining unit intervals and separately bounds the Lebesgue tail. This is compatible with the half-line result above. Neither the entire leaf expectation nor the limiting integral 1/tau is replaced by its truncated part. The precise tail constants are assigned to the separate late-tail review.

## 5. Written adversarial controls

* A windowed decreasing function is generally not decreasing on all of R: exp(-u)1_[0,1](u) jumps from zero to one at zero. This defeats a global-monotonicity shortcut, but its superlevel sets are intervals, as the source needs.
* For v identically one on a window, -dv is zero while the whole-window discrepancy may be nonzero. Dropping the terminal-constant Stieltjes term would give a false zero error. The source retains it.
* An atom at a window endpoint distinguishes [a,b) from (a,b). Endpoint conventions cannot be erased merely because the Gaussian has no atoms. The singleton/endpoint interval control prevents that step here.
* A positive leaf tail cannot be declared absent. In the actual finite law, the all-rank-one word has positive probability. At large G it gives u_leaf=delta+G*ln5>5000, where g remains positive. Its contribution may be small but requires the source's tail charge.
* A shift c proportional to n can place the half-line kernel far from the Gaussian center; replacing it by 1/(c_sigma*tau) with a c-independent vanishing error is false. Equation (14)'s c-dependent terms and the source layer split prevent this.

These are hand controls, not executed experiments or counterexamples to the stated source proof.

## 6. Decision and limitations

The reviewed symbolic onset, interval-to-kernel transfer and endpoint treatment are sound under their named premises. No local correction is requested. A downstream summary must retain the distinction between (13)'s shift-uniform comparison and (14)'s shift-dependent flattening, per-window monotonicity and global zero extension, and a finite cutoff plus paid tail versus the entire half-line.

This note does not authenticate executable source constructors, re-run inventories or margin checks, independently admit the scalar recurrence identity, prove every later propagation constant, execute a proof kernel, or discharge a physical/selected supplier condition. Source authors and earlier external reviews retain their credit. The calculus, layer-cake, Stieltjes and symbolic onset reasoning are classical methods; this external written audit is prepared with substantial OpenAI Codex assistance, not human acceptance.
