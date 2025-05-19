import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="定期継続分析ダッシュボード", layout="wide")
st.title("📦 定期継続分析ダッシュボード")

uploaded_file = st.file_uploader("all_orders.csv をアップロードしてください", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file, encoding="shift_jis")
    df.columns = df.columns.str.strip()
    df["受注日"] = pd.to_datetime(df["受注日"])
    df["注文月"] = df["受注日"].dt.to_period("M").astype(str)

    # 初回月と初回URLの特定
    first_orders = df[df["定期回数"] == 1][["顧客番号", "注文月", "購入URL"]].drop_duplicates()
    first_orders = first_orders.rename(columns={"注文月": "初回月", "購入URL": "初回購入URL"})
    df = df.merge(first_orders, on="顧客番号", how="left")

    # 商品・URL フィルタ
    products = df["購入商品（商品名）"].unique()
    urls = df["初回購入URL"].dropna().unique()
    selected_product = st.selectbox("購入商品でフィルタ", ["すべて"] + list(products))
    selected_url = st.selectbox("購入URLでフィルタ", ["すべて"] + list(urls))

    if selected_product != "すべて":
        df = df[df["購入商品（商品名）"] == selected_product]
    if selected_url != "すべて":
        df = df[df["初回購入URL"] == selected_url]

    # 初回購入月ごとの集計
    base_grouped = df.groupby(["初回月", "定期回数"]).agg(
        ユーザー数=("顧客番号", "nunique"),
        売上=("合計", "sum")
    ).reset_index()

    base_grouped = base_grouped.sort_values(by=["初回月", "定期回数"])
    base_grouped["前回ユーザー数"] = base_grouped.groupby("初回月")["ユーザー数"].shift(1)
    base_grouped["継続率"] = base_grouped["ユーザー数"] / base_grouped["前回ユーザー数"]
    base_grouped.loc[base_grouped["定期回数"] == 1, "継続率"] = None
    base_grouped["継続率"] = base_grouped["継続率"].apply(lambda x: f"{x:.2%}" if pd.notnull(x) else "-")
    base_grouped["売上"] = base_grouped["売上"].apply(lambda x: f"¥{int(x):,}")
    base_grouped["定期回数"] = base_grouped["定期回数"].astype(str) + "回目"
    base_grouped = base_grouped.rename(columns={"初回月": "初回購入月"})

    # カレンダー形式の範囲指定
    st.markdown("#### 📅 表示する初回購入月の範囲を選択")

    min_month = df["注文月"].min()
    max_month = df["注文月"].max()

    min_date = datetime.strptime(min_month, "%Y-%m")
    max_date = datetime.strptime(max_month, "%Y-%m")

    date_range = st.date_input(
        "初回購入月の期間を選択してください",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        type="range"
    )

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
        start_month = start_date.strftime("%Y-%m")
        end_month = end_date.strftime("%Y-%m")

        # フィルタ適用
        filtered_grouped = base_grouped[
            (base_grouped["初回購入月"] >= start_month) &
            (base_grouped["初回購入月"] <= end_month)
        ]

        st.markdown("### 📈 分析結果")
        st.dataframe(
            filtered_grouped[["初回購入月", "定期回数", "ユーザー数", "売上", "継続率"]].reset_index(drop=True),
            use_container_width=True
        )
    else:
        st.warning("有効な日付範囲を選択してください。")
