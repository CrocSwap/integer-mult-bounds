Run with the same NumPy-capable Python as the main audit:

```sh
python3 -I -O -B research/h6-independent-audit/gate/replay.py
```

This copies only the audit and the 27 pinned source/data files into a new
`/private/tmp` export, then runs from an unrelated working directory. Python
is isolated and optimized, and every new script is checked for zero `assert`
nodes. Git blob provenance stays active through an explicit read-only
`GIT_DIR` pointing at the exact source repository object database. The export
does not contain an independent Git object database.

The gates reject a transitive source mutation, the predecessor's doubled block
count, the reversed compensation-block sign, a corrupt exhaustive histogram,
an inconsistent exceptional-pair summary, the reversed exception sign in the
integer Walsh identity, omitted helper pad, and omitted lifecycle cleanup.
Each rejection must be nonzero with its specific mathematical error, under
`-I -O -B`.

For a final integration refresh after a passed full export:

```sh
python3 -I -O -B research/h6-independent-audit/gate/replay.py --reuse-pass
```

This explicitly reuses the two exhaustive Walsh receipts only after byte
equality of both checker scripts and all frozen source/data inputs. It
records the reused receipt hashes, reruns provenance and the seven remaining
modules, reruns the final unified summaries, and repeats all corruption
controls. `RESULT.json` distinguishes this mode from a full fresh replay and
binds every final audit script by SHA-256. A final equality check confirms the
current scripts match the tested export and all mutants were restored.

The checked scope remains finite H6 audit evidence. It makes no selected
supplier cold-replay, hosted CI, all-port word, admission, or new kappa claim.
