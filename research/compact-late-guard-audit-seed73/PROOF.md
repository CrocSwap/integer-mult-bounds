# A two-pass invariant guard for later-source compact controls

Mathematical audit / research note; no new kappa. This concerns the unchanged
later-source address word in `notes/compact-control-movement.tex`, at base
`49b3157d1d89adcef16df8be98445451672be5ba`. The note and literal physical
interpreter are pinned in [SOURCES.json](SOURCES.json).

The inputs are complete, disjoint address fields in the source's stated order
`u,t,y,x,b`. Their availability at recursive nodes and the implementation of
the controlled rotations remain inherited hypotheses. Every compact field is
dirty; none is assumed zero.

## Statement

Let `n>=1`, `G>=1`, `K>=G+1`, `0<=rho<K`, and write

\[
B=2^G,\qquad A=2^{K-1},\qquad R=2^K=2A.
\]

The wide slots have `(n+1)K` bits. The raw routine processes positions
`rho+iK`, `0<=i<n`; the highest selected position is supplied afterward by
the retained elementary XOR. Let `c_i` be the selected source bits, `u_i,t_i`
the radix-`B` compact digits, `p_i=u_i mod 2`, and
`2g_i+a_i` the initial target segment at position `rho+iK`.

Define `H` by

\[
\begin{aligned}
&t_i\le B-2 &&(0\le i<n),\\
&u_i+c_i<B &&(0\le i<n-1),\\
&g_i+(p_i\mathbin\lor c_i)t_i<A &&(0\le i<n-1).
\end{aligned}
\tag{1}
\]

**Theorem.** On `H`, the complete later-source routine toggles exactly the
selected target bits and restores `x,u,t,b` and every other target bit.
`H` is invariant under both the ideal map and the actual word. Its exact
fraction of a complete address rectangle is

\[
\boxed{\Pr(H)=\left(\frac{B-1}{B}\right)^n
\left(1-\frac1{2B}-\frac{(3B-2)(B-2)}{8AB}\right)^{n-1}.}
\tag{2}
\]

Inside the nonsaturated-`t` domain, (1) is also exactly the condition that
the source load has no interior carry **and each earlier-source subcall
individually implements its intended parity flip and restoration**. It is
not asserted to be necessary for the final composite map to be correct.
Some addresses outside `H` are correct. This distinction matters for both
the theorem and its finite checks.

## The inherited one-pass fact

PR1219 establishes that an earlier-source subcall with controls `z_i` and
nonsaturated `t_i` implements its full intended map if and only if

\[
g_i+z_i t_i<A\quad(0\le i<n-1).
\tag{3}
\]

Here is the needed integer argument, repeated to make the composition
self-contained. Divide out the unchanged low `rho` bits of the target.
The remaining modulus is `Y=2^((n+1)K-rho)>=2R^n`. In the first target
rotation, the incoming wide carries satisfy

\[
d_0=0,\quad d_{i+1}=\left\lfloor
\frac{2g_i+a_i+2z_it_i+d_i}{R}\right\rfloor,\quad
a'_i=(a_i+d_i)\bmod2.
\]

Since `B<=A` and `t_i<=B-2`, every `d_i` is a bit. The following compact
load has digits `t_i+a'_i<=B-1`, so it has no carry. Cancelling the two
target offsets, the difference from the intended XOR is

\[
\sum_{i<n}2z_i d_i(2a_i-1)R^i\pmod Y.
\]

Its magnitude is below `Y`, and a largest nonzero term cannot cancel
the smaller terms since `R>=4`. Thus target correctness forces
`z_i d_i=0` for each processed digit. If the target is correct, the final
unload subtracts the original parity vector. The remaining temporary
difference is

\[
\sum_{i<n}d_i(1-2a_i)B^i\pmod{B^n}.
\]

Its magnitude is below `B^n`, and again the largest nonzero term cannot
cancel the smaller ones, including when `B=2`. Hence full restoration
forces all incoming `d_i`, `i<n`, to vanish. Conversely zero incoming
carries give the intended XOR and restoration. Induction in the carry
recurrence makes this equivalent to (3). The last outgoing carry `d_n`
is not read by either compact update and cancels in the completed target
offset; it needs no exclusion. Every back-field swap sandwich restores
the arbitrary back field.

