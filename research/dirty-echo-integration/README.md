# Full-transform and bit-adapter experiment: functional success, no κ gain

The requested integration is implemented as an exact reference experiment.
The multiway echo can be wrapped to transform **every role**, then used in
complete normalized synthetic Fourier transforms and Boolean address-chunk
interchanges. The complete recursive bill rejects this direct adapter as a
route to positive exponent saving—even with free routing and unusually cheap
recursive leaves. The selected result and existing supplier profiles remain
unchanged.

[PROOF.md](PROOF.md) states the all-role identity, transform conventions, complete
child recurrence, scoped cost rejection and two exact boundary counterexamples.
This extends [PR673](https://github.com/CrocSwap/integer-mult-bounds/pull/673),
whose local dirty inverse improvement remains independently reviewable.

| Integration obligation | Result |
|---|---|
| Apply the complex kernel to every physical role | Exact adapter and all-input basis replay pass |
| Apply the bit address interchange to every role | Exact symbolic Boolean replay passes |
| Forward and opposite synthetic transforms | Stored order, signed polynomial twiddles and normalization pass |
| Transform / pointwise product / opposite transform | Exact cyclic/negacyclic convolution passes |
| Complete recursive supplier cost | Rejected: even optimistic moment is at least 3 at saving zero |
| Replace triangular Newton factor by cyclic kernel | Rejected: explicit radix-4 wrong output; boundary rank r-1 |
| Transfer complex cyclic conditioning to bit fields | Rejected: radix-3 kernel is singular on a length-5 GF(4) cycle |
| New κ from this integration | None |

## Reproduce

Standard Python and the source tree at this PR are sufficient. No network,
optional numerical library, compiler, optimizer or historical workspace is
needed. From the repository root, with a new output directory:

```sh
sh research/dirty-echo-integration/replay.sh /tmp/dirty-echo-integration
```

Expected final line:

```text
PASS_INTEGRATION_EXPERIMENT_WITH_REJECTED_SUPPLIER_BILL
```

The cost rejection is a **passed negative research result**, not a passing
supplier admission. The driver checks freshly produced deterministic evidence
against [evidence/FUNCTIONAL.json](evidence/FUNCTIONAL.json) and
[evidence/PRICE.json](evidence/PRICE.json). The functional checker also runs
under `-I -O`; pricing deliberately refuses `-O` because it invokes an inherited
assertion-based rational moment engine.

The completed domain contains 168 complex all-input basis cases, 11,616
symbolic Boolean output rows (covering every independent input bit), six
complete transform/convolution configurations, 40 additional full-transform
basis columns, 59 signed-rotation checks, 12 instruction/interface controls
and six wrong-convolution-normalization controls. Tested transform axes are
(2), (2,2), (4,2), (4,4), (8,2), and (4,2,2), with synthetic record widths 2
or 4. Boolean address radices are 3 and 5, with one through three field pairs
as explicitly listed in the checker. No random search or unreported early stop
is involved. The general claims use the separate written identities, not
extrapolation from these finite cases.

## Why the earlier 12× call reduction does not become 12× κ

One echo restores its borrowed roles. The recursive supplier owes those roles
their own transforms. Completing every output requires three echo shears per
pair of roles. With N(n) echo leaves and W roles, this is 3 W N(n)/2 leaves.
Even granting one child per additive leaf, the normalized moment at saving
zero is 3 N(n)/(2n), at least 6-6/n. It exceeds one for every n>=2.

This closes the direct all-role echo route priced here. It does not establish
a lower bound for every possible integration. The next useful mechanism must
change the paid rank/volume profile or share work across roles so this bill
no longer applies. A faster implementation of the same finite scalar word
can improve constants and cutoffs without changing κ.

For the pinned profiles, κ=0.01 would require both supplier savings above
1/99. The bit supplier alone currently caps the outer saving below
0.001730427469824. At the required 1/99 rate, diagnostic uniform reductions
of the paid moments would need to exceed approximately **2.70% on the bit
side and 2.47% on the complex side**. These percentages include the bit fallback
term and are budget targets, not an admitted construction. The exact intervals
and values at smaller targets are in PRICE.json. The complex comparison is
against pinned PR659, not a claim about newer pending frontier proposals.

## Scope, pins and attribution

The adapters are indexed-read exact-arithmetic prototypes. They implement the
finite operator and normalization contracts; they do not supply a fixed-tape
compiler, a new physical hosting plan, an O(p) precision guard, or a revised
finite supplier invoice. The optimistic cost already fails before those
additional costs. No full bit-circuit rebuild, complete multiplication proof,
practical runtime speedup or new κ is claimed.

[SOURCES.json](SOURCES.json) binds the inherited echo, synthetic-transform
contracts, kernel proof, supplier profiles and rational engines by SHA-256.
Both checkers reject source drift. The exact primary Newton source is also
identified by immutable commit and blob. Base PR673 commit:
`0e35f56cab3cae1eb0a99447135569d687c5695a`; main base:
`66849e1475c930fd7732b1a0067ffee7e1e95f60`.

Credit the OpenAI integer-multiplication and exact-DFT preprints, their classical
Newton/replay sources, Ali Romman (#621), Chafik Boukhalfa (#628), the credited
DreamingOfClouds/eumemic bit lineage (#589), and Jeremy Kothe's complex witness
(#659, with icekylinx and the owner/construction lineage). Their existing notices
remain in force. Concurrent #677 treats a different native ADDRESS shear and
query minimum; it is context, not a dependency. #670/#674 improve scalar XOR
counts without changing the paid histogram, consistent with the distinction
made here. The submission does not reopen their searches or claim their results.

The final queue refresh also found Dillon Amburgey's
[#689](https://github.com/CrocSwap/integer-mult-bounds/pull/689) at
`0dedef12f05f9a06faf9d4e1c8b1462c0e3bff3a`, which refines balanced ternary
block placement in the pinned PR673 echo without changing its scratch use.
This package leaves that generator unchanged. The all-role cost lower bound
allows any group ordering, so the local refinement does not remove this
particular obstruction. Greer Guthrie's
[#679](https://github.com/CrocSwap/integer-mult-bounds/pull/679) at
`dce137e540acd2b689281afe222cd32c0ec1f1ae` separately prices selector-batched
children with their joined volume. Neither proposal is a dependency of this
adapter or its finite evidence. Queue inspected through #693; newer pending
complex values are not substituted into the pinned comparison.

Prepared for **@androolloyd with substantial OpenAI Codex assistance**.
Apache-2.0. Independent arithmetic means distinct program paths, not independent
human review or proof-assistant certification.
