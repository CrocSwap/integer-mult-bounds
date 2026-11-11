# Public MOVE fusion contact bound on the retained P104 word

**NO VERIFIED GAIN. Exact conditional κ change 0%.** On the exact
[#7277](https://github.com/CrocSwap/integer-mult-bounds/pull/7277) word,
consider fusing consecutive ascending paid MOVEs of the same public
role. Two fixed-word contact rules both leave zero surviving stock.

- **Delete individually silent scalar contacts.** All 4,732 consecutive
  public MOVE windows contain a nonsilent intervening contact. The exact
  row replay covers 7,721 distinct scalar contacts and 11,548 window
  incidences. Every case has a nonzero change witness. First witnesses
  are 4,553 ADDs and 179 SCALEs.
- **Retime one unchanged ADD after an existing common lift.** All 1,922
  windows with exactly one intervening ADD fail because the other
  operand's first later contact is different from the required direct
  lift. The two lift orders are allowed in this scope. The complete
  first-blocker counts are in [SUMMARY.json](receipts/SUMMARY.json).

Zero cases remain unresolved in each declared scope. The compatible
saving upper bound after support is zero. The comparable conditional
witness remains #7277 at κ = 0.003645669928698.

## Price and fixed-word predicates

The old public itinerary A→B→C must be strictly nested and retains
its original public endpoints and productive targets. The direct A→C
MOVE runs at the second old MOVE clock. For old ranks x and y, the
direct replacement pays rank x+y. The signed price before new work
credits the exact complete 17-copy change
`17(Hₓ + Hᵧ − Hₓ₊ᵧ)` on the #7113 caller, where Hᵣ is the retained
recursive tariff at the pinned old crossing upper. Both price
receipts are written before support tests. The per-role maximum
matching counts each original MOVE at most once. Its directed upper
ignores cross-role interference and grants added ordinary and physical work free.

The complete pre-support upper is approximately 363.3275462698572
raw units for the scalar-silence stock and 199.18473699786647 for
the one-ADD stock. The latter is a subset of the former inventory
under a different contact rule. The two optimistic bounds are separate.

In the first scope, deleting an ADD requires an identically zero source
row and preservation of the fresh-zero token. Deleting a SCALE requires
a zero field row for a nonunit scale. COPY and lifetime changes are
barriers. An independent denominator-safe mod-65521 interpreter
certifies nonzero changes by exhibiting a nonzero coefficient of
the exact rational row change. This provides an obstruction even
before physical phase, ownership, restoration or precision checks.

In the second scope, the ADD keeps its operands and coefficient. It
moves from B to C after both original operands reach C. At the original
ADD clock the other operand's next contact must be its existing
B→C MOVE, which stays paid exactly once. After either individual lift
and before the common ADD, a contact of either operand would block
the edit. The independent reverse scan includes source reads as well
as destination contacts and reproduces the first blocker for every
case.

| First blocker in the one-ADD scope | Cases |
| --- | ---: |
| MOVE to a different destination | 809 |
| ADD source read | 472 |
| ADD destination contact | 459 |
| No later contact | 149 |
| SCALE | 27 |
| CLEAR | 6 |

Controls cover signed cancellation, an altered sign, COPY and fresh
token barriers, a shared old MOVE in the matching, both lift orders,
an intervening source read and a wrong destination. The fixed-word
result leaves changed peer itineraries, compensated scalar edits,
alternate transports and coupled edits open.

## Replay

From a clean checkout with CPython 3.12 and assertions enabled:

~~~sh
python3.12 -B scripts/research_package.py --package research/p104-public-move-fusion-contact-bound
python3.12 -B scripts/check_research_commit.py --package research/p104-public-move-fusion-contact-bound --check-modes --check-source-history
~~~

From a Git-free export, this command also emits all six full receipts
into a fresh output directory:

~~~sh
python3.12 -I -B research/p104-public-move-fusion-contact-bound/replay.py --out fresh-receipts
~~~

[PROVENANCE.json](PROVENANCE.json) pins all eight public inputs by
commit, path, Git blob and SHA-256. [LOCAL-PINS.json](LOCAL-PINS.json)
pins the bundled files by relative path. The wrapper regenerates
the complete deterministic plaintext receipts and verifies their
full SHA-256 values against [SHA256.json](receipts/SHA256.json).
This preserves every proof-relevant field without storing another
copy of the large JSON arrays. The independent engines also check
the literal keys and mathematical evidence. All inputs are bundled,
and the replay needs only the standard library.

## Credit

[#7277](https://github.com/CrocSwap/integer-mult-bounds/pull/7277) at
`ed090b57ed88f8859e5ff4643645099e6ba856ea` supplies the native word
and comparable price. [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
supplies the exact signed 17-copy caller.
[#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298)
supplies the retained tariff and known-good paid-stock replay.
[#7311](https://github.com/CrocSwap/integer-mult-bounds/pull/7311)
supplies the word and contact-authentication engine and identifies
silent-contact fusion as its next test.
[#7308](https://github.com/CrocSwap/integer-mult-bounds/pull/7308)
supplies the signed normalized row interpreter.
[#7259](https://github.com/CrocSwap/integer-mult-bounds/pull/7259)
covers fixed-output verification on older words.
[#7171](https://github.com/CrocSwap/integer-mult-bounds/pull/7171),
[#6765](https://github.com/CrocSwap/integer-mult-bounds/pull/6765),
and [#6529](https://github.com/CrocSwap/integer-mult-bounds/pull/6529)
supply related timed-support, resident-carrier and compensated-fusion
precedents. OpenAI Codex and subagents materially assisted.

## Open next questions

Can a compensated public MOVE fusion change one peer's lift and
preserve the signed action at a favorable complete price? Start by
pinning one changed peer itinerary and bounding compatible savings
over the full word with all additional transports and contacts
charged. Any surviving proposal still needs arbitrary-input signed
forward and adjoint action, ownership, restoration, precision and
complete tape verification.
