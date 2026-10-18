# Executed validation and limits

Author-checked on Windows x64, CPython 3.12.10 (official portable distribution)
and CPython 3.10.9. Standard library only, one process at a time. No separate
agent, independent human, maintainer or proof-assistant review is claimed.

Canonical main was fetched at entry and again before submission:
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`. Priority revision 4, catalogue SHA256
`d46eb6d5b3e279428753d770653663fbdf1063e55c255ea073d768f344927ef7`;
selected-record SHA256
`10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
The selected binding-only baseline passed, with the complex side binding.
That command is not the full selected supplier replay.

Executed successfully:

```sh
python3.12 scripts/research_package.py --package research/qq16-accumulated-frame-l2
python3.10 -I -O -B research/qq16-accumulated-frame-l2/verify.py
python3.10 -I -B research/qq16-accumulated-frame-l2/independent_check.py
python3.10 -I -B research/qq16-accumulated-frame-l2/test_package.py
python3.10 scripts/research_package.py --package research/qq16-accumulated-frame-l2 --check-only
python3.10 -B scripts/research_baseline.py
git diff --cached --check
```

The registered Python 3.12 hook runs the normal and optimized primary verifier,
the direct-character/matrix oracle and all five boundary tests. Expected markers:

```text
PASS_QQ16_ACCUMULATED_FRAME_L2 sources=200 outputs=96 rank_mass=224 controls=10 no_new_kappa
PASS_QQ16_DIRECT_CHARACTER_AND_MATRIX_ORACLE characters=13631488 basis_coordinates=594 dirty_fixture=1
PASS_REGISTERED_RESEARCH_PACKAGE research/qq16-accumulated-frame-l2 outcome=completed
```

RESULT binds both invoices, including the old-frame 992 rank mass. MAPS and WORD
are regenerated in memory and compared in full. OLD-FRAME-TAIL is required and
likewise compared. The default replay writes nothing. Source-export testing
uses a fresh temporary directory with PATH empty and optimized Python; exact
before/after file bytes agree. Receipt, literal-word and map corruption fail;
source drift rejects before the authenticated scalar-cost function is evaluated.

Two host-environment failures were repaired and rerun: Windows denied a test
rename in its sandbox temp directory, so the missing-receipt test uses explicit
temporary-file deletion/restoration; the newly acquired portable interpreter
could not create nested files in that default temp directory. Setting TEMP/TMP
to a dedicated writable session directory resolved that environment issue.
The registered hook then passed all commands. No mathematical check was disabled.

Coverage is the complete local operator and its stated finite premises, rather
than the complete controller or selected multiplication theorem. Geometry and
the actual input cut are inherited from the pinned QQ16 packet and contract;
the original archived compiler/geometry derivation was not rerun. Physical
cover motion, address work, record capture/retirement, output storage, global
child hosting, recursive precision/tape, all-size admission and the full supplier
invoice remain open. No hosted CI result is asserted by these local receipts.

## Overlap and coordination receipt

The task picker used nonce `d650c685a88fea5fb302527452e1b3c1` and selected
recursive interfaces. The local overlap helper ran and reported missing gh/no
remote snapshot. Connected GitHub searches of QQ16 and QQ16 frame PR bodies,
the public start/handoff/discussion pages and the precise pending sources were
then inspected. The later QQ16 open-PR query returned 38 records. This is a
targeted search, not complete live Discussion/comment pagination or a novelty
certificate. An attempted advance comment on PR2492 returned HTTP 403; it was
not posted and no reservation is claimed.

At the 2026-10-15 13:06 UTC source checkpoint:

| Pending predecessor | Exact inspected head |
| --- | --- |
| PR2492 / ywz65 | `9cc0d4d60819ddd246c9db9549f8ae4a61b68e45` |
| PR2480 / Ross Richardson | `4c0c18ac3a3b080c263478067ee39e8fec6b1f68` |
| PR2470 / Sagar Thakrar | `1b2eee3bf1ec67e68c0b0fa7f47c7b2a66febe56` |
| PR2468 / ywz65 | `baa90ee8176931e697d91a9024114ee2e9a189ea` |

PR2492 supplies the comparison and asks the frame question; its executable was
not imported or rerun. All mathematical execution inputs come from the pinned
main branch. No selected frontier edit, merge or closure of others' work occurs.
