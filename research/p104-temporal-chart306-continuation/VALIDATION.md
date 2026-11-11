# Validation

Direct source-aware gates passed under CPython3.12.14 on the internal Mac workspace. The registered manifest reruns all three gates without generating receipts and compares every frozen field:

```sh
python3.12 -B scripts/research_package.py --package research/p104-temporal-chart306-continuation
```

Registered isolated-cache replay passed, matching every frozen receipt field with all 23 scientific hashes unchanged. REPLAY.txt records the run and REPLAY-INTEGRITY.json authenticates the unchanged scientific inputs. No hosted scientific pass or independent human/formal acceptance is claimed.

The existing CI navigation correction from PR7147 is retained to reconcile the guide with the unchanged selected7000 record. Its targeted CurrentCiNavigationTests passed. This does not select a new bound or repair the separate historical Makefile-drift replay.
