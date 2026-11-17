# Portable independent strict-74 reviewer

The independent reviewer uses a separate exact rational interpreter and checks all 1,501 public rows, before-and-after values of 630 protected private/COPY observations, 74 original erasures, the one COPY guard, and the candidate's signed invoice arithmetic. It rejects an actual sign mutation in a role-46 correction. Its price comparison reuses the retained #7644 directed engine; the reviewer is not an independently authored price engine and does not replace the complete native/signed application.

`review.py` is byte-identical to the original executed review (SHA-256 `8590fbfa198eec5499a55606943110c612dd372f64f92436cefe1cea609dd5dd`); `exact.py` is its unchanged interpreter (SHA-256 `966f98673b8b3e41f16ec54819ce7c230b16bede9446d686fed474ef00399fb2`). `replay.py` is a path/custody adapter (SHA-256 `62459617a2e2bb2663eef830685e10cbedd2e3015c028269bcad5c4230b117ae`): it authenticates and extracts the package's exact source archive into a private temporary directory, regenerates the candidate and invoice, makes a fresh hash-bound temporary input manifest and invokes the original reviewer unchanged. No network is used.

Run on Linux with Python 3.12, supplying a new output path:

```sh
python3.12 -I -B research/p104-original74-main46-on7644/independent/replay.py \
  --output p104-original74-independent.json
```

The relocated adapter passed in a frozen standalone package copy: its 24 stable result fields exactly matched the original review after excluding only the start/end timestamps and elapsed time. The relocated result SHA-256 was `03837b807e40248ae711208d968afe2e34e6f838eb0f5b587517377ddb4e5dc8`; the original result SHA-256 was `400b963f4c997e5fc1aea4ca76952901ad3793c0de2ace9d942955b61284501e`. The relocated run took 47.53 seconds wall, 47.13 seconds user CPU and 121,160 KiB peak RSS under its observed conditions. The original and relocated receipts are separate; this optional replay is not registered in the timed main hook.
