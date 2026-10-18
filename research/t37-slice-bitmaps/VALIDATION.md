# Executed validation

Completed on 2026-10-13, on Linux with CPython 3.14.4 and CPython 3.12.3.

The full differential verifier passed under isolated ordinary 3.14.4. It ran
both engines through Jonathan Capalbo's unchanged T37 wrapper, including its
six original negative controls and eight omitted-edit controls. Every
normalized original receipt field matched the retained maintainer replay.
The new complete verification receipt was written to EXPECTED.json.

The documented CLI then passed under isolated 3.12.3 from a relocated,
read-only 24-file closure containing exactly the ten pinned source inputs
and the then-current package/evidence files. Output went outside that tree.
The complete receipt is byte-identical across both interpreters, with SHA-256
`0627fb656754ce70ea7a23428b9049a2dc98ec52b946b0cff41f8b0442c868f3`.
README.md and this validation note were added afterwards; executable sources,
certificates and source manifests are identical to that successful replay.

Executed coverage includes 167,832 separately replayed occupied-state
boundaries, 1,258,074 inserted cells, 74,592 final slice-prefix checks, sixteen
identical-rejection cases, four equivalent accepted inputs, 51,190 primitive
interval cases and 65,536 prefix masks. The deliberate cardinality-only
optimizer fault accepts the constructed invalid gap and is detected by the
comparison. No assertion-only replacement was introduced.

All eleven package tests pass on ordinary isolated 3.14.4 and relocated
read-only isolated 3.12.3. They check source corruption/missing sources,
duplicate and nonfinite JSON, typed and incomplete receipts, missing receipt
provenance, changed patch predicates, corrupt archive-member pins, existing
outputs and retention of the original wrapper's `-O` rejection. The full
audit is deliberately not described as passing under `-O`.

Five alternating complete fresh-process benchmark pairs passed on each
interpreter. Every measured invocation independently admits sources,
materializes immutable inputs and runs the whole original audit and its
fourteen controls. All twenty complete normalized receipts agree. CPU time
uses child-process resource accounting; peak resident memory comes from each
fresh worker's own `getrusage(RUSAGE_SELF)`, in KiB on this Linux host. The
reference/bitmap median wall ratios are 1.190218 on 3.12 and 1.172579 on 3.14.
Peak-RSS medians fall by 22.324% and 22.097%, respectively. The host was not
isolated; caches were not flushed; no timing or memory threshold gates
mathematical acceptance. Preliminary pilot timings are excluded.

All ten source hashes were checked against exact Git objects at base
`407d52ff15b2217b6e22bce44728b4c3907b6515` and refreshed main
`8bddbee377e2f3ce1f1247196c4b290d55767d20`. All five implementation hashes bind
the benchmarked adapter and the verification code. `make selected-record-check`
passed for the unchanged selected rational `1661960547713947 / 10^18`.

Queue refresh through PR999 found no concurrent occupied-cell optimization of
this checker. Existing PR824/849/950/976 concern other kernels. PR991 supplies
a different T37 schedule and additional package/payload checks; its scope
and evidence remain separate. No candidate or checker from that PR
is imported. No new construction, full cold replay, full `make verify`,
whole-frontier timing, formal multiplication proof or independent human
review is claimed. Hosted CI remains a separate status after publication.
