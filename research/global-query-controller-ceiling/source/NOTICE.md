# Copied source files

Apache-2.0. Preserve the source headers. No copied source file is modified.

- `owned/native.py` and its unchanged `WITNESS.json`: Ali Romman's [PR5383 native construction](https://github.com/aliromman/integer-mult-bounds/blob/4bd6efa51a495a7c7b7754915cf0244e7e60969e/research/kappa-joint-relations-20261023/native.py). Only its pure construction, scalar allowance and exact row replay functions are called. The package's independent pins bind its source inputs. Its original notices credit Cao Yifan, Cinna Davis and zxv.
- `cutoff/exact.py`, `cutoff/native.py`, `cutoff/native_identity.py` and `cutoff/check_certificate.py`: Ali Romman's [PR5369 native tensor package](https://github.com/aliromman/integer-mult-bounds/tree/18354f41de4dc7bfda4692e814cf1d91a6d619ef/research/native-tensor-cutoff). The [complete proof and source credit](https://github.com/aliromman/integer-mult-bounds/blob/18354f41de4dc7bfda4692e814cf1d91a6d619ef/research/native-tensor-cutoff/PROOF.md) retain the native recipe lineage of Jose Manuel/jmbarrancoml, Douglas Colkitt and the listed contributors, plus the classical Fourier, binary Gram factorization, finite-group, Cook and Barrington results. This package uses the positive identity decision and the separately implemented certificate checker. It does not claim those results as new.

The local `price.py` is an adapted version of the [PR5377 complete price engine](https://github.com/aliromman/integer-mult-bounds/blob/c448d13c71908647f968b06cddb795ce7d288139/research/kappa-owned-relation-20261023/price.py). Its notice credits Cao Yifan, Cinna Davis, zxv and Jacob Alan Sussman. The new census debits the eight owned helpers in all 18 full calls and includes every forward transpose wrapper.

Substantial OpenAI Codex assistance was used in both source packages and in this contribution. Source links are fixed commits; SOURCES.json records each copied blob and byte hash.
