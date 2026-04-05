"""
services/market_data.py
市場データ取得サービス

【データソースの切り替え方】
- DATA_MODE="mock" の場合: sample_data/mock_market.json からデータを読み込む
- DATA_MODE="live" の場合: yfinance や各種APIからリアルデータを取得する

【実際のAPIに差し替えるには】
1. yfinanceを使う場合（無料）:
   - pip install yfinance
   - fetch_live_data() 関数のコメントを参照

2. Alpha Vantage を使う場合:
   - config.py の ALPHA_VANTAGE_KEY に APIキーを設定
   - 各関数の TODO コメントを参照

3. その他のデータソース:
   - Bloomberg API (有料)
   - Refinitiv / LSEG (有料)
   - J-Quants API（日本株専門、一部無料）
     https://jpx-jquants.com/
"""

import json
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.types import MarketData
from config import DATA_MODE, MOCK_DATA_PATH


def fetch_market_data() -> MarketData:
    """
    市場データを取得するメイン関数
    DATA_MODE に応じてモック/実データを切り替えます
    """
    if DATA_MODE == "live":
        return fetch_live_data()
    else:
        return fetch_mock_data()


def fetch_mock_data() -> MarketData:
    """
    サンプルデータファイルから市場データを読み込む
    APIキーなしで動作確認できます
    """
    with open(MOCK_DATA_PATH, "r", encoding="utf-8") as f:
        raw = json.load(f)

    m = raw["market"]
    return MarketData(
        nikkei=m["nikkei"],
        nikkei_change_pct=m["nikkei_change_pct"],
        topix=m["topix"],
        topix_change_pct=m["topix_change_pct"],
        tse_growth=m["tse_growth"],
        tse_growth_change_pct=m["tse_growth_change_pct"],
        usdjpy=m["usdjpy"],
        usdjpy_change=m["usdjpy_change"],
        sp500=m["sp500"],
        sp500_change_pct=m["sp500_change_pct"],
        nasdaq=m["nasdaq"],
        nasdaq_change_pct=m["nasdaq_change_pct"],
        sox=m["sox"],
        sox_change_pct=m["sox_change_pct"],
        us_2y_yield=m["us_2y_yield"],
        us_10y_yield=m["us_10y_yield"],
        jp_10y_yield=m["jp_10y_yield"],
        wti_crude=m["wti_crude"],
        wti_change_pct=m["wti_change_pct"],
        gold=m["gold"],
        gold_change_pct=m["gold_change_pct"],
        vix=m["vix"],
        turnover_trillion_yen=m.get("turnover_trillion_yen"),
        advance_decline_ratio=m.get("advance_decline_ratio"),
    )


def fetch_live_data() -> MarketData:
    """
    実際のAPIからリアルタイム市場データを取得する
    【使い方】 DATA_MODE=live python main.py

    TODO: yfinanceを使う場合は以下のコメントを解除してください
    pip install yfinance が必要です
    """

    # ===== yfinance 版（無料・推奨） =====
    # TODO: 以下のコメントを解除して yfinance を有効化してください

    # try:
    #     import yfinance as yf
    #     from datetime import timedelta
    #
    #     def _get_change_pct(ticker_sym: str) -> tuple[float, float]:
    #         """終値と前日比(%)を取得"""
    #         t = yf.Ticker(ticker_sym)
    #         hist = t.history(period="2d")
    #         if len(hist) < 2:
    #             return 0.0, 0.0
    #         close_today = hist["Close"].iloc[-1]
    #         close_prev = hist["Close"].iloc[-2]
    #         change_pct = (close_today - close_prev) / close_prev * 100
    #         return float(close_today), float(change_pct)
    #
    #     def _get_yield(ticker_sym: str) -> float:
    #         """金利データを取得（^TNX など）"""
    #         t = yf.Ticker(ticker_sym)
    #         hist = t.history(period="1d")
    #         if hist.empty:
    #             return 0.0
    #         return float(hist["Close"].iloc[-1])
    #
    #     nikkei, nikkei_chg = _get_change_pct("^N225")
    #     topix, topix_chg = _get_change_pct("^TPX")
    #     usdjpy, _ = _get_change_pct("JPY=X")
    #     usdjpy_prev_close = usdjpy / (1 + _ / 100) if _ != 0 else usdjpy
    #     usdjpy_change = usdjpy - usdjpy_prev_close
    #     sp500, sp500_chg = _get_change_pct("^GSPC")
    #     nasdaq, nasdaq_chg = _get_change_pct("^IXIC")
    #     sox, sox_chg = _get_change_pct("^SOX")
    #     wti, wti_chg = _get_change_pct("CL=F")
    #     gold, gold_chg = _get_change_pct("GC=F")
    #     vix, _ = _get_change_pct("^VIX")
    #     us_10y = _get_yield("^TNX")
    #     us_2y = _get_yield("^IRX")
    #     jp_10y = _get_yield("^JGB10Y")  # 利用可能な場合
    #
    #     return MarketData(
    #         nikkei=nikkei, nikkei_change_pct=nikkei_chg,
    #         topix=topix, topix_change_pct=topix_chg,
    #         tse_growth=0.0, tse_growth_change_pct=0.0,  # yfinanceで取得困難
    #         usdjpy=usdjpy, usdjpy_change=usdjpy_change,
    #         sp500=sp500, sp500_change_pct=sp500_chg,
    #         nasdaq=nasdaq, nasdaq_change_pct=nasdaq_chg,
    #         sox=sox, sox_change_pct=sox_chg,
    #         us_2y_yield=us_2y, us_10y_yield=us_10y, jp_10y_yield=jp_10y,
    #         wti_crude=wti, wti_change_pct=wti_chg,
    #         gold=gold, gold_change_pct=gold_chg,
    #         vix=vix,
    #     )
    # except Exception as e:
    #     print(f"[警告] ライブデータ取得に失敗しました: {e}")
    #     print("[情報] サンプルデータにフォールバックします")
    #     return fetch_mock_data()

    # ===== 現在はフォールバックとしてモックデータを使用 =====
    print("[警告] live モードが選択されましたが、yfinanceが未設定です。モックデータを使用します。")
    print("[情報] services/market_data.py の TODO コメントを確認してください。")
    return fetch_mock_data()
