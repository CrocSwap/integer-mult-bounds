# Blockwise P104 lifting at linear precision

**Conditional cost reduction; no fast backend, supplier or new kappa.**
Splitting Tekalign's PR3033 residue construction into consecutive smaller
blocks removes its scalar `O(N r²)` bottleneck at `W=Theta(r)`, **if** both
orientations of a complete exact reversible linear backend have saving `a>0`.
The resulting saving is `b=a/(1+a)`, with every backend call, nonlinear pass,
clean-bank cleanup and addressed-array gather/scatter charged. This is a
conditional upper bound, not an improvement to the selected exponent.

The proposal takes PR3033 open question 2. It changes the size of each residue
pass of the identical lifting word. It does not change its translation lattice,
compress defect labels or assume that nonlinear work is a cheap native child.

## Construction and complete conditional bill

Let `N=2^n`, `r<=n=Theta(r)`, and let input component magnitude use `W>=r` bits.
Use maximal consecutive blocks of rank `h` and one genuine shorter tail. For
a rank-`k` block, `g=floor(k/2)+1` and the inherited exact signed identity is

```
x = 2^g q+s,   0 <= Re(s),Im(s) < 2^g,
L_k(x) = 2^g U_k(q)+L_k(s).
```

The literal inverse obeys the same identity; inverse blocks run in reverse
order. All original prefixes need `V=W+O(r)` bits; narrow prefixes need `O(k)`.
The backend premise is a source-preserving exact XOR/additive oracle for
**both** `2^g U_k` and `2^g U_k^-1` on arbitrary Gaussian integer inputs,
with complete time `E(k,V)<=K 2^k V k^(1-a)` and specified workspace. Reversing
a scaled integer overwrite does not supply this interface.

A clean XOR evaluator computes the wide/narrow terms, copies their sum into
an arbitrary dirty target, then reverses every private operation. Compute,
swap, inverse-XOR implements an in-place block. Per local cube it pays **four
backend oracle calls and four narrow passes**, including uncomputation.
Gather and scatter each cube by swaps through one zero local bank; the global
data are temporarily unavailable inside a complete block. The bank returns
to zero. Global addresses are charged once per moved word, local addresses at
their smaller `k`-bit width. The addressed-array bound is

```
T <= C N [V sum k_i^(1-a) + sum k_i² + (V+n) ceil(r/h)]
     + Setup + Wrap + PhysicalRouting.
```

Since `sum k_i²<=rh` and `sum k_i^(1-a)<=2rh^-a`, for `W>=r`, `n=Theta(r)`:

```
T = O(N[W r h^-a+r h]) + Setup + Wrap + PhysicalRouting.
```

At `r<=W<=r^(1+a)`, take `h` near `W^(1/(1+a))` to obtain
`O(N r W^(1/(1+a)))` before the external terms. At `W=Theta(r)` this is
`O(N r^(2-b))`, `b=a/(1+a)`. At `W>=r^(1+a)`, take `h=r` to recover
`O(N W r^(1-a))`. Integer block counts and the tail are included; there is no
rank-padding or free extra pass. A direct Walsh backend has `a=0` and gives
no exponent saving. Substituting this reduction for its own assumed backend
is circular: `a/(1+a)<a` has no positive fixed point.

Extra clean stock is `O(2^h(V+h)+n)` plus backend workspace; retained global
data require `O(NV)`. Affine-address/Z4-quadratic monomial wrappers admit an
explicit Gray compiler using `O(Nn+n²)` addressed bit work, with `O(Nn)` public
table/schedule/history storage and `O(N(V+n))` application. The direct formula
is checked independently. Generic wrappers retain their supplied Setup/Wrap
prices; keeping a quadratic `O(Nr²)` setup would erase the benefit.

[PROOF.md](PROOF.md) derives the identities, dispatcher, exact tail bounds,
clean-work construction, Gray compiler and stopping gates. It is an ordinary
written proof with separate internal specialist review, not a formal-kernel or
independent human proof. No complete physical tape tariff or dirty-helper
hosting is supplied. Physical routing is **unknown**, not assigned zero.

