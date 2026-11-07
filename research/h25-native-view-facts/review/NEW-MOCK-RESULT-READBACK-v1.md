# Independent passive readback of the new mocked controls

Actual readback completed at 2026-11-07T00:58:50Z, before the 00:59:31 review cutoff. This reviewer did not execute or rerun any control.

The parent-produced `verification-native/RESULT.json` has SHA256 `5d853d07aaaaccddaa6c071129e3680da4cf6968d435918b167d4de397f4ff07`. It records PASS for the exact two new controls and four ordered steps. Every step has return code 0, known wait, both EOFs, complete true and no recorded errors. The compile steps retained 5,437 and 5,433 bytes of stderr respectively. I read both complete raw warning streams: each contains five misleading-indentation warnings at proposal C lines 154, 239, 493, 643 and 791, with their source notes. The warned sequential statements have the intended reviewed control flow. No warning-free claim is warranted.

The changed-policy control has empty stdout and stderr (both SHA256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`). The native-fact control has empty stderr and exactly these 64 stdout bytes:

```text
unselected native fact control: finite operation oracles passed
```

That stdout has SHA256 `e938ab0debc79b2a1578b478231fb7fa9919cdfd0849d7922e4b75c9d4bc9110`.

The outer `PRE-RETIREMENT.json` records the guard's known wait, return code 0, no errors, and the held timeout group/manager relationship. Its record precedes deliberate group retirement. Exit 137 is the separately specified cleanup terminal, not the four-step test oracle. External prepaid accounting and any physical terminal uncertainty remain the parent's independently retained responsibility.

**ACCEPT the observed component result in its exact mocked scope.** The actual helper/constructor controls passed; no production entry, actual kernel/namespace/LSM/mount probe, original caller or compiler-property query was executed by them. The result explicitly preserves whole-source accepted false and original credit delta 0. It does not discharge the applied Ubuntu binutils source-transfer lemma or the remaining connected parent/compiler/fallback changes.

