# Verification

CPython 3.12 on POSIX, standard library only. From a clean checkout:

```sh
python3.12 -I -B research/p104-chart431-owned-transport-bounds/replay.py
```

Five shared source and helper files are pinned relative to the package directory. The three exact science inputs are copied byte-for-byte from the exact #7481 package. Six engines use a 30-second cap each and compare regenerated receipts, ignoring elapsed timing fields. The signed price is reconstructed twice. Controls drop one named old ADD in each of the receiver replays, check the zero input and COPY guard for the source, and reject altered input bytes, duplicate path keys and a corrupted retained-product response. The three bounded cases were exhausted with zero unresolved in scope. Each solver and independent replay exits zero. No scientific result depends on a prior temporary pointer or network.
