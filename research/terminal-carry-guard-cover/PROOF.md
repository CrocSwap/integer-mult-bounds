# A terminal-carry refinement of the translation cover

## Statement

Let r>=1, B=2^G>=4, N=2^m, q=3r-1, q<=B and q(B-2)<=N.
There are r disjoint target blocks, indexed by increasing bit position,
each comprising one bit b_i followed by
an m-bit window W_i. Two separate dirty control fields u,t have at least r
base-B digits. Additional high control digits and exterior data are arbitrary.
All arithmetic on each complete control field is modular at its declared width.
Sources f_i(y) are arbitrary Boolean functions of data excluding every active
target bit. They read neither control field. They may read every guard window
and exterior data bit.

Use the four live-digit updates of PR4100 CRT.md section 4, then load
u += sum f_i(y) B^i between two executions and subtract that same expression
afterward. Updates read the digit after the preceding update, as clarified
by unpaidmoon's PR4321. The relaxed sufficient product predicate is

    t_i <= B-2 for every i;
    u_i <= B-2 for i < r-1, with u_(r-1) unrestricted;
    W_i <= N-B+1 for i < r-1; the highest window is unrestricted.

On this predicate the complete macro XORs f_i(y) into each target and restores
all other fields. The smallest coordinate-translation menu covering this
predicate has exactly 3r-1 entries. Each entry may translate each guarded
coordinate independently modulo its own period. The terminal u digit and highest window need
no translation. This is optimality for this product predicate only.

## Why the terminal digit is free

For a nonterminal block write L=b+2W, tau=t_i and z=u_i mod 2. The first data update
gives L1=L+2z tau. Its maximum is 1+2(N-B+1)+2(B-2)=2N-1 and its minimum
is nonnegative. Thus it cannot affect another block. Its parity remains b.
The t load changes tau to tau+b<=B-1, with no carry into another digit.
The next data update gives

    L2 = L1 + z(1-2(tau+b)) = 2W+(b XOR z).

It is also inside the block. Unloading (b XOR z) XOR z=b restores t
without any borrow. For the highest block, the bound on L1 is unnecessary. It may overflow
into exterior high data, or wrap at the complete data field boundary. This
cannot affect any lower target bit. Its parity is still b, and the same
cancellation gives L2=2W+(b XOR z) modulo the complete field. The endpoint
changes only that target bit, so its high data also return. Lower blocks
remain confined and cannot interfere with this calculation. Thus the packed
statement holds with the highest window unrestricted. In particular,
one execution reads u only through its low r digit parities and leaves u
unchanged, regardless of saturation in those digits.

Between executions each f_i has its original value c_i, because the first
execution changes only active targets. For the control load, set k_0=0 and

    u'_i = u_i+c_i+k_i-B k_(i+1),
    k_(i+1) = floor((u_i+c_i+k_i)/B).

The lower r-1 digit guards imply k_1=...=k_(r-1)=0. Since B is even,
parity(u'_i)=parity(u_i) XOR c_i for all represented active digits,
including i=r-1. The outgoing k_r may modify inactive high digits, or wrap
out of the field if its width is exactly r digits. Neither affects any
active parity. The second four-update execution therefore leaves the targets
b_i XOR c_i and restores t and all windows. Source values at unload are
still c_i, since they omit all targets. Subtracting the same packed integer
restores the *entire* u field, including any inactive high digits or modular
wrap. Arbitrary exterior data are preserved.

John-Michael Smith's PR763 already proves the harmless terminal carry for
fixed source bits in its different later-source caller. Hanson Sun's seed73 audit and its PR1219 predecessor already leave the
highest window unguarded for a fixed-bit source. Both terminal cancellation
facts are credited to that lineage. The step here is their composition
with arbitrary target-omitting sources and the exact relaxed translation
cover, rather than a claim of new local cancellation identities.

## Optimal cover of the relaxed predicate

There are 3r-2 guarded coordinates: r t digits, r-1 u digits, and r-1 windows.
Each has a proper good subset. Given any s<=3r-2 translations, assign a
different guarded coordinate to each entry. Set that coordinate so the entry
sends it to its maximum value, B-1 or N-1. These independent choices defeat
every entry. The terminal u digit and highest window are irrelevant. This proves the lower bound
3r-1 for arbitrary coordinate constants, including menus shifting that digit.

For attainment let d=B-2 and k=0,...,q-1. Add k modulo B to every guarded
control digit and kd modulo N to every guarded window. Leave terminal u
and the highest window unchanged.
A control digit forbids at most one phase because q<=B. A window's bad
preimages in phase k are exactly

    [N-(k+1)d, N-kd-1].

These q intervals are pairwise disjoint because qd<=N. Each window therefore
forbids at most one phase. The 3r-2 coordinates forbid at most 3r-2 phases,
so at least one of the q phases is good. This is the same standard coordinate
adversary and disjoint-interval method used by Nick Petalas's conservative
3r+1 cover. The new predicate removes two guarded coordinates from that model.

## Source transport and selector

Let D_k be an attaining translation, and D_(k,y) its data part. The raw
translated macro must use f_(i,k)=f_i composed with D_(k,y)^(-1). Translation
preserves target bits, so transported sources still omit them. Choose the
least good phase sigma of the original controls and windows. Then

    D_k^(-1) S_(f_k) D_k(x) = T_f(x), k=sigma(x).

The selector depends only on coordinates restored by T_f. Thus its logical
owned record can be uncomputed by recomputing sigma after return. This is a
logical interface, not a physical clean-selector implementation. No tariff
for selector production, translations, source transport, shuttles or cleanup
is supplied. Fewer menu entries alone implies no time or exponent saving.

## Boundary

The theorem is uniform in the displayed integer parameters. Finite checks
corroborate it, not prove its quantifiers. No all-size selected assumption is
discharged. This alternate CRT interface does not establish PR4100, produce a
selected P104 caller, or change the selected conditional exponent. The proof
needs disjoint blocks, live t digits, omission of *all* targets by sources,
and the lower source-digit guards. It does not optimize the actual agreement
set, which may be larger than this sufficient product.
