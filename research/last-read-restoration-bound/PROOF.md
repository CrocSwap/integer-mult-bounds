# Deferred delivery and exact workspace restoration

This proof and its finite corroboration were produced by Nick Petalas.
Apache-2.0. Claim type: scoped mathematical proof. Injectivity, counting and
matrix-rank facts are classical; no literature-priority claim is made for them.

## 1. Contract at a last-read cut

Fix the initial workspace w0, initial output y0, future sources z and an
entire random tape rho. The earlier source is x. The complete workspace at
the cut is c(x) in a set W, of any size or alphabet. Include persistent
heads, control, transcripts and any other state affecting the continuation.

The cut output a is independent of x under these fixed conditions. It can
depend on w0, y0, z and rho. This permits pre-cancellation of incoming dirt,
but forbids delivering an x-dependent part of this output early. After the cut:

1. No further read of x is allowed, including an omitted x-dependent choice
   of continuation.
2. The final workspace is s(c(x)), where s: W -> W is injective. Invertible
   workspace updates independent of output contents suffice.
3. The final output is a+d(c(x)), with outputs in an abelian group and d
   arbitrary. Outputs supply no information back to the workspace. The
   theorem also holds for an arbitrary final-output function of c.

The intended endpoint is workspace w0 and output y0+F(x). The required
deferred increment f(x)=y0+F(x)-a has the same fibre sizes as F. No linearity,
fixed workspace dimension or bounded computation is needed below.

This is a proposed interface, not a description of a selected word.
Reversibility of the combined workspace/output map alone does not imply
item 2. Output feedback is an explicit escape in section 5.

## 2. Sharp joint-success theorem

Let X have any finite distribution mu, independent of the fixed initial
state, future sources and random tape. Put p_max=max_v Pr[F(X)=v]. Then

`Pr[output correct AND workspace restored] <= p_max`.                 (1)

Injectivity implies that at most one cut state u satisfies s(u)=w0. If none
exists, joint success is empty. Otherwise every jointly successful x has
c(x)=u, hence f(x)=d(u). These inputs lie in one fibre of f, of mass at most
p_max. This proves (1). Conditioning on each independent random tape proves
the same bound for randomized protocols, including nonlinear ones. The
argument is valid for each fixed future input and arbitrary fixed dirt.

Let e_out be the final output error probability and e_work the probability
that the complete final workspace differs from w0. By the union bound,

`e_out + e_work >= 1-p_max`.                                        (2)

For uniform X in F_q^d and F(x)=Lx of rank r, every fibre has q^(d-r) points.
For every finite field, therefore,

`Pr[correct AND restored] <= q^(-r)`,
`e_out + e_work >= 1-q^(-r)`.                                      (3)

Any nonzero deferred linear target prevents simultaneous zero-error delivery
and exact restoration in this contract. More workspace cannot remove this
obstruction. A single nonzero binary target forces the sum of the two error
probabilities to be at least 1/2. For r=0 the bound is zero.

## 3. Attainment on the whole error boundary

For any finite field and any rank-r map L with codomain F_q^t, take distinct
workspace and output registers w,y in F_q^t with arbitrary initial values.
Execute:

```text
before cut: y -= w
before cut: w += Lx       # the only read of x
after cut:  y += w
```

At the cut y=y0-w0, independent of x. The output is always y0+Lx. The final
workspace w0+Lx is restored exactly on ker L, with probability q^(-r). The
suffix workspace map is the identity. This attains
`(e_out,e_work)=(0,1-q^(-r))` on arbitrary incoming dirt and output values.

Leaving both registers unchanged instead attains `(1-q^(-r),0)`. An
independent coin choosing between the two programs attains every point on
`e_out+e_work=1-q^(-r)` in the nonnegative quadrant. Thus (3) is the sharp
lower boundary of this error pair. These are logical state transitions;
no native realization, free operation or favorable paid invoice is asserted.

## 4. Rank obstruction over every field

For a linear computation let the cut workspace be Bx+b. Since the cut output
has zero x coefficient, the final output's x coefficient is L=CB for some
C. The final workspace's x coefficient is E=AB with A invertible. Thus

`rank L <= rank B = rank E`.                                      (4)

E measures dependence on x, not on incoming dirt. Exact restoration requires
E=0, forcing L=0. This holds over infinite fields too. The program in section
3 has B=L and A=C=I, attaining equality for every rank.

## 5. Changed-premise controls

The first four programs change a hypothesis and deliver/restore exactly.
The last control exposes omitted state. None is a counterexample to (1).

* Read x again after section 3's delivery and execute w-=Lx. This pays a
  second source-dependent operation, the usual missing inverse call.
* With clean initial workspace, load Lx, deliver it and erase workspace to
  zero. The suffix workspace map is not injective. Erasure/history costs
  need their own implementation and cannot be treated as zero.
* Allow output feedback. Before the cut swap w and y, then add Lx to w.
  At the cut y=w0, independent of x. After the cut swap w and y again.
  The endpoint is `(w,y)=(w0,y0+Lx)` for arbitrary incoming values. This is
  reversible on the combined pair, but the suffix workspace is not a
  function of workspace alone. No ADD decomposition of SWAP is claimed.
* Deliver y+=Lx before the cut and leave workspace untouched. Delivery is
  no longer deferred.
* Leave a source-dependent log outside the reported workspace. Apparent
  restoration can leave that log dirty; including it restores the boundary.

This excludes no construction using source rereads, readable outputs, paid
irreversibility, early accumulation or retained history. It is a rejection
test for a declared one-pass deferred helper interface, not a universal
network, compiler or multiplication lower bound. No new kappa follows.

## 6. Finite evidence

The verifier exhausts literal prefix maps, suffix permutations and output
maps on three declared small domains. It scores each input directly, without
using a rank/fibre bound to compute the score. Separate finite-field gate
executions check attainment and changed-premise escapes on arbitrary dirty
workspace and output values. Elimination checks (4) on separate matrices.
All checks remain active under optimized Python. The finite evidence
corroborates the written proof; it does not extrapolate it from sample fields.
