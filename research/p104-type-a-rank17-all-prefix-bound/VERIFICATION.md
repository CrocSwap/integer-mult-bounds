# Verification

`replay.py` authenticates the exact input and verifier paths, reproduces the forward and reverse sweeps and verifies the directed comparator quote. Each scientific child has a 30-second cap and uses only CPython 3.12's standard library. The recorded forward and reverse scientific wall times were 0.07 and 0.33 seconds. Both exited zero. The verifier compares the deterministic receipt fields and omits only the reverse measured elapsed time. In addition to the inherited Laurent controls, it checks pure even and odd passing columns, mixed phase, mixed body, a foreign body, empty body, duplicate keys and altered input rejection.

- `receipts/FORWARD.json` records all per-root interval classifications, first term witnesses and complete forward endpoint recovery.
- `receipts/REVERSE.json` records the same classifications, separate body-failure accounting, old role10 and new role28 focused controls, and exact recovery of the initial columns.
- `receipts/PRICE.json` records the exact directed #7481 gross bracket and the negative net upper bound when adding one rank-one job per port.

Registered replay, exact committed bytes and modes, source-history check, read-only Git-free export replay and 27 local onboarding tests were checked at package preparation. Hosted checks are separate.
