# Sequential decoder-side bookkeeping supplement

This supplements the frozen representation proof at `../PROOF.md`. For the
same source/event/service contract, it supplies sorted binary tables with
explicit head movement, paid request/reply tapes, fixed reusable roles,
bitwise register arithmetic and a conservative all-size clock proof.

The complete literal `Plan.run`, including every group and round and B row
initializations per decode, has decoder-side bookkeeping below BN^350 tape
steps. The explicit comparison N^512<=9^N for N>=2^16 and the actual field
geometry W/B>=9^N then put this local bookkeeping below W. Production uses
h>=3000. This does not price Plan/event generation or native/leaf/zero-service
bodies, including service-side dispatch and numerical erasure.

- `COST-PROOF.md`: full statement, source binding, machine model, operation
  ledger, historical storage, bitwise lowering and explicit cutoff.
- `tapes.py`: binary cells, physical head motion, complete sorted-table
  scans, streaming initialization, rewrite/copy/clear and persistent peaks.
- `controller.py`: decoder and complete Plan.run replay with these tables;
  paid callback metadata roundtrips and bounded resident service slots.
- `registers.py`: bitwise copy/compare, ripple arithmetic, product and
  restoring division, with actual local head movements.
- `check_sequential.py`: source equivalence, warm role reuse, complete
  group/round replay, negative controls and exact arithmetic bounds.

The reference's complete host calendar images and expanded port lists are
correctness adapters, not the claimed tape workspace. The physical method
stream-copies an already encoded supplied calendar and transfers expanded
ports one at a time into separately charged service input storage.

The reference measures table cell actions and separately reports a proved
conservative register/adapter upper bound. It is not a measurement of
CPython memory or production execution time. Universal conclusions rest
on the written proof and inherited complete source census, not small tests.
The only resident reference dictionary in the decoder holds the explicitly
excluded callback bodies; it is not free physical storage.

Run from the repository root:

```sh
python3 -B research/retimed-decoder-control/sequential/check_sequential.py --output /tmp/retimed-sequential.json
python3 -O -B research/retimed-decoder-control/sequential/check_sequential.py --output /tmp/retimed-sequential-optimized.json
```

Expected marker: `PASS_SEQUENTIAL_DECODER_BOOKKEEPING`. Standard-library
Python 3.11 or newer suffices. No production-sized Plan or numerical payload
is constructed. This is a separate scientific addition; the original
representation proof, original source pins and original receipts remain
byte-for-byte unchanged.
