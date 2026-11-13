# Local verification of the funded 485/1455 successor

All four registered stages passed in one uninterrupted invocation on 2026-11-13 UTC against the final scientific bytes. No selected record was changed.

```sh
timeout --kill-after=5s 1250s prlimit --as=1073741824 \
  python3 -B scripts/research_package.py --package research/p104-funded-485-1455-return
```

Environment: CPython 3.12.3, Linux x86_64, standard library only for the registered package. The four command limits were 180, 480, 495, 45 seconds. The inherited address-space limit was 1 GiB per process; the outer 1250-second guard includes launcher overhead. Actual wall time 849.56 seconds; maximum reported RSS 662,252 KiB; exit 0. This is the exact local command and observed result, not a hosted-CI result or total consultation cost.

The run reached every stage marker and the final `PASS_REGISTERED_RESEARCH_PACKAGE` marker. The native and signed stages reconstructed their sources and compared every mathematical receipt field with the frozen receipts; only explicit runtime measurements were excluded. Generated copies were temporary, and the package sources and expected receipts stayed unchanged. The complete stdout is included as REPLAY.log, with its resource receipt in REPLAY.time. These execution reports are not mathematical inputs. The log has SHA256 f0c4e3389dc254afe27164d50f35fb11dcf828bbadceec7be375c79ea41cde43.

Final scientific inventory: PACKAGE-MANIFEST.json SHA256 8a1e0a27530fca480b70b8587d2e175180a665b9af8e68d667a4e34dcc374bc8. Candidate canonical SHA256 64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8; compressed SHA256 acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9.

The independently fetched public #7480 source matches all 28 retained input files. All 93 entries of the original Pro packet manifest authenticated before integration. The original positive packet ZIP SHA256 is 686b490ea58f2b832e45c66c501e55eb394d9b1a4256a38b466308ca4004bafa. The frozen receipts and full source closure are included.

## Supplementary independent local check

The separately written #7164 dense exact integer oracle, source SHA256 d114b8ba1e1c093316a66df203875d59c9ef97d267574c2b34a52011d170fd4a, checked all 2,253,001 public input/output coefficients, current coframes, actual COPY, owned chronology and common grid. It passed in 5.010483 seconds, retaining the original owned-erasure premise. Required grid 37748736000, public 1501, owned 68, lifetimes 74, peak 50. This additional local NumPy 1.26.4 audit is separate from the self-contained standard-library registered recipe; no independent human review is claimed. Its raw local receipt is retained by the contributor as INDEPENDENT-POSITIVE.json.

## Retained verification prechecks

The first frontier wrapper precheck timed out at 45 seconds. Instrumentation measured 83.91 seconds reconstructing predecessor constructors merely to read a pure tariff module; the module import and sample arithmetic took milliseconds. The repair keeps full source reconstruction in the native and signed stages and authenticates the exact tariff member through a 29-archive chain for the separate packing arithmetic. The actual provider module SHA256 is 60a743d13f668ef86db4b8215b4d5d04430a671ba6f1fe06d9c1c4c3dfe86da5. The corrected precheck passed in 2.32 seconds. The final complete registered run above passed unchanged; the verification limits stayed 180/480/495/45 seconds and all mathematical checks remained required.

The packing certificate verifies both directed endpoints and the uniform derivative bound on the actual candidate profile. Its fixed-model raw ceiling lies in [0.005811222728, 0.005811222730], leaving more than 0.002164141689 raw headroom. This is a relaxation, not an attainable multiplier or universal ceiling.

## Publication boundary

This records local verification. Exact published head, hosted job conclusions and canonical handoff are reported on the PR and in the contribution discussion. Five inherited framework assumptions remain. Neither local nor hosted success changes maintainer selection.
