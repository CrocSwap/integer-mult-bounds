# Verification and freshness

Scientific code, inputs and receipts were frozen at the conservative checkpoint
**2026-11-02 04:21:00 UTC**. Session start: 03:59:32 UTC. The 60-minute ceiling
is 04:59:32 UTC; at least fifteen real minutes after this freeze are reserved
for verification and handoff. Final elapsed time belongs in the public handoff.

## Passed checks

- CPython **3.12.14**, standard library only. The registered manifest runs both
  standalone checkers with `-I -W error -B`, normally and with explicit `-O`.
  Metadata validation and all four registered commands passed.
- Primary and independent reverse oracle agree on all 770-by-770 rational
  public coefficients. The primary additionally binds the actual dual prefix,
  response bridge, retained source events and ordered inverse suffix.
- Six primary semantic/interface controls reject; four independent literal
  omission controls supply concrete unequal coefficient witnesses.
- A fresh package-only copy, without Git, used an empty executable PATH and
  read-only files/directories. Both checkers passed normally and optimized;
  file inventories before and after were identical. The two primary runs took
  1.504/1.338 seconds and two oracle runs 2.489/2.669 seconds on this host.
- In that isolated copy, corrupting each input word and BASIS byte stream was
  rejected by **both** checkers at source authentication (six controls).
  Changing a retained integer to a JSON float was rejected by each checker
  at typed receipt comparison (two controls). Originals were restored and
  their complete inventories rechecked. These controls do not mutate the
  published package.
- A separate mathematical reviewer inspected matrix order, arbitrary-input
  response decomposition, dirty-carrier cancellation and literal bridge checks.
  The review corrected an initial checker conflation of 381 full channels
  with 562 total helper roles before the final receipts were retained.

## Submission checkpoint

Canonical main was fetched again at submission and remained
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. Priority revision is 8 and selected
record SHA256 is
`9b8d0eea95b3bf0dfcb7938a732a6439b87a2685dec2a5ab9e525b3b34debbfa`.
The selected record's PR6030 takes precedence over stale PR5599 text in some
orientation pages; no selected or priority file is edited here.

The PR6353 head remained `db2a20bc50bc7a8a4db931af85ce7f012ae7c3c3`.
Open-PR title/body pagination returned 100/100/100/21/0 entries, 321 distinct
open PRs, completed before the observed 04:21:49 UTC checkpoint. This is not
an atomic snapshot. Live visible #1166 and #5645 posts were reread; no separate
matching audit surfaced. The offline overlap helper also ran against those
records. Sparse local notes, closed historical code, complete Discussions and
unpublished work are not fully covered; absence of a match is not novelty proof.

## Limits

This is independently implemented finite rational evidence. It is not a
maintainer acceptance, formal theorem, native-phase audit, physical-erasure
proof, caller or complete-price replay. Hosted CI, publication transport and
human acceptance are separate from these local scientific results. The
selected frontier and all five framework assumptions remain unchanged.