## Exact finite evidence

`blockwise.py` is an executable reversible **macro** reference. Its direct
integer Walsh backend demonstrates exact semantics, not the hypothesized fast
backend. The Python interpreter is not a bit-gate or physical tape trace.
Macro counts include every backend orientation and literal private cleanup.
The tested `inplace=True` dispatcher uses the caller's actual data; the default
read-only convenience wrapper makes a separate input copy. Constant-many local
Python oracle arrays fit the displayed local order, but no Python allocation
peak or physical memory trace is asserted.
The authenticated PR3033/3025 floor source is compared before execution;
source bytes are compiled directly to exclude stale bytecode substitution.

`verify.py` checks all consecutive partitions through rank seven, inactive
axes, every maximal block cap, forward/inverse clean macro invoices, arbitrary
dirty XOR targets and the Gray wrapper compiler. The independent no-import
checker additionally exhausts 2,401 rank-one and 6,561 rank-two signed inputs,
all 127 compositions through rank seven, and signed 4,096-bit fixtures. Its
wrong-floor, insufficient-guard and inverse-order controls fail as intended.
The independent cost checker covers exact integer block selection, tail bounds,
Gray phases and a missing-derivative control. Exact domains are printed in the
three receipts. They are finite computations corroborating the written proof.

```sh
python3.12 -B scripts/research_package.py --package research/p104-blockwise-lifting
```

The registered replay runs both independent checkers, the source-bound macro
verifier and export controls. Normal replay is read-only. `verify.py --out NEW`
requires an absent output. Export tests reject source corruption, bool/int
receipt substitution, missing cleanup, dirty work, aliased ports, missing
inverse-backend tariffs and insufficient headroom. Hosted CI is separate.

## Open next questions

1. Supply the exact backend in both directions at an independently justified
   favorable complete tariff. First bind one native rank-seven call, including
   the `V`-dependent exact-recovery precision. Relative accuracy at the original
   collector request is insufficient. This is the first unresolved gate.
2. Price the actual physical gather/scatter, wrappers and clean/backend stock
   within one named caller. A charged addressed-memory index is not tape
   movement or a hosted-helper allocation. Test whether those extra terms fit
   the displayed conditional allowance before expanding implementation.
3. Only after those gates, emit the whole supplier recurrence and compare both
   suppliers and the outer inequalities. The arithmetic exponent `b` is not a
   kappa, and a scalar speedup at fixed rank does not establish this transfer.

## Provenance and credit

Scientific base `d8e0f83f00191df62174b641e9fff055c357f641`, priority revision 6;
selected-record SHA256
`bb2eaa58647b353f88d0aec2eafb9d30df1be53589231b23e12ceef3e4bad129`.
Canonical investigation:
[Discussion2750](https://github.com/CrocSwap/integer-mult-bounds/discussions/2750#discussioncomment-18983485).
The catalogue card is changed to the concrete PR3033 handoff; TASK.json records
that scope and overlap coverage. Selected records, frozen predecessors and
shared checkers are unchanged.

Credit **Tekalign / PR3033** at
`b12bbaeb5ca2e83f15433fc2dd0ba3b766595281` for the signed split, sharp guard,
Walsh backend, original invoice and open linear-precision question;
**Tekalign / PR3025** at `a544ef068a46f4de3bc47d1d02149cbdc3ba547f` for the
literal paired lift. The preserved source retains **ywz65 / PR2586/2555**,
**Arham Tahir / PR2999**, Nick Petalas and the P104/native/compiler lineage.
The coupled-lattice, inverse-basis, pointwise-code and restricted-update
contributions are adjacent work, not results claimed here. PREDECESSOR.json
binds each copied source byte and original Git blob. The new contribution is
the blocked complete conditional construction and its independent checks.

Ross Richardson with substantial OpenAI Codex assistance, including separate
carry-and-rounding and asymptotic-bounds specialist reviews. No independent
human review is presumed. Apache-2.0; source notices remain in vendored files.
