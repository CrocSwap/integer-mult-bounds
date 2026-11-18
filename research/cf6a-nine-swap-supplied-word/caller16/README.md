# bfeb native를 사용하는 실제8+8 caller 연구 후보

실제 native는 `../COMMUTING-CANDIDATE-1/WORD.json.gz`의
bfeb95d0959b8345d34424d6c2d998b0c3ebca70db54739d12b02cb8ee669f11이다.
원본 word/certs는 바꾸지 않았다. 새 caller는 canonical
953168feae5af41e6d782dcecf603d6132cc6f519b4358ab65e96ea331e50272,
68roles/16stages/4192events, 파일SHA256
62d94fb992acab0a71c3d12f22be4ce63f4f65e5cbe3f420b93aa1393ffa8dcf이다.

원 저자는 Rohan Arun 및 OpenAI Codex, 상속된 기여자들이다. #7113 commit
07a76c5e2738882c0cb322278e56f6cae3c9885d의 실제8+8 A root,
short_dyadic_seam.py의8+8 비가환 B tape, elementary lowering와 A/B emission을
선택하여 사용했다. 원문/Apache-2.0은 `../../review-swap/vendor7113-caller16/`에
보존했다. #7112는 native 공급자이며 등록된16-stage caller로 취급하지 않는다.
BUILD.json에 source blobs/SHA256 및 counted in-memory tape edits가 있다.

이번 B idle 그룹은 중간 cut에서 양쪽 phase의 passive paired subspace를 exact rational로
묶어 구성했다. stage-local 잔여 projector 및 source frame 정당성을 실제 확인했다.
앞6개 block-LU 기각과7번째 parameter[-4,-1,-1,3,0] 성공을 BUILD.json에 보존했다.
이는 source가 준비한8+8 탐색을 좁게 구성한 것이며 보편적 caller 최적성 증명이 아니다.

| 증거 | 실제 상태 | 범위 |
|---|---|---|
| BUILD.json | 생성 완료 |68roles/4192events; scalar lowering 및 passive projector |
| EXACT.json | PASS | 임의입력 전역 signed Laurent endpoint; ADD 변이 거부; 실제 events invoice |
| CALLER-GRID.json | PASS |2025·2^325; 모든 pre-product 나눗셈 exact;153295 divisions |
| INVOICE.json | 구성 완료 |새16caller events와 실제bfeb native 잔차를 결합 |
| PRICE-LOW/HIGH.json | 공식 CLI256bit 판정 |κ=.0037180102482에서 new_cost_lower, .0037180102483에서 new_cost_higher |
| PRICE-MILESTONE/TARGET.json | 두 지점 미달 |κ=.00372/.00374에서 new_cost_higher |
| ORDINARY.json | invoice_match true |raw795101344, signed-source-unit798816288; literal numerator24bits |
| finite service counts | 산술 대입 완료 |constant32 가정 하114667008 services; 적용성 별도 PENDING |
| PRECISION.json |새caller forward/adjoint 계산 완료 |height346, mass bits718, c1436≤4096; 동일native exact bounds 명시재사용 |

실제16 invoice의 가격 구간은 앞선 Decimal 모델과 일치한다. 이것은 인접 두 유리수
지점에서의 방향성 구간 판정이며 전 구간의 유일한 교차 증명은 아니다. 기존17-stage의
κ 구간(.0037175928262,.0037175928263)보다 개선했지만 중간목표 .00372와 목표 .00374에는
못 미친다. signed-source-unit ordinary도 기존882209528보다83393240 감소했다.
source 저자의 다른 #7641 bill878834276과512000 정의차는 오류로 단정하거나 이 후보의
장부와 같은 정의로 합치지 않는다. native104→128 단가 대체도 raw source 단위에 몰래
섞지 않는다.

PRECISION.json은 같은 bfeb word/hash/grid10125·2^21 및 owning envelope/grid source
bytes에 결속한 기존 native M/Sigma/Gamma exact 값·witness·adjoint와 grid 증거만
재사용했다. 기존17caller의 positive upper는 사용하지 않았고 새68role/16stage caller의
forward/adjoint를 실제 계산했다. native 전체 grid replay를 중복 실행하지 않았다.
3536개 physical-main inputs와17616개(stage,helper) arbitrary inputs는 source envelope의
새 census이며, 실제 주소/owner allocation을 만들고 검증했다는 뜻은 아니다.

native의 scalar/CLEAR/native phase 증거는 동일 bfeb의 FINITE/NATIVE/GRID를 명시적으로
재사용했다. 새caller의 구체 물리 label/주소 배치와17→16stage 조합 전역 정합은 아직
완료된 signed application admission이 아니다. 새 공급/경계 및 독립(stage,helper)
arbitrary-input allocation은 명시적 조건이다. 상속된 framework/common-U/whole extent
reset/child/tariff/compiler/provider 조건과 H/Kstar·rounded exponent margin·constant32
서비스·전체 tape/outer는 해결됐다고 주장하지 않는다.

