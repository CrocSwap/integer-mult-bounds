# A shared private bank for the literal phase and egress boundary

This construction was produced by Nick Petalas. New material is Apache-2.0.
The lifetime-sharing argument is elementary. The new result is its explicit
application to the pinned, supplied-interface programs below, with a single
fixed graph and retained physical histories. No global tape minimum is claimed.

## Statement and source premises

Let S be CubeJerry's phase table from PR #7425 at
`8b549ca6557ccbb3017b104b27ea35051f990416`. It has 2,146 locations and twenty
tapes, numbered 0 through 19. Tapes 0 and 1 are HEADER and DATA. Its private
roles are 2 through 19. Its successful-return theorem is retained unchanged in
`sources/phase-PROOF.md`.

Let E be the 17,814-location egress table retained by that package. It has
eighteen tapes numbered 0 through 17, with the same two public roles and
private roles 2 through 17. Its source contract, including successful
retirement, is retained in `sources/egress-PROOF.md`, from
`51ab0539059214fcfa044938c36a0b6017232be5`.

These arithmetic and successful-retirement theorems are cited premises.
This result neither audits them nor extends their failure contracts.
`EXPORT-PINS.json` binds seven exact retained source files by SHA256 and Git
blob ID, with immutable source URLs. No pending source commit is required
by the executable. The metadata's base-ancestry check covers canonical main;
it does not assert that these pending source heads are ancestors of this PR.

Both components use the four-symbol alphabet `{_,0,1,|}`, scanned-symbol
branches, single-cell writes, unit moves, fixed jumps and halt. Their input
is the same actual nine-Gamma layer header

```text
Gamma(p) Gamma(d) Gamma(r) Gamma(D) Gamma(P) Gamma(S)
Gamma(K) Gamma(rho+1) Gamma(w).
```

Assume the source domains: positive parameters, D <= d, 0 <= rho < K,
w >= p+2, and N = P 2^(DK) S r complete Gaussian fields in the canonical
address order. A phase input has signed width w. An egress input has signed
width H = p+2d+4 on the conservative p+d fractional grid. The component
range conditions and complete ownership premises are retained.

Allocate just twenty distinct physical tapes, with fixed origins. Map each
component tape j to physical tape j. The common private windows must be blank
on entry wherever either component will visit, including their offset -1
guards. Opaque exterior may be arbitrary outside those windows. This is a new
allocation contract; it does not merge two existing arbitrary dirty banks.

**Theorem.** One fixed 19,960-location graph on these twenty tapes has two
entry points. Entry 17,814 performs S and returns. Entry 0 performs E followed
by S and returns. On successful calls it preserves HEADER and exterior,
installs output on the original DATA owner, erases the shared private bank
and returns every head. The latter call is subject to the final S range
condition as well as E's domain. All previous visited histories remain charged.

This replaces the direct 36-tape boundary wrapper supplied by #7425 with a
20-tape wrapper. The exact central C service and its format conversion remain
supplied outside this graph. No new kappa, complete layer implementation,
selected-frontier change or complete multiplication theorem follows.

## Graph and execution proof

Place E at locations 0 through 17,813. Replace its unique successful `halt`
with `goto 17814`. Leave its rejecting empty read unchanged. Place S at
locations 17,814 through 19,959, adding 17,814 to every jump and branch
target. Tape indices, symbols and unit moves are unchanged. S's successful
halt remains a halt. This is exactly `compile_shared()` in `shared.py`.

The relocation map on S program counters is a bijection. By induction on
executed instructions, entering at 17,814 produces precisely S's tape actions
and control sequence, with relocated counters. Therefore its successful
contract holds on the twenty supplied tapes.

Entering at 0 produces precisely E's tape actions until its successful halt
would execute. E uses no tape above 17. Thus tapes 18 and 19 remain blank
at their origins. E's successful contract makes tapes 2 through 17 blank
again and returns every used head. Its DATA is now the w-bit packet and its
old H-bit tail is blank. HEADER still contains the same original nine words.
Consequently all S entry premises hold, including blankness of the two
previously unused tapes. The replacement jump enters the relocated S table.
The first argument completes the proof. No copy, scan, allocation, head reset,
or tape-identity exchange occurs at the component boundary.

Counting halt as one instruction, replacing E's halt by a jump costs exactly
the same one instruction. An accepting exit therefore costs exactly
T_E + T_S, using the original complete literal instruction counts.
The entry call costs exactly T_S. There is no runtime dispatch service.

## Historical backing and repeated calls

For physical private tape j let I_j^0 be its supplied historical interval.
Let A_ij and B_ij be the intervals visited by phase and egress in invocation i,
translated to that same physical origin. B_ij is empty for j = 18,19.
The charged history after any finite sequence contains

```text
I_j^0 union all_i A_ij union all_i B_ij.
```

Its visited interval is the hull of this union. In the source programs the
working visits extend rightward from the common origin and its offset -1
guard. Thus their future working extent is the maximum of their per-role
extents, rather than the sum of two separately allocated extents. Initial
backing is still charged. This does not assert that the maximum of total
fresh footprints bounds a sum of per-role historical maxima.

After successful return the entire visited private working portion is blank.
Any previously visited longer tail is already blank by induction. A shorter
next invocation need not scan that old tail; a longer invocation needs the
same explicit ownership/blankness premise for its newly visited cells.
The proof works with fixed tape identities and origins across any finite
admitted successful call sequence. It gives no recovery after rejection or
interruption and no certificate that unseen hostile dirt is absent.

The source complete time bounds add directly. With L=DK and E_h the header
length, one sufficient exit bound is

```text
65536 (2 E_h + 2p + 2d + D + L + w
       + N(H + 2w + 1) + 2).
```

This is the sum of the source E and S bounds, without deleting source access,
commit, return or erasure work. The same shared inventory supports an entry
S call, a separately supplied C/format service that leaves the private bank
retired, and the exit call. Costs and workspace of that outside service are
additional. No total visited-space improvement is inferred from tape count.

## Evidence and executable limits

`verify.py` executes the new graph in `machine.py`, which imports no retained
interpreter. A direct Gaussian tensor oracle supplies the explicitly external
C output and compares the complete boundary with normalized Walsh action.
The executable checks original DATA ownership, all heads, all private cells,
opaque exterior, old-tail erasure, history unions and all sixteen shared
egress roles over changing geometries on the same twenty objects.

Its fixtures are finite corroboration of this composition proof. They do not
replace either cited component theorem. Fixture cardinality is at most 256,
component width at most 64, and each interpreter invocation has a hard
20,000,000-step bound. No generated graph or receipt is written by a replay.
The printed receipt includes source/package hashes and the generated graph hash.

The new Python source has no recursive calls and functions fit within sixty
physical lines. Fixed graph generation and loading two authenticated component
modules are the bounded metaprogramming deviation. Managed Python allocation
is bounded by the fixed graph and fixture/step limits, rather than prohibited.
Four statically listed rejection callbacks are bounded test-only dispatch.
The retained source code is byte-exact and is not refactored to these local
style rules. Warning-strict normal and optimized runs exercise explicit
checks that remain active under `-O`; no optional analyzer is required.

## Open next questions

Bind one actual C producer whose packet, signed headroom, private lifetime and
format conversion meet this boundary. Its cost and allocation are additional,
and this result supplies none of them. Begin with one pinned caller occurrence.
Further tape reduction would require changing a component's simultaneous
liveness; this simple sharing theorem supplies no lower bound or such change.
