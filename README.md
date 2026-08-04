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

## 검색식 예시
- 저자만: `author:"Gil Dong Hong"`
- 본문 색인 키워드: `"field emission scanning electron microscope"`
- 저자 + 키워드: `author:"Gil Dong Hong" "FE-SEM"`
- 기간 포함: `author:"Gil Dong Hong" "FE-SEM" after:2022 before:2026`

앱에서 입력한 조건으로 위와 같은 검색식을 자동 생성합니다.

## 유의사항
- `scholarly`는 Google Scholar의 공식 API가 아닌 비공식 라이브러리입니다.
- 대량·반복 요청은 CAPTCHA, 일시적 차단 또는 결과 제한을 유발할 수 있습니다. 기본값처럼 요청 간 대기시간을 유지하고, 처음에는 10~20건 이하로 수집하세요.
- Google Scholar의 검색 결과는 제목·초록·색인된 원문 등 Scholar의 자체 색인 범위에 기반합니다. 검색 결과만으로 키워드가 제목, 초록, 본문 중 어느 위치에 있는지 확정할 수는 없습니다.
- 결과별 메타데이터 제공 수준은 출판사 및 Scholar 색인 상태에 따라 달라집니다. DOI가 반드시 제공되지는 않습니다.