우리 working caller/해시 pins/감독 영수증은 재현·출처·도구 증거이며 다른 연구자에게
우리 보조 검증기 통과를 프로젝트 필수 조건으로 강요하지 않는다. 공식 인정·무조건
곱셈 성과·독립 사람 검토·목표κ 도달을 주장하지 않는다.

재현은 `research/final233-k372`를 현재 디렉터리로 두고 새 output 이름을 사용한다.
기존 Python3.12 및 표준 라이브러리만 필요하며 추가 설치가 없다.

```powershell
python -I -B -m unittest discover -s review-swap -p test_caller16_build.py
python -I -B -m unittest discover -s review-swap -p test_caller16_audit.py
ruff check review-swap/caller16_build.py review-swap/test_caller16_build.py review-swap/caller16_audit.py review-swap/test_caller16_audit.py
python -I -B review-swap/caller16_build.py --max-attempts 8 --output-dir runs/BFEB-CALLER16-REPRO
python -I -B review-swap/caller16_audit.py --caller runs/BFEB-CALLER16-REPRO/CALLER.json --native-projection runs/BFEB-CALLER-K-SPLIT-1.json --invoice runs/BFEB-CALLER16-REPRO/INVOICE.json --grid-output runs/BFEB-CALLER16-REPRO/CALLER-GRID.json --report runs/BFEB-CALLER16-REPRO/EXACT.json
python -I -B -m unittest discover -s review-swap -p test_caller_precision_reuse.py
ruff check review-swap/caller_precision_reuse.py review-swap/test_caller_precision_reuse.py
python -I -B review-alternatives/ordinary_tape_audit.py --word runs/COMMUTING-CANDIDATE-1/WORD.json.gz --invoice runs/BFEB-CALLER16-REPRO/INVOICE.json --caller runs/BFEB-CALLER16-REPRO/CALLER.json --caller-grid-receipt runs/BFEB-CALLER16-REPRO/CALLER-GRID.json --native-grid-receipt runs/COMMUTING-CANDIDATE-1/GRID.json --output runs/BFEB-CALLER16-REPRO/ORDINARY.json
python -I -B review-swap/caller_precision_reuse.py --word runs/COMMUTING-CANDIDATE-1/WORD.json.gz --caller runs/BFEB-CALLER16-REPRO/CALLER.json --caller-grid-receipt runs/BFEB-CALLER16-REPRO/CALLER-GRID.json --native-precision-receipt runs/COMMUTING-CANDIDATE-1/PRECISION.json --odd-scale 10125 --frac 21 --output runs/BFEB-CALLER16-REPRO/PRECISION.json
```

가격 비교는 새 invoice와 같은 contract를 가지며 paid/targets가 빈 INVOICE-ZERO.json을
새로 만들었다. source17 zero contract를 바꾸거나 comparator의 contract 일치 검사를
완화하지 않았다. 빈 histogram은 이16-stage 장부의 산술적0이며17-stage 증거가 아니다.
연구 디렉터리에서 다음 공식 CLI를 사용한다(출력은 표준출력 JSON이다).

```powershell
python -I -B ../../scripts/evaluate_recursive_power.py runs/BFEB-CALLER16-CANDIDATE-2/INVOICE-ZERO.json runs/BFEB-CALLER16-CANDIDATE-2/INVOICE.json --exponent 0.9962819897518 --bits 256
python -I -B ../../scripts/evaluate_recursive_power.py runs/BFEB-CALLER16-CANDIDATE-2/INVOICE-ZERO.json runs/BFEB-CALLER16-CANDIDATE-2/INVOICE.json --exponent 0.9962819897517 --bits 256
python -I -B ../../scripts/evaluate_recursive_power.py runs/BFEB-CALLER16-CANDIDATE-2/INVOICE-ZERO.json runs/BFEB-CALLER16-CANDIDATE-2/INVOICE.json --exponent 0.99628 --bits 256
python -I -B ../../scripts/evaluate_recursive_power.py runs/BFEB-CALLER16-CANDIDATE-2/INVOICE-ZERO.json runs/BFEB-CALLER16-CANDIDATE-2/INVOICE.json --exponent 0.99626 --bits 256
```

생성기 QA7fixture, caller audit 독립8fixture와 Ruff가 통과했다.
native재사용 어댑터4fixture/Ruff도 통과했다. 모든 실제 감독 실행의 cleanup0→0와
owned PID+creation_filetime/감독 PID/lock 부재를 확인한 뒤 다음 작업자에게 인계했다.
최초 lint의 unused variable, 복사한 source의 추가 말미 개행, 선택하지 않은 sparse 정의의
구현 오류를 고쳤고 실패 receipt도 보존했다. source bytes 검사는 말미 개행까지 포함한
Git blob 자체를 확인한다. 과거 native 전체 baseline 재실행이나 원문·기존 branch/commit/
원격 변경은 하지 않았다.
