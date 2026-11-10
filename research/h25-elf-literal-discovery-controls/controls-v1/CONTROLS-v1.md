# Independent literal controls — source only

The builder/harness are authored, not imported/compiled/tested.23 active cases use20 syntheticbuffers, normally1KiB(except the deliberately short header), with independent literal ELF fields/bytes/addresses. S01–S10/S14 are implemented at discovery scope, including absolute immediate and pointer-slot routes, false instruction boundary, overflow/zero-fill/ambiguous mapping/truncation, symbolicbias and source-loader badhash/size.

Two independent reviewer counterexamples are mandatory STOP controls: C01 competing virtual mapping despite file-unique literal, and C02 non-X entry with executable file-offset alias at a differentVA. They are bounded metadata models, not kernel-loadability claims. Oldv1failedmappingrules remain preserved; the harness is now strictly pinned to the separately repaired NEWv2helper.

The harness requires exact absolutev2path and digest from a later reviewed parent launch. It checks source size/hash before compiling those SAME checked bytes into a fresh named module; it does not re-read a path to load changed bytes. Fixturebuilder is also pinned. Only NEW code loads after a separate grant; helper.main and actual GCCpath are never called. All fixture expectations are literal/manual, not extractor-derived.

All requirements remain active under Python-O; no assert statement is used. Eligible runs emit one stdoutJSON with23case/pass/fail counts and optimize mode. Loaderpreflight refusal emitsJSON/exit2; testcasefailure exits1. No network, Popen or original function is involved. Proposed normal/O argv are in CONTROLS-v1.json and are not grants.

S04 checks that interior immediate bytes can remain a candidate without boundary validation. S06 checks nonpromotion only, not instruction semantics. S11(role/reachability), S12(relocationeffects) and S13(privatecall/alias truth) remain explicitly unimplemented conceptualfalsifiers. No semanticchecker, certificatefeasibility or actualimagequalification is claimed.

Frozenhelperv1andv2pins/provenance are retained. Parent independently reviews these sources before any synthetic execution and controls all later passive/native grants. FullC05/fullV03false; originalscore/creditunchanged, physicalcostsOPEN_NOT_ZERO.
