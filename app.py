import streamlit as st
import pandas as pd
import io
from scraper import run_scraping

st.set_page_config(page_title="SES企業リスト", page_icon="🏢", layout="wide")
st.title("🏢 SES営業リスト 企業一覧")
st.caption("CloudMeetsの第1弾〜第38弾から企業名・URLを収集します")

# セッションに結果を保持
if "companies" not in st.session_state:
    st.session_state.companies = []

# ---- スクレイピング実行ボタン ----
if st.button("🔍 スクレイピング実行", type="primary"):
    progress_bar = st.progress(0)
    status_text = st.empty()

    def on_progress(current, total, url):
        progress_bar.progress(current / total)
        status_text.text(f"取得中... ({current}/{total}) {url}")

    with st.spinner("スクレイピング中..."):
        st.session_state.companies = run_scraping(progress_callback=on_progress)

    progress_bar.empty()
    status_text.empty()
    st.success(f"✅ {len(st.session_state.companies)}社を取得しました！")

# ---- 結果表示 ----
if st.session_state.companies:
    df = pd.DataFrame(st.session_state.companies)

    # 検索フィルター
    keyword = st.text_input("🔎 企業名で絞り込み")
    if keyword:
        df = df[df["企業名"].str.contains(keyword, na=False)]

    st.dataframe(
        df,
        column_config={"URL": st.column_config.LinkColumn("URL")},
        use_container_width=True,
        height=500,
    )
    st.caption(f"{len(df)}社表示中")

    # ---- Excel出力 ----
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="SES企業リスト")
    st.download_button(
        label="📥 Excelでダウンロード",
        data=output.getvalue(),
        file_name="ses_companies.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