This one-pass result and its dirty-field necessity belong to PR1219,
not to this contribution.

## Composition and the second control vector

The later-source word executes the first subcall with controls `p_i`,
loads `C=sum c_i B^i` into `u` modulo `B^n`, executes the second subcall
with the loaded parities, and subtracts the same `C` from `u`.

PR763's source-load carry recurrence is

\[
k_0=0,\quad k_{i+1}=\left\lfloor\frac{u_i+c_i+k_i}{B}\right\rfloor,
\qquad u'_i=u_i+c_i+k_i-Bk_{i+1}.
\]

Because `B` is even, the old and new parities differ by `c_i xor k_i`.
The conditions `u_i+c_i<B` for `i<n-1` are equivalent to absence of every
interior carry. Under those conditions the second control is
`q_i=p_i xor c_i` for every processed digit. The final outgoing compact
carry is discarded and harmless. The inverse source load restores `u`
exactly, including on bad addresses, because `x` is unchanged.

The first subcall needs (3) for `z=p`. Once correct, it changes only the
target parities, so all `g_i` and `t_i` are unchanged at the second call.
The second needs (3) for `z=q`. The two conditions together are precisely

\[
g_i+\max(p_i,q_i)t_i<A,
\qquad \max(p_i,p_i\mathbin\oplus c_i)=p_i\mathbin\lor c_i.
\]

This proves (1)'s sufficiency and its stated two-subcall characterization.
Composing the flips gives `p_i xor q_i=c_i`. The highest selected XOR
does not change any tested guard or compact digit and completes the map.

The source-load condition and parity formula are credited to PR763. The
new step is their composition with the sharper target guard, followed by
the correlated count in (2).

## Why checking only one call fails

Take `n=2,K=6,G=2,rho=1` and the physical input

```text
(x,y,t,u,b) = (2,124,1,0,7).
```

Here `g_0=31`, `t_0=1`, `p_0=0`, and `c_0=1`. The first-call guard holds,
and the compact source load has no interior carry. It changes the second
control to `q_0=1`, for which `g_0+q_0 t_0=32=A` fails strictly.
The unchanged physical interpreter returns

```text
actual: (x,y,t,u,b) = (2,126,5,0,7)
ideal:  (x,y,t,u,b) = (2,126,1,0,7).
```

The target alone is correct. The dirty temporary is not restored. Using
`u=1` instead gives the matching counterexample to checking only the
second control: the first subcall is then unsafe. These are composition
witnesses obtained from PR1219's one-pass carry mechanism; no new
primitive-defect priority is claimed. Neither predecessor nor the retained
conservative construction asserts the failed one-call implication.

Separately, with `(x,y,t,u,b)=(2,0,0,3,7)` the wide target conditions are
harmless but an interior compact source carry gives `y=130` instead of
`2`. This corroborates PR763 and shows why the source-load condition
cannot be removed when sharpening the target guard.

## Exact density and repair

For an interior digit, the source constraint permits `2B-1` pairs `(c,u)`.
Exactly `B/2` have `c=0` and even `u`, hence inactive `p or c=0`.
The other `3B/2-1` pairs are active. For fixed nonsaturated `t`, an
inactive pair permits all `A` guards, and an active pair permits `A-t`.
Thus the number of admitted `(c,u,t,g)` quadruples is

\[
N_{\rm int}=(B-1)\left((2B-1)A-
\frac{(3B-2)(B-2)}4\right).
\]

Divide by `2B^2 A`. The last processed digit needs only nonsaturation of
`t`, so its fraction is `(B-1)/B`. Independent complete digits now give
(2); target parities and spectator bits cancel from the ratio. Conditioning
on the source-load guard changes the control-parity distribution. Treating
that distribution as independent would give the wrong count.

In particular, for `n=2,K=6,G=2`, the good fractions are

| Predicate | Exact fraction |
| --- | --- |
| Original later-source guard | `81/1024` |
| PR763 source-dependent compact-carry guard, original target guard | `63/512` |
| Two-pass guard (1) | `1971/4096` |

The original guard implies (1): its `u,t` digits are nonsaturated and
`g_i<A-2B`, which is stronger than every required target comparison.
There is no contradiction with either earlier result.

