# Literal positive central service for fixed native rank

## Result

For each construction time rank `rho=1..9`, the retained program implements positive
`C` on the first `rho` native slots and every encoded column, in the original
six-Gamma/HOME ABI. It checks the actual joint guard `rho*f <= cutoff` while
keeping the caller's original nine-slot geometry and `f` header. It returns the
complete operand, its spectators and opaque exteriors, with all 35 HOME heads
restored and private fields retired on success.

Here

`C = (1/2) [[1+i, 1-i], [1-i, 1+i]]`.

The entry contract supplies the common grid, positive `f,c,P,S,cutoff`, signed
width `w>=2`, complete header and payload, a reserved owner, valid origin and
blank required private work. Every actual intermediate C prefix must be integral
on the supplied grid and fit signed `w` bits. Final fit alone is not enough. One
simple sufficient reserve is initial component divisibility by `2^(rho*f)`,
absolute components at most `M`, and `2^(rho*f) M <= 2^(w-1)-1`. This is a
sufficient condition, not a claim that a selected producer supplies it.

## Complete stated costs

Let `E` be the six Gamma header length, `V = 2 P S c 2^(9f) w` be the complete
payload length, and `F=E+V`. With the fixed table, entry reservation, origins,
and setup already supplied, the 31-tape core has

- time `T_core <= 2^24 (fV+E+1)`;
- historical backing `K_final <= K_entry + 2048 (V+E+1)`.

The 35-tape Gamma6/HOME adapter adds at most `128(F+1)` transitions and
`64(F+1)` backing. A B1 full-bank scatter/return has its separate
`O(R_bank K_bank (F+1))` charge. Fixed `Setup_rho`, table storage, origin
provisioning, typed owner reservation and caller placement are separate entry
charges when they are not already supplied. Prior history is retained; retired
cells do not refund old backing.

This is a direct leaf bound. It does not establish the selected faster nonleaf
rate, a complete caller invoice, or any of the five inherited assumptions.

## Evidence and overlap

`implementation/` is the exact A freeze, preserved byte for byte, with freeze
SHA-256 `5735c401ba981a7af4d3a146eb047d04fa0c87dbf7ed49bd82dc57df8d6cb2ef`.
The author receipt covers all nine fixed-r tables, 233 guard cases including
large cutoff syntax, and a dense rank-three `f=1` packet. `review/root/` contains
the independent review and a separate rank-four execution: its sparse CPU
executed 24,105,820 literal transitions for one fresh rank-four `f=1` packet,
and a closed Hamming-distance tensor kernel checked the exact output including
all spectators. It restored all 35 heads, private bodies and opaque exteriors.
The rank-four receipt is a finite execution, not a numerical replay for every
rank or arbitrary large `f`.

PR #6978 (head
`12e58dfdad9371a26f9978c814779da344fd80b4`) already proves the rank-times-column
algebra, positive orientation, joint cutoff and a coded numerical child. Its
section 7 item 3 leaves the literal numerical lifecycle export open. This
package addresses that physical Gamma6/HOME lifecycle for fixed positive rank.
It does not claim new tensor algebra, all-source MOVE coverage, a monomial join,
or actual selected caller admission. The exact #6978 proof is retained at
`implementation/reference/pr6978-PROOF.md` and pinned by
`implementation/SOURCES.json`.

## Reproduce

From the repository root, the registered commands are:

```sh
python3 -B -W error research/literal-fixed-rank-positive-native/implementation/verify.py
python3 -O -B -W error research/literal-fixed-rank-positive-native/implementation/verify.py
python3 -I -B -W error research/literal-fixed-rank-positive-native/review/root/check_positive_root.py research/literal-fixed-rank-positive-native/implementation
```

The first two commands compare the frozen author receipt in normal and optimized
Python. The third runs the independent root checker against the preserved
implementation. The checks use the Python standard library only. They do not
write result files by default.

## Open next questions

- Bind an actual selected producer output to the full header, owner and every
  C-prefix integrality/range promise.
- Compile the complete source-specific affine, linear, quadratic, global-phase
  and event-owner recipes around this central service with a literal paid join.
- Price typed creation, B1 bank delivery, receiver/return and historical backing
  in the enclosing caller, then compare a complete bill to the selected
  nonleaf tariff.

## Credit and review scope

Prepared for @CubeJerry with substantial OpenAI ChatGPT/Codex assistance. The
root review is disclosed and is not blind, human peer review, or formal-kernel
verification. No new `kappa` claim is made. See [TASK.json](TASK.json),
[SOURCES.json](SOURCES.json), [VERIFY.json](VERIFY.json), and
[PR-DESCRIPTION.md](PR-DESCRIPTION.md) for provenance, verification and the
publication draft.
