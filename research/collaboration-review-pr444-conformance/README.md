# Future serialization conformance review

Constructive review informed by chafreaky/OpenAI Codex PR444 at head `8c4242ea61c67827fe62b07b2edc093d7ddfa631`. This project artifact has not been sent to upstream authors. See REVIEW.md for the exact source pin and admission boundary.

The existing immutable [signed75 hosted package](https://github.com/applecrusher/integer-mult-bounds/tree/106f07a9c76ab25c5cb79555f4887cc97022d3d2/research/e8-r740-signed75-idle-hosting-composition) supplies the replay inputs. From this directory, run:

```sh
mkdir -p derived
python3 -B audit_serialization.py \
  ../e8-r740-signed75-idle-hosting-composition/evidence/experiments/stage-search/pr441-signed-retime/full/bit426-source-centres/global \
  ../e8-r740-signed75-idle-hosting-composition/evidence/experiments/stage-search/pr441-signed75-hosting/hosted \
  --assignment-audit assignment_audit.py --out derived/CONFORMANCE.json
```

The receipt should equal CONFORMANCE.json. Fourteen semantic mutations reject; the fresh local-call stream hashes 11,309,184 instructions. A separate canonical schedule hash binds the serialized schedule. The unchanged helper assignment audit is included from that published package. This strengthens the serialized contract and does not admit fully expanded idle/bridge/sigma/selector primitives or discharge the conditional hosting compiler/invoice interfaces.

No changes were made to existing published manifests. Apache-2.0; inherited own helper audit and original supplier attribution retained by the referenced immutable package.
