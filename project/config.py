"""
config.py
設定値・定数の定義ファイル
閾値やラベルをここで一元管理します
"""

import os

# ==============================
# データモード設定
# ==============================
# "mock" : サンプルデータを使用（APIキー不要）
# "live" : 実際のAPIからデータ取得
DATA_MODE = os.getenv("DATA_MODE", "mock")

# ==============================
# APIキー設定
# ==============================
# TODO: 実際のAPIキーを環境変数に設定してください
# 例: export ALPHA_VANTAGE_KEY="your_key_here"

ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY", "")   # TODO: Alpha Vantage APIキー
YAHOO_FINANCE_ENABLED = True                               # yfinanceは無料で使用可能

# ==============================
# サンプルデータファイルのパス
# ==============================
MOCK_DATA_PATH = os.path.join(os.path.dirname(__file__), "sample_data", "mock_market.json")

# ==============================
# 市場レジーム判定の閾値
# ==============================

# 円安・円高の判定閾値（変化幅、円）
USDJPY_WEAK_YEN_THRESHOLD = 0.5      # この値以上の上昇→円安トレンド
USDJPY_STRONG_YEN_THRESHOLD = -0.5   # この値以下の下落→円高トレンド

# 米10年金利の閾値 (%)
US10Y_HIGH = 4.5                     # この値以上→金利高水準
US10Y_RISING_CHANGE = 0.05           # 1日の変化がこの値以上→金利上昇トレンド

# VIXの閾値
VIX_HIGH = 20.0                      # この値以上→高ボラティリティ（リスクオフ警戒）
VIX_VERY_HIGH = 30.0                 # この値以上→強いリスクオフ

# SOXの閾値（変化率 %）
SOX_STRONG_UP = 1.5                  # この値以上の上昇→半導体主導の強気
SOX_STRONG_DOWN = -1.5               # この値以下の下落→半導体セクター重し

# 原油の閾値（変化率 %）
OIL_RISING = 1.0                     # この値以上→原油上昇トレンド
OIL_FALLING = -1.0                   # この値以下→原油下落トレンド

# 米国株の閾値（変化率 %）
US_STOCK_STRONG_UP = 0.5
US_STOCK_STRONG_DOWN = -0.5

# ==============================
# セクター定義
# ==============================
# 代表的な東証セクター
SECTORS = {
    "export": "自動車・機械・輸出関連",
    "semiconductor": "半導体・電子部品",
    "bank": "銀行・金融",
    "resource": "商社・資源・エネルギー",
    "real_estate": "不動産・REIT",
    "growth": "グロース・テック（高PER）",
    "domestic_demand": "内需・小売・食品",
    "pharma": "医薬品・ヘルスケア",
    "airline_transport": "空運・陸運",
    "utility": "電力・ガス",
    "steel_chemical": "鉄鋼・素材・化学",
    "insurance": "保険",
}

# ==============================
# FastAPI設定
# ==============================
API_HOST = "0.0.0.0"
API_PORT = int(os.getenv("PORT", 8888))
