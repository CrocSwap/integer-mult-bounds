# Validation

All direct commands passed under CPython3.12.14 on the internal Mac workspace:

```sh
python3.12 -I -B research/p104-endpoint-funded-split/verify_early.py
python3.12 -I -B research/p104-endpoint-funded-split/verify_native.py --out research/p104-endpoint-funded-split/NATIVE-RESULT.json
python3.12 -I -B research/p104-endpoint-funded-split/verify.py --out research/p104-endpoint-funded-split/RESULT.json
```

The registered manifest reruns these three gates without output generation and compares every receipt field:

```sh
python3.12 -B scripts/research_package.py --package research/p104-endpoint-funded-split
```

Registered replay passed; REPLAY.txt records its output and REPLAY-INTEGRITY.json records the20 unchanged scientific hashes. See APPLICATION.md for the direct complete coverage and remaining assumptions. No hosted scientific pass or independent human/formal acceptance is claimed.

The existing CI navigation correction from PR7131 is retained to fix the onboarding mismatch between the guide and unchanged selected record. Its targeted tests.test_research_current_status.CurrentCiNavigationTests passes. This documentation correction does not select a new bound or repair the separate historical Makefile-drift replay.
