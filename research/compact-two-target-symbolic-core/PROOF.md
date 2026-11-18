# The invariant core of the two-target compact switch

## Word and agreement contract

Let the control radix $B=2^g$ and window modulus $N=2^m$ satisfy
$g\ge 1$ and $N>B$. Put $L=2N$. Write the two control fields as
$u=u_0+Bu_1$ and $t=t_0+Bt_1$, taken modulo $B^2$. The data field is

$$
y=b_0+2W_0+L(b_1+2W_1)\pmod{L^2},
$$

with $0\le W_i<N$ and target bits $b_i\in\{0,1\}$. All these fields are
arbitrary at entry. Use the two-target switch of PR #6812 with constant
source bits $(1,1)$. A subcall fixes $u$, sets $z_i=u_i\bmod 2$, and
executes the following four packed updates in order. Each right-hand side
uses the field values at that point.

$$
\begin{aligned}
y &\gets y+\sum_{i=0}^1 2 z_i t_i L^i   &&\pmod{L^2}\\
t &\gets t+\sum_{i=0}^1 b_i(y)B^i      &&\pmod{B^2}\\
y &\gets y+\sum_{i=0}^1 z_i(1-2t_i)L^i &&\pmod{L^2}\\
t &\gets t-\sum_{i=0}^1 (b_i(y)\mathbin{\mathrm{XOR}} z_i) B^i
                                        &&\pmod{B^2}.
\end{aligned}
$$

The complete raw word $S$ runs a subcall, adds $1+B$ to $u$, runs a
second subcall, and subtracts $1+B$ from $u$. The ideal endpoint $T$
keeps both controls and both windows and flips both target bits.

**Theorem.** For every specified $B,N$, the maximal $T$-invariant
subset of $\{x:S(x)=T(x)\}$ is

$$
u_0<B-1,\qquad t_0<B-1,\qquad t_1<B-1,\qquad W_0+t_0<N.
\tag{1}
$$

Since $T$ is an involution, this subset consists exactly of states
$x$ for which both $S(x)=T(x)$ and $S(T(x))=x$. It is sufficient to
analyze each ideal pair together.

## Lower digit and window

In one subcall let $b=b_0$ and $z=z_0$ at entry, and put
$c=\lfloor (t_0+b)/B\rfloor$. The first data update preserves the
lower target parity. The live low temporary is $t_0+b-Bc$, so the
total lower-block increment before reduction modulo $L$ is

$$
2zt_0+z(1-2(t_0+b-Bc))=z(1-2b)+2Bzc.
$$

The output lower target is $b\mathbin{\mathrm{XOR}}z$. The unload
therefore subtracts $b$ in the lower temporary digit. In particular
$t_0$ is restored modulo $B$ whether or not the load carries. The
output lower window is $W_0+Bzc$ modulo $N$.

The load of $1+B$ flips the parity of $u_0$, so exactly one of the two
subcalls has $z_0=1$. Before that subcall the lower target is still
its entry bit. If $t_0=B-1$, the orbit member with $b_0=1$ therefore
shifts $W_0$ by $B$ modulo $N$. This shift is nonzero by $N>B$ and
the inactive subcall cannot cancel it. Thus every invariant
agreement requires $t_0<B-1$.

Now suppose $t_0<B-1$. The net lower increment is the exact lower
bit flip with zero carry into the upper block. The first data
update, however, has an intermediate carry
$a=\mathbf 1_{W_0+z_0t_0\ge N}$. If $h=b_1$ at subcall entry, the
high temporary is loaded by $h\mathbin{\mathrm{XOR}}a$. The upper
block receives zero **net** lower carry and its own signed
increment has parity $z_1$, so its output bit is
$h\mathbin{\mathrm{XOR}}z_1$. The high temporary unload subtracts $h$.
Thus the subcall changes the high temporary modulo $B$ by

$$
(h\mathbin{\mathrm{XOR}}a)-h.
$$

Here $W_0$ and $t_0$ stay fixed through both subcalls. If
$W_0+t_0\ge N$, only the active lower subcall has $a=1$, and its
temporary change is $+1$ or $-1$ modulo $B$. The other subcall
cannot remove that change. Hence $W_0+t_0<N$ is necessary even for
an individual agreement with nonsaturated $t_0$.

## Source carry and upper digit

Assume both lower conditions. The intermediate lower carry is then
zero in each subcall, and the temporary field is restored after each.
The high target flips once for each active high parity $z_1$. In
the load $u\gets u+1+B$, the high digit receives $1$ plus the
carry $\mathbf 1_{u_0=B-1}$. If $u_0=B-1$, the high parity is unchanged
and the two subcalls leave $b_1$ unchanged. Agreement requires
$u_0<B-1$.

Under this last condition exactly one subcall is active in the upper
block. Its entry high target is the original $b_1$, as the other
subcall has no high data effect. The same increment formula used
for the lower digit now gives a high window change of $B$ modulo
$N$ if $t_1=B-1$ and $b_1=1$, and zero otherwise. The $b_1=1$ orbit
member rules out $t_1=B-1$ because $N>B$.

Conversely, under (1), neither subcall has a temporary carry or a
lower-window spill. Each flips its active target bits and leaves
both windows and the entire temporary field fixed. The source load
complements both active parities, and the final source unload
restores the entire source field. Therefore $S=T$ on (1). All four
conditions are independent of the target bits, so their intersection
is $T$-invariant.

The condition $N>B$ is used to see the saturation error in the
restored window. For example, at $N=B=4$ the state $(u,t,y)=(0,12,0)$
and its ideal mate both agree even though $t_1$ is saturated. The
upper-window increment wraps at the full data modulus.

## Translation consequence

An entry translates each digit and each window independently by a
fixed constant modulo its own period. It preserves both target bits
and therefore commutes with $T$. A selector with
$\sigma(T(x))=\sigma(x)$ can use an entry on the ideal orbit of $x$
exactly when the translated state belongs to (1). The selector is
logical. Its preparation, execution and cleanup have separate costs.

For $B\ge4$, four entries cannot cover (1). Extend the finite
adversary of PR #7197 as follows. Label four entries $C,D,E,F$.
Order the first two so that their lower-temporary shifts differ
by something other than $1$ from $C$ to $D$ modulo $B$. Such an
order exists because reversing a difference of $1$ gives $-1$.
Choose $u_0$ to saturate in $E$, $t_1$ to saturate in $F$, and
$t_0$ to saturate in $C$. The translated $t_0$ in $D$ is then
some $v>0$. Choose $W_0$ to become $N-v$ in $D$. The first three
entries each fail a saturation condition, while $D$ fails the
window inequality. Any smaller nonempty menu pads to four by
repetition.

For $B\ge8$ and $N\ge5(B-2)$, PR #6812's five-entry menu applies.
In phase $k\in\{0,1,2,3,4\}$, shift $u_0,t_0,t_1$ by $k$ and
$W_0$ by $k(B-2)$. Each guarded control rejects at most one phase.
The five preimages of $W_0>N-B+1$ are disjoint intervals of length
$B-2$, so the window rejects at most one phase. At least one phase
has all three nonsaturated controls and $W_0\le N-B+1$, which
implies $W_0+t_0<N$. Choosing the least such phase gives an
invariant selector. The exact minimum in this parameter range is
therefore five.

The all-width step is the core identity (1). The menu construction
and the form of its lower-bound adversary are credited specializations
of PR #6812 and PR #7197.
