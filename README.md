# Google Scholar 논문 검색 프로그램

## 기능
- 저자명, 키워드, 발행연도 조건으로 Google Scholar 검색
- `scholarly`를 통해 검색 결과의 메타데이터 수집
- 제목, 저자, 연도, 출처, 초록, 인용 수, 출판/원문 URL, Google Scholar 서지 URL 표시
- 제목·저자·연도 기준의 간단한 중복 제거
- CSV 및 XLSX 다운로드
- 필요 시 개별 논문의 상세 메타데이터 추가 조회

## 설치 및 실행

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

macOS/Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

실행 후 터미널에 표시되는 로컬 주소(기본값 `http://localhost:8501`)로 접속합니다.

## 키워드 입력 및 AND / OR / 정확 구문 검색
- 키워드는 **쉼표(,)로 구분**하여 여러 개 입력할 수 있습니다. 예: `XRD, SEM, TEM`
- **결합 조건(AND/OR)**을 라디오 버튼으로 선택합니다.
  - `AND`: 입력한 키워드를 **모두 포함**하는 논문만 검색 (예: `XRD SEM` → XRD와 SEM을 둘 다 포함)
  - `OR`: 입력한 키워드 중 **하나라도 포함**하는 논문 검색 (예: `(XRD OR SEM)`)
- **정확 구문 검색** 체크박스를 켜면 각 키워드를 따옴표로 감싸 정확한 구문(phrase)으로 검색합니다. 예: `SEM` → `"SEM"`
  - 여러 단어로 이루어진 장비명(예: `field emission scanning electron microscope`)은 정확 구문 검색을 켜야 그 단어 순서 그대로 붙어 있는 문서만 찾습니다. 꺼두면 각 단어가 흩어져 있어도 매칭될 수 있습니다.
- Google Scholar는 공백으로 나열하면 기본적으로 AND, `OR`을 명시하면 OR, `-`를 붙이면 제외(NOT) 조건으로 동작합니다.

## 검색식 예시
- 저자만: `author:"Gil Dong Hong"`
- 본문 색인 키워드: `"field emission scanning electron microscope"`
- 저자 + 키워드: `author:"Gil Dong Hong" "FE-SEM"`
- 키워드 AND (정확 구문 ON): `XRD, SEM` → `"XRD" "SEM"`
- 키워드 OR (정확 구문 OFF): `XRD, SEM` → `(XRD OR SEM)`
- 기간 포함: `author:"Gil Dong Hong" "FE-SEM" after:2022 before:2026`

앱에서 입력한 조건으로 위와 같은 검색식을 자동 생성합니다.

## 유의사항
- `scholarly`는 Google Scholar의 공식 API가 아닌 비공식 라이브러리입니다.
- 대량·반복 요청은 CAPTCHA, 일시적 차단 또는 결과 제한을 유발할 수 있습니다. 기본값처럼 요청 간 대기시간을 유지하고, 처음에는 10~20건 이하로 수집하세요.
- Google Scholar의 검색 결과는 제목·초록·색인된 원문 등 Scholar의 자체 색인 범위에 기반합니다. 검색 결과만으로 키워드가 제목, 초록, 본문 중 어느 위치에 있는지 확정할 수는 없습니다.
- 결과별 메타데이터 제공 수준은 출판사 및 Scholar 색인 상태에 따라 달라집니다. DOI가 반드시 제공되지는 않습니다.
