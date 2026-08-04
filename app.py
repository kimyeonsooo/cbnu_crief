import re
import time
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent
LOGO_PATH = BASE_DIR / "nova_logo.png"

st.set_page_config(
    page_title="CBNU CRIEF",
    page_icon=Image.open(LOGO_PATH),
    layout="wide"
)


def load_scholarly():
    try:
        from scholarly import scholarly
        return scholarly
    except ImportError:
        st.error("`scholarly` 패키지가 설치되어 있지 않습니다. `python -m pip install -r requirements.txt`를 실행하세요.")
        st.stop()


def make_query(author: str, keyword: str, exact: bool) -> str:
    parts = []
    if author.strip():
        parts.append(f'author:"{author.strip()}"')
    if keyword.strip():
        parts.append(f'"{keyword.strip()}"' if exact else keyword.strip())
    return " ".join(parts)


def clean_text(value):
    if value is None:
        return ""
    if isinstance(value, (list, tuple)):
        return "; ".join(str(x) for x in value)
    return str(value)


def get_year(paper: dict):
    value = clean_text((paper.get("bib") or {}).get("pub_year"))
    match = re.search(r"\b(?:19|20)\d{2}\b", value)
    return int(match.group()) if match else None


def is_in_year_range(paper: dict, year_from, year_to) -> bool:
    if not year_from and not year_to:
        return True
    year = get_year(paper)
    if year is None:
        return False
    if year_from and year < int(year_from):
        return False
    if year_to and year > int(year_to):
        return False
    return True


def paper_row(paper: dict, query: str, detail_loaded: bool = False) -> dict:
    bib = paper.get("bib", {}) or {}
    return {
        "검색식": query,
        "제목": clean_text(bib.get("title")),
        "저자": clean_text(bib.get("author")),
        "발행연도": clean_text(bib.get("pub_year")),
        "출처(학술지/학회 등)": clean_text(bib.get("venue")),
        "출판사": clean_text(bib.get("publisher")),
        "권": clean_text(bib.get("volume")),
        "호": clean_text(bib.get("number")),
        "페이지": clean_text(bib.get("pages")),
        "초록": clean_text(bib.get("abstract")),
        "인용 수": paper.get("num_citations"),
        "출판/원문 URL": clean_text(paper.get("pub_url")),
        "Google Scholar 서지 URL": clean_text(paper.get("url_scholarbib")),
        "Google Scholar 논문 ID": clean_text(paper.get("author_pub_id")),
        "상세 조회 여부": "Y" if detail_loaded else "N",
        "수집 일시(UTC)": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
    }


def normalize_title(value: str) -> str:
    return re.sub(r"[^a-z0-9가-힣]", "", str(value).lower())


def remove_duplicates(rows: list[dict]) -> list[dict]:
    seen, result = set(), []
    for row in rows:
        key = (normalize_title(row["제목"]), str(row["발행연도"]), str(row["저자"]).lower())
        if key[0] and key not in seen:
            seen.add(key)
            result.append(row)
    return result


def search_papers(query: str, limit: int, pause: float, load_details: bool, year_from, year_to):
    scholarly = load_scholarly()
    iterator = scholarly.search_pubs(
        query,
        year_low=int(year_from) if year_from else None,
        year_high=int(year_to) if year_to else None,
    )
    rows, errors, skipped = [], [], 0
    progress = st.progress(0, text="Google Scholar 검색을 시작합니다.")
    processed = 0

    while len(rows) < limit:
        try:
            paper = next(iterator)
        except StopIteration:
            break
        except Exception as exc:
            errors.append(f"검색 결과 조회 중 오류: {exc}")
            break

        processed += 1
        if not is_in_year_range(paper, year_from, year_to):
            skipped += 1
            if processed >= limit * 5:
                break
            continue

        detailed = False
        if load_details:
            try:
                paper = scholarly.fill(paper)
                detailed = True
            except Exception as exc:
                title = (paper.get("bib") or {}).get("title", "제목 미상")
                errors.append(f"‘{title}’ 상세 조회 실패: {exc}")

        rows.append(paper_row(paper, query, detailed))
        progress.progress(len(rows) / limit, text=f"{len(rows)}/{limit}건 수집 완료")
        if len(rows) < limit and pause > 0:
            time.sleep(pause)

    progress.empty()
    return remove_duplicates(rows), errors, skipped


def to_excel(df: pd.DataFrame) -> bytes:
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="검색결과", index=False)
        ws = writer.sheets["검색결과"]
        ws.freeze_panes = "A2"
        widths = {"A": 42, "B": 36, "C": 12, "D": 30, "E": 20, "F": 20, "G": 10, "H": 10, "I": 14, "J": 60, "K": 12, "L": 45, "M": 48, "N": 24, "O": 12, "P": 22}
        for col, width in widths.items():
            ws.column_dimensions[col].width = width
        for cell in ws[1]:
            cell.font = cell.font.copy(bold=True)
    return buffer.getvalue()


st.title("충북대학교 공동실험실습관 논문 실적 검색")
st.caption("충북대학교 공동실험실습관 장비 이용 연구자의 논문 실적을 검색하고 수집하는 기관 전용 서비스입니다.")

