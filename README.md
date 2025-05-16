# 定期継続分析ダッシュボード

このアプリは Streamlit + Cloudflare Access を使って、社内メンバー向けに定期継続分析を提供するものです。

## ✅ 公開手順

1. このリポジトリを GitHub にアップロード
2. [Streamlit Cloud](https://streamlit.io/cloud) で新しいアプリを作成し、`streamlit_repeat_dashboard_final_v2.py` を指定
3. [Cloudflare](https://dash.cloudflare.com) にて Access を設定し、この Streamlit URL を保護（Googleログインなど）

## 📦 構成ファイル
- `streamlit_repeat_dashboard_final_v2.py`: アプリ本体
- `requirements.txt`: 必要パッケージ
