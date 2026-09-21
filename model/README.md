# TAPIE FACE

사진 한 장을 YOLOv8-Face로 검출하고 5점 랜드마크로 정렬한 뒤, BiSeNet으로 배경·머리카락·목·의류를
제외한 얼굴 구성 요소만 남겨 ArcFace 512차원 임베딩을 만드는 로컬 얼굴 유사도 워크벤치입니다.

## 처리 흐름

1. `YOLOv8-Face`가 얼굴 박스와 눈·코·입 5점 랜드마크를 찾습니다.
2. 얼굴을 ArcFace 표준 좌표인 112×112로 정렬합니다.
3. `BiSeNet`의 19개 클래스 중 피부, 눈썹, 눈, 코, 입술, 귀, 안경만 남기고 배경·헤어를 중립색으로 바꿉니다.
4. `ArcFace`가 L2 정규화된 512차원 임베딩을 생성합니다.
5. 인물별 여러 기준 사진의 임베딩을 단위 평균 벡터로 저장하고 코사인 유사도로 순위를 계산합니다.

마스킹은 배경과 헤어스타일의 영향을 크게 줄이지만, 어떤 생체 모델도 영향이 수학적으로 0이라고 보장할
수는 없습니다. 조명, 표정, 연령, 촬영 각도도 결과에 영향을 줍니다. 화면의 0–100 값은 원시 코사인을
읽기 쉽게 바꾼 표시용 점수이며 신원 확인이나 확률이 아닙니다.

## 기준 사진 준비

당사자 동의를 받은 사진만 `references/` 아래 인물별 폴더에 넣습니다.

```text
references/
  person-a/
    front.jpg
    slight-left.png
  person-b/
    portrait.webp
```

JPG, PNG, WebP를 지원합니다. 폴더명이 결과 라벨이 됩니다. 실행 후 **기준 벡터 다시 만들기**를 누르면
`.data/face-index.json`에 임베딩만 저장됩니다. 원본 기준 사진은 그대로 `references/`에 남습니다.

## 실행

Python 3.13과 [uv](https://docs.astral.sh/uv/)가 필요합니다.

```bash
uv sync
uv run model
```

브라우저에서 <http://127.0.0.1:8000>을 엽니다. 첫 인덱싱 때 YOLOv8-Face, BiSeNet, ArcFace ONNX
가중치 약 76MB를 내려받습니다. CPU 실행이 기본값입니다.

## API

- `GET /api/status`: 모델·기준 인덱스 상태와 인물/사진 수
- `POST /api/reindex`: 기준 사진을 다시 처리해 인물별 벡터 생성
- `POST /api/analyze`: `image` multipart 필드의 얼굴 사진 분석
- `GET /showcase`: 빈 상태, 로딩, 성공, 경고, 오류, 비활성, 포커스, 긴 콘텐츠 UI 상태

업로드는 JPG, PNG, WebP 및 10MB 이하만 허용합니다. 질의 이미지는 요청 메모리에서만 처리하고 서버에
저장하지 않습니다.

## 검증

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run basedpyright
uv build
```

UniFace 자체는 MIT 라이선스이지만 배포 전에는 사용하는 각 사전학습 가중치의 라이선스도 별도로 확인해야
합니다. 얼굴 임베딩은 생체정보이므로 접근 제어, 암호화, 보존 기간, 삭제 절차를 운영 환경에 맞게 적용하세요.