with st.sidebar:
    st.header("검색 조건")
    author = st.text_input("저자명", placeholder="예: Gil Dong Hong 또는 홍길동")
    keyword = st.text_input("키워드", placeholder="예: field emission scanning electron microscope")
    exact = st.checkbox("키워드 정확 일치 검색", value=True)
    c1, c2 = st.columns(2)
    with c1:
        year_from = st.number_input("시작 연도", min_value=1900, max_value=2100, value=None, step=1, placeholder="전체")
    with c2:
        year_to = st.number_input("종료 연도", min_value=1900, max_value=2100, value=None, step=1, placeholder="전체")
    limit = st.slider("최대 수집 건수", min_value=1, max_value=50, value=10)
    pause = st.slider("요청 간 대기(초)", min_value=0.1, max_value=2.0, value=1.0, step=0.1)
    load_details = st.checkbox("논문별 상세 메타데이터 추가 조회", value=False, help="초록·권호·페이지 등의 정보를 보완하지만 요청 수가 늘어납니다.")
    search_clicked = st.button("검색", type="primary", use_container_width=True)

query = make_query(author, keyword, exact)
period = "전체 기간" if not year_from and not year_to else f"{int(year_from) if year_from else '최초'} ~ {int(year_to) if year_to else '현재'}"
st.markdown(f"**생성된 검색식:** `{query or '검색어를 입력하세요.'}`  |  **발행연도 필터:** `{period}`")

if search_clicked:
    if not author.strip() and not keyword.strip():
        st.warning("저자명 또는 키워드를 하나 이상 입력하세요.")
    elif year_from and year_to and year_from > year_to:
        st.warning("시작 연도는 종료 연도보다 클 수 없습니다.")
    else:
        try:
            rows, errors, skipped = search_papers(query, limit, pause, load_details, year_from, year_to)
            st.session_state["rows"] = rows
            st.session_state["errors"] = errors
            st.session_state["skipped"] = skipped
            st.session_state["search_number"] = st.session_state.get("search_number", 0) + 1
        except Exception as exc:
            st.error("Google Scholar 검색 요청이 처리되지 않았습니다. CAPTCHA·접속 제한 또는 네트워크 문제일 수 있습니다.")
            st.exception(exc)

if "rows" in st.session_state:
    rows = st.session_state["rows"]
    errors = st.session_state.get("errors", [])
    skipped = st.session_state.get("skipped", 0)
    if rows:
        df = pd.DataFrame(rows)
        st.success(f"중복 제거 후 {len(df)}건을 수집했습니다.")
        if skipped:
            st.info(f"발행연도 정보가 없거나 지정 기간 밖인 {skipped}건은 결과에서 제외했습니다.")

        st.subheader("검색 결과 선택")
        st.caption("내보낼 문서의 ‘선택’ 체크박스를 선택한 뒤 XLSX 다운로드 버튼을 누르세요.")
        show_cols = ["선택", "제목", "저자", "발행연도", "출처(학술지/학회 등)", "인용 수", "출판/원문 URL", "Google Scholar 서지 URL"]
        select_df = df.copy()
        select_df.insert(0, "선택", False)
        result_key = f"paper_selector_{st.session_state.get('search_number', 0)}"
        edited_df = st.data_editor(
            select_df[show_cols],
            key=result_key,
            use_container_width=True,
            hide_index=True,
            disabled=[col for col in show_cols if col != "선택"],
            column_config={
                "선택": st.column_config.CheckboxColumn("선택", help="엑셀로 내보낼 논문을 선택합니다.", default=False),
                "출판/원문 URL": st.column_config.LinkColumn("출판/원문 URL"),
                "Google Scholar 서지 URL": st.column_config.LinkColumn("Google Scholar 서지 URL"),
            },
        )

        selected_positions = edited_df.index[edited_df["선택"].fillna(False)].tolist()
        selected_df = df.loc[selected_positions].copy()
        selected_count = len(selected_df)
        st.markdown(f"**선택한 문서: {selected_count}건 / 전체 {len(df)}건**")

        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if selected_count:
            xlsx_name = f"google_scholar_selected_{selected_count}건_{stamp}.xlsx"
            st.download_button(
                f"선택한 {selected_count}건 XLSX 다운로드",
                to_excel(selected_df),
                xlsx_name,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                type="primary",
            )
        else:
            st.info("엑셀로 내보낼 문서를 하나 이상 선택하세요.")

        with st.expander("전체 결과를 CSV로 다운로드"):
            st.download_button(
                "전체 결과 CSV 다운로드",
                df.to_csv(index=False).encode("utf-8-sig"),
                f"google_scholar_all_{stamp}.csv",
                "text/csv",
                use_container_width=True,
            )
        with st.expander("선택 문서의 전체 메타데이터 미리보기"):
            if selected_count:
                st.dataframe(selected_df, use_container_width=True, hide_index=True)
            else:
                st.caption("문서를 선택하면 제목·초록·URL 등 전체 메타데이터를 확인할 수 있습니다.")
    else:
        st.info("조건에 맞는 결과를 찾지 못했습니다.")
    if errors:
        with st.expander(f"처리 중 경고 {len(errors)}건"):
            for error in errors:
                st.write(f"- {error}")

st.divider()
st.caption("발행연도 필터는 Google Scholar 요청의 year_low/year_high 옵션과 수집 후 pub_year 재검증을 함께 적용합니다. 따라서 기간 필터를 설정하면 발행연도 정보가 없는 결과도 제외됩니다. Google Scholar의 발행연도는 온라인 공개일과 정식 출판일 차이 등으로 출판사 정보와 다를 수 있습니다.")
