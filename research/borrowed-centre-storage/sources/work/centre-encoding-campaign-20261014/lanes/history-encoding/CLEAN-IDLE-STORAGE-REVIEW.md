# Review of clean query storage in old idle fields

The strict post-backward storage construction passes independent review.
All 512 query rows have distinct old donor fields. No donor has an
original use during its storage interval. The changed bridge reads use
the exact saved query. The second swaps restore every donor and the
original coded source state before the next forward call.

The reviewed proof is
[CLEAN-IDLE-STORAGE.md](../source-domain/carried-owner-reuse/CLEAN-IDLE-STORAGE.md),
SHA256
`1015479b667d70be74121c0abd347cbd8fd72938d932b544675b2236dd18864a`.
Its receipt has SHA256
`294a8f4ac078cebb2545834f307628ca1578c635ca10d6c9d309900997d86ae1`.
The independent checker does not import or execute the producer.

## Exact storage operation

After the complete backward call, selected Y contains the query q in
its actual physical output frame. Let a be the arbitrary old donor
value. The emitted four-operation word is an unsigned exchange:

```text
Y += donor
donor -= Y
Y += donor
donor = -donor
```

It sends (q,a) to (a,q) at the same physical cover class and address.
No equality of logical frames is needed for this complete raw swap.
No native operator or phase changes. If an original bridge reads q,
the modified bridge reads the donor. A second unsigned swap sends
(a,q) back to (q,a).

The checker verifies the whole swap/read/swap word on three independent
formal inputs: q, a, and the bridge target. This gives the original
target minus q and restores the two swapped fields. It imposes no
independence assumption on their values in an actual invocation.

## Independent schedule replay

The checker reads the pinned selected archive and constructs each
event's owner-use set directly. It covers all 482 events, including:

- all 144 local calls and all 69,120 helper occurrences;
- all 160 idle events, including zero-rank remainders and translations;
- all 144 bridges;
- both terminal events in all 16 replicas;
- the final all-live events.

It recomputes every eligible donor set. The donor has no event use in
the post-B, pre-F interval. It is also outside both 704-owner endpoint
calls and outside all 512 query-source families. The independent count
ranges from 3,608 to 10,675 eligible fields per interval. Every selected
donor is in its actual eligible set. All 512 donors are distinct, and
the 512 source-donor pairs are globally disjoint.

The selected bridge acts by

```text
X_dst += coefficient * X_src
Y_src -= coefficient * Y_dst.
```

The original source code at commit
`bce54fb3f895cbe5cd4c0eb477c3afeed100190f`, in
`research/owner-boundary-audit/verify.py`, function `scalar_columns`,
confirms this convention. The independent checker expands the exact
bridge operations from the selected template. It checks that each
parked selected Y has one read and no write in stages one, three, and
five, and no use in stage seven. All 384 replacements retain the
original target family, coefficient -1, cover class, and address.

The checker then follows the physical location of every one of the
14,336 original logical owners through the entire changed schedule.
Capture changes this location by an exchange. An unchanged local,
idle, terminal, or final event must see every used owner in its
original location. Each changed bridge read must follow the recorded
location of its original source. All bridge targets stay in their
original locations. Erase reverses the exchange. Every check passes,
and all owner locations are original at the end.

This is a symbolic event-level proof. It does not treat a native or
scalar event as an identity. It proves that each event receives the
same physical values as before, with the stated read substitutions.
The local source-query identity and its exact original-complex phase
are bound to the separate independent carried-query alias review.

Capture and erase are complete cover sweeps. Capture is after the
whole backward sweep. Erase is before the whole forward sweep. The
construction does not insert partial swaps among local invocations.

## Price and limits

The 1,024 physical swaps contain 3,072 complex unit ADDs and 1,024
complex sign SCALEs. Their real primitive subtotal is 26,624. There
is no added native child, productive field, or physical field. Live
stock remains 14,336, and physical stock remains 14,826.

The complete address, control, precision, and logger bills remain
separate. The saved query retains its original post-B selected-Y
physical frame. The result does not normalize it to a common frame,
carry it through the next forward core, invert the source code, or
complete a data controller. A use during storage must preserve the
query or restore it before swapback.

## Reproduction

Run from the workspace root:

```sh
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/history-encoding/review_clean_idle_storage.py
```

The command exits with status zero and prints:

```text
PASS_INDEPENDENT_ALL512_CLEAN_IDLE_STORAGE
```

The negative controls reject an omitted swap sign, the unchanged old
bridge source, an owner used by the actual idle event, and a duplicate
donor.

The checker is
[review_clean_idle_storage.py](review_clean_idle_storage.py), SHA256
`34583755f14fab094d46546a1cb08da7bde59748c0306cbe06c0b487154f6e06`.
The receipt is
[CLEAN-IDLE-STORAGE-REVIEW.json](CLEAN-IDLE-STORAGE-REVIEW.json), SHA256
`46a66234f6aeb9f98a056301c7652c2dab5577719152a393930f5e1f463d6909`.
