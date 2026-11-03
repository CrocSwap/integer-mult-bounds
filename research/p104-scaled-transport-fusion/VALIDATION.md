# Local validation

The direct complete replay and both registered modes pass locally on CPython
3.12.13, macOS arm64. The interpreter is
`/Users/aliromman/.local/share/uv/python/cpython-3.12.13-macos-aarch64-none/bin/python3.12`.
The registered runner reports `PASS_REGISTERED_RESEARCH_PACKAGE`.
Both scientific modes report `PASS_SCALED_TRANSPORT_FUSION_KAPPA_003288299`.

```sh
python3.12 -B research/p104-scaled-transport-fusion/verify.py --write-result
python3.12 -B scripts/research_package.py --package research/p104-scaled-transport-fusion
```

Coverage includes the complete retained constructor, the new literal word,
all 799 scalar columns, 2,939 native maps with exact phases, 208 main adapters,
all 7,488 mixed caller contacts, two rational price engines, compiler and
outer bounds, sixteen named controls, the native wrong-phase control and
the retained source controls. Both engines reject the unchanged source at
the new claim. Package metadata and pins pass.

The public predecessor export and its original member pins are retained at
local ancestor commit `4b09a1a39`. Its files are unchanged. Original authors
and source heads remain recorded in `SOURCE.json` and `NOTICE`.

Committed bytes and owner-execute modes pass for all 18 package files at
`575d3cba682ade7dd9408f913770d1326a57f82a`. The official export passes its
integrity check. Its SHA256 is
`cfe940638d7c4ba8cf9b82bc63fdf96e8103eec39c80df6efe34877ea7a75164`.

Both normal and optimized cold replays pass from that export with an empty
`PATH`, isolated Python, and no Git checkout. An audit hook rejects network
access, process creation and package writes. All 19 exported files, including
the export receipt, retain their bytes and modes. Both runs give the same
stdout SHA256:
`29b386b89e62d4d0c134224bee1667476550187eeca443adfbd41833a130e5cc`.
The measured times are 170.28 seconds and 125.85 seconds. These single runs
are verification evidence, not a runtime comparison.

The optional full-history check declines this shallow checkout. The exact
main base and retention commit are both checked ancestors of the tested
head. The live source pins pass, and the cold export contains all runtime
inputs. A full-history check remains unrun.

No pull request, push, hosted run or independent review is claimed.
The selected frontier and five framework assumptions remain unchanged.
The larger donor objective remains open.
