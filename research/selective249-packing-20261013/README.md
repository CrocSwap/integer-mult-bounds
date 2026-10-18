# Selective raw249 endpoint and literal packing

Chi Zhao, with substantial OpenAI Codex assistance. Apache-2.0.

This supplement starts from verified PR639 at `a374528ad44924951514067c3e104b7afb0e54c3` and uses the new raw249 endpoint in12 selected JP8 calls. The remaining59 JP8 calls retain the previous word, and CK remains at time5. Activated times are7,9,12,13,15,20,31,32,40,46,53,61. Both orientations of the new supplier occur, and time0 retains the previous JP8 supplier.

For each selected call, helper25 (raw249) shrinks9→8 and its native local profile changes by `{1:+2,2:-1,4:+1,5:-1}`. The exact native supplier construction and audit are supplied by the enclosing witness. Packing these changed calls yields idle profile `{48:2230}` and paid profile `{1:181970,2:28798,3:32112,4:12104,5:4602,6:288,8:576,48:2230}`. Rank mass remains520704 and deficit2560.

The map was nominated by an exact integer CP-SAT feasibility model on62 owners and248 roles. It assigns every selected role exactly once, enforces capacity, owner-window eligibility, at most one role per call per owner, and exactly12 shortened roles. All other roles retain their owners. It fills every selected owner except the original rank36-gap owner, which becomes empty. The literal validator subsequently checks all35424 roles, including physical family exclusions and compact intervals. Solver status OPTIMAL indicates a solved feasibility problem; it is not an unrestricted optimality claim.

The admission path requires only the Python standard library. The exporter applies235 recorded changed rows, verifies the full structure and canonical decompressed payload, and rejects duplicate-role, width, offset, and family corruptions. It does not rerun a solver. Published gzip hashes authenticate immutable source artifacts; regenerated gzip containers may differ across zlib versions.

```sh
python3 -I -O -B replay_owner_map.py --base-data /path/to/PR639/witness638/data --out /tmp/raw249-export --negative-controls
```

`selective_cp.py` is optional search provenance (OR-Tools9.15, eight workers, seed37,60-second limit; the retained solve took47.8seconds). Running it again may choose a different feasible map. The deterministic exporter, canonical payload pin, and exact enclosing witness are the reproducible acceptance path.

The scalar constructions underlying PR637 are credited to Jeremy Kothe (`jeremykothe2`); inherited sources include Jeremy Diviney's PR627 and Jeremy Kothe's PR629. The raw249 extension, selective dispatch, and ownership work are by Chi Zhao with substantial OpenAI Codex assistance. The conditional exponent requires the enclosing native, owner, moment, and assembly replay.
