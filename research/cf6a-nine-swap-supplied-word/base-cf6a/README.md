# K372-4에 382·770·세 필드 보정을 결합한 cf6a96f5

κ=**0.0037241804545**에서 새 16회 호출 장부 비용이 더 낮고, 0.0037241804546에서는 더 높다. κ=0.00374에서는 기준 비용이 여전히 더 낮다. 모든 수치는 공급 조건이 붙은 실제 장부 비교다. [네 가격 판정](PRICE-SUMMARY.json) · [입력 장부](INVOICE.json)

맥북의 K372-4가 보존한 EARLY 탐색 기록에서 hit 13은 382의 3→480→849 경로를 3→849로 줄이고 44번 필드에 429를 더하는 편집이다. 5080에서는 K372-4 행에서 네 변화 방향과 선후 전달을 계산했다. 자유 기저를 처음 선택했을 때 non-full 출력 902·903·926·927을 요구해 구성이 실패했다. 다음 계산에서 rank-4 Woodbury 역식과 맥북의 서로 다른 U·V 허브 정산을 사용해 prefix 241개와 tail 288개를 합성했다. 1,501개 임의 입력의 목표 행을 대수적으로 확인한 뒤 실제 WORD의 정수 행과 CLEAR도 검산했다. [최초 선택의 실패](../MAC-C4-HIT13-1/BUILD.json) · [다른 기저의 성공과 출처](../MAC-C4-HIT13-LIFT-2/BUILD.json) · [382 단독 유한 검사](../MAC-C4-HIT13-LIFT-2/FINITE/AUDIT.json)

그 382 후보에서 1517/770의 실제 행과 주입 위치를 다시 구하고 236·544·1000의 삼각 보정을 적용했다. 382 단독과 1517/770 단독은 이 장부에서 같은 가격 구간을 보이지만 실제 수정 위치와 기저가 다르다. 여기 적은 수치는 최종 바이트에서 다시 계산했다. Mac의 여섯 원래 체류 기여, #21·137이 공유하는 ADD 하나, #99·601의 연결, Ali Romman 및 OpenAI Codex의 #7663 기저와 경계를 유지한다. [770 결합](../MAC-K3724-H13-ROLE770-1/BUILD.json) · [최종 구성](BUILD.json) · [선행 5080 결합과 원 저자별 계보](../MAC-K3724-ROLE770-TRIANGLE-1/README.md)

| 검산 대상 | 결과 |
|---|---|
| 실제 WORD | canonical SHA-256 `cf6a96f5b912a70dea4767ab05f0a47a89318345f702f3412c7bd00572c9a4bc`, 총 151,075개 이벤트 |
| 이벤트 | ADD 140,280, SCALE 4,172, MOVE 6,153, INIT와 CLEAR 각 235 |
| 유한 행·생애 | public 1,501, CLEAR 증인항 1,135, 영행 CLEAR 42, 예약 68개 중 사용 53, 최대 동시 생애 51 |
| 정수 grid | 관측 분모 최소공배수 225·2¹⁴, 기약 분자 최대 20비트, 공급한 감사 grid 225·2⁴⁰ |
| ordinary | raw 상계 730,358,496, signed-source-unit 734,073,440, 단가 32를 대입한 서비스 수식 79,758,336 |
| precision | height 339, mass 662, context 1,324 |
| 16회 호출 | ambient 137, fresh helpers 17,616, productive 21,152, paid 102,000, 접촉 경계 12,800 |
| 새 기저 | 3→849에서 512 forward·512 adjoint의 signed Pauli·절대위상 일치, 잘못된 위상 대조군 거부. 나머지 세 변경 기저는 같은 순서의 선행 증거 재사용 |

[정수 행](FINITE/AUDIT.json) · [CLEAR](CLEAR-RECONSTRUCTION.json) · [ordinary](ORDINARY.json) · [precision](PRECISION.json) · [주소와 유료 발생 위치](PHYSICAL.json) · [새 기저 실측](NATIVE-NEW-3-849.json) · [측정 후 결속](NATIVE-BINDING.json)

**경계.** K372-4의 입력 740·1356은 1098, 출력 289·1052는 234다. 이전 325/1087 경계와 함께 이 포트의 공급·회수·단가를 가정한다. 전체 fixed-tape domain, common-U 전체 extent와 reset, 실제 반올림을 포함한 16회 호출과 H/Kstar, 외부 복구와 제공자 승인은 열려 있다. 상속된 native all-columns, owned erasure, uniform compiler, precision/tape, analytic recovery를 가정한다. 원 가격 CLI는 선언 장부 산술을 검사한다. 5080의 행·증인·결합 검산 코드 및 고정 해시는 이 후보를 재현하고 소스를 식별하는 용도다.

**출처.** SYLforge #7637, DreamingOfClouds #7641 원안 및 #7658, Clear1nsight의 24비트 계수 51개 분할 보고와 #7660, Ali Romman #7663, Rohan Arun 등의 #7113 caller, CubeJerry 등의 선행 공급 모형을 보존한다. #7641의 0.0037136318149와 51개 수정 후 같은 값은 각 저자의 보고다. 이번 독립 유한 검사의 대상은 맥북 전송에서 파생한 실제 결합 WORD다. [#7641](https://github.com/CrocSwap/integer-mult-bounds/pull/7641) · [51개 분할에 관한 저자 보고](https://github.com/CrocSwap/integer-mult-bounds/discussions/7111#discussioncomment-19691406) · [#7663](https://github.com/CrocSwap/integer-mult-bounds/pull/7663)

**재현.** 후보 폴더에는 실제 WORD, 증인, 유한 행, 장부와 서비스 결과가 있다. 연구 루트에서 원 프로젝트의 가격 판정 하나를 직접 실행하려면 다음 명령을 사용한다.

```powershell
python -I -B ../../scripts/evaluate_recursive_power.py runs/BFEB-CALLER16-CANDIDATE-2/INVOICE-ZERO.json runs/MAC-K3724-H13-ROLE770-TRIANGLE-1/INVOICE.json --exponent 0.99626 --bits 256
```

이미 설치된 Python 3.12 표준 라이브러리로 실행했다. [382 측정 인자](../K374-K4-RANK-FOUR-13/hit.json) · [유리수 역식과 맥북 함수의 정산 인자](../K374-K4-SHEAR-AND-LIFT-2/woodbury.json) · [4개 기여의 실제 재구성 인자](../K374-H13-AND-FOURWAY-1/combination.json) · [유료 기저 검사 인자](../K374-FOURWAY-3-849-COLUMNS-1/geometry.json)