The ideal map preserves every `g_i,c_i,u_i,t_i`, hence preserves `H`.
The actual swap/rotation word `S` and ideal map `T` are bijections of the
finite complete rectangle. Since `S=T` on `H`, they both map `H` onto
itself and preserve its complement. Therefore `T composed with S^-1`
is supported on that complement. The retained repair extracts current
bad records, computes that destination key with the literal inverse,
sorts the full records and keys, and reinserts them into the marked holes.
Merely filling all holes does not establish payload correctness; the
checker includes the wrong-key `T(q)` control from PR763's repair analysis.

Writing `delta=1-Pr(H)`, an explicit union bound is

\[
\delta\le\min\left\{1,\frac nB+(n-1)
\left(\frac1{2B}+\frac{(3B-2)(B-2)}{8AB}\right)\right\}.
\tag{4}
\]

## Cost and scope

All twelve compact swaps and ten rotations remain, including both source
loads, both temporary loads and unloads, both target updates in each
subcall, and their source-dependent offset computations. The highest
selected XOR remains `O(V)`. No dirty field or access is supplied for free.

With `M` records, payload width `P`, address width `L`, and `V=MP`, the
source's complete exceptional-repair allowance remains

\[
O\bigl(V+ML^3+\delta ML(P+L)\bigr).
\]

The extra bit tests and strict comparisons scan at most `n<=L` digits
and fit in that retained descriptor allowance. Extraction, inverse/key
evaluation, full-payload radix sorting, reinsertion, rewinds and cleanup
remain charged. Under the source's `G=4 ceil(log2 p)+6`, `n<p`,
`K/log p -> infinity`, `L=O(p)` and superpolynomial payload assumptions,
(4) retains the same `O(V)` repair conclusion. The selected-bit routine's
existing `O(V*((f log p)^tau+1))` bound and all recursive charges remain;
there is no supplier-profile, binding-constraint or kappa change.

The new predicate is tested only in this package. No production caller,
selected certificate, reservation schedule or upstream file is changed.
Complete field availability, physical tape/compiler realization, recursive
hosting, precision and analytic transfer are not reverified. The written
argument is universal in the stated domain; the finite checks below are
supporting evidence, not a proof-assistant formalization or a proof of the
full multiplication theorem.

## What the finite checks cover

Six complete quotient domains use `rho=K-1`, so the projected target has
`nK+1` bits, including the highest spill bit. They enumerate every low
source mask, compact `u,t`, and projected target. Only the low target bits,
unread source bits and back field are omitted. The offsets are multiples
of `2^rho`, source reads use only the selected bits, and every back-field
swap sandwich is the identity on its original value. Those facts justify
spectator lifting; the omitted addresses are not claimed to be individually
enumerated. The highest XOR is exercised separately on physical samples.

All 723,520 representatives check literal inversion, ideal and actual
guard invariance, the two-subcall characterization, and the full admitted
map. Exactly 293,408 lie in `H`. The separately written quotient model
agrees with the pinned physical interpreter on 1,728 full-field samples,
including dirty back fields, all offset extremes, and 312 admitted cases
where omitting the highest XOR would be wrong. Twelve complete repair
blocks check 24,576 payloads. The deliberate wrong key fills all 17,376
bad holes but misplaces every one of their payloads.

The domain, deterministic sampling seed, stopping rule and predecessor
heads are frozen in [CLAIM.json](CLAIM.json). No optimization or search
for a stronger supplier was performed.

## Credit

Douglas Colkitt supplied the compact-control construction, physical
simulator and repair/tape accounting; OpenAI supplied the original
framework. John-Michael Smith / @jp3isme supplied PR763's compact-carry
law and repair diagnostics. Hanson Sun / @bbMisk supplied PR1219's
earlier-source guard audit with substantial OpenAI Codex assistance.
@martinxxx9's PR1108 supplies the related one-digit boundary analysis.
The present contribution composes the first two guard results and counts
their correlated later-source envelope. Their proof/README bytes are
preserved under `sources/`; no predecessor audit implementation is imported.

Prepared for Hanson Sun / @bbMisk with substantial OpenAI Codex assistance
in mathematics, implementation, verification and writing. Apache-2.0.
No independent human peer review or literature-priority claim.
