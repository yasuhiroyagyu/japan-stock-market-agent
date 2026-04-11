"""
services/market_data.py
市場データ取得サービス

【データモードの切り替え】
- DATA_MODE="mock" : sample_data/mock_market.json からデータを読み込む（デフォルト）
- DATA_MODE="live" : yfinance を使ってリアルデータを取得する

【実行例】
  python3 main.py               # モックデータ
  DATA_MODE=live python3 main.py  # 実データ

【データソース (live モード)】
  yfinance 経由で Yahoo Finance から取得（無料・APIキー不要）
  取得対象: 日経平均, TOPIX, S&P500, NASDAQ, VIX, USD/JPY, Gold, WTI原油

【未対応 → mock フォールバック】
  - SOX (^SOX)       : TODO コメント参照
  - 米2年金利 (^IRX) : TODO コメント参照
  - 米10年金利 (^TNX): TODO コメント参照
  - 日本10年金利      : TODO コメント参照
  - 東証グロース指数  : yfinance では安定取得が困難
"""

import json
import sys
import os
from datetime import datetime
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.types import MarketData
from config import DATA_MODE, MOCK_DATA_PATH


# ============================================================
# パブリック API
# ============================================================

def fetch_market_data() -> MarketData:
    """
    市場データを取得するメイン関数。
    DATA_MODE に応じてモック / 実データを切り替えます。
    """
    if DATA_MODE == "live":
        return fetch_live_data()
    else:
        return fetch_mock_data()


# ============================================================
# モックデータ取得
# ============================================================

def fetch_mock_data() -> MarketData:
    """
    sample_data/mock_market.json からサンプルデータを読み込む。
    APIキー不要で即動作確認できます。
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


# ============================================================
# 実データ取得（yfinance）
# ============================================================

def fetch_live_data() -> MarketData:
    """
    yfinance を使って Yahoo Finance からリアルタイムデータを取得する。
    各銘柄を1件ずつ安全に取得し、失敗した場合は None を返す。

    取得成功: yfinance の実データを使用
    取得失敗: モックデータの対応値にフォールバック
    """
    try:
        import yfinance as yf
    except ImportError:
        print("[エラー] yfinance がインストールされていません。")
        print("  pip install yfinance pandas を実行してください。")
        print("[情報] モックデータにフォールバックします。")
        return fetch_mock_data()

    print("[live] yfinance でリアルデータを取得中...")

    # モックデータを fallback 用に先に読み込んでおく
    mock = fetch_mock_data()

    # ---- 各銘柄を1件ずつ安全に取得 ----

    nikkei_r      = _fetch_ticker("^N225",  label="日経平均")
    # TOPIX 直接シンボル (^TPX / ^TOPX) は yfinance で取得不可のため、
    # TOPIX 連動型 ETF (1306.T) で騰落率を近似する。
    topix_r       = _fetch_ticker("1306.T", label="TOPIX(1306.T近似)")
    sp500_r       = _fetch_ticker("^GSPC",  label="S&P500")
    nasdaq_r      = _fetch_ticker("^IXIC",  label="NASDAQ")
    vix_r         = _fetch_ticker("^VIX",   label="VIX")
    usdjpy_r      = _fetch_ticker("JPY=X",  label="USD/JPY")
    gold_r        = _fetch_ticker("GC=F",   label="Gold")
    wti_r         = _fetch_ticker("CL=F",   label="WTI原油")

    # ---- TODO: 以下は yfinance での安定取得が困難なため mock フォールバック ----

    # TODO: SOX (フィラデルフィア半導体指数)
    #   シンボル ^SOX は yfinance で取得できない場合がある。
    #   代替: SOXX (iShares 半導体 ETF) で近似する方法もある。
    #   sox_r = _fetch_ticker("^SOX", label="SOX")
    sox_price      = mock.sox
    sox_change_pct = mock.sox_change_pct

    # TODO: 米2年金利 (^IRX は13週Tビル利回り ≒ 2年金利の近似)
    #   より正確な取得には FRED API や Bloomberg が必要。
    #   us2y_r = _fetch_ticker("^IRX", label="米2年金利")
    us_2y_yield = mock.us_2y_yield

    # TODO: 米10年金利 (^TNX)
    #   yfinance で ^TNX を取得できる場合もあるが不安定。
    #   us10y_r = _fetch_ticker("^TNX", label="米10年金利")
    us_10y_yield = mock.us_10y_yield

    # TODO: 日本10年金利
    #   yfinance に安定したシンボルがない。
    #   J-Quants API または日本銀行 API の利用を推奨。
    #   https://jpx-jquants.com/
    jp_10y_yield = mock.jp_10y_yield

    # TODO: 東証グロース指数
    #   yfinance での取得が不安定なため mock を使用。
    tse_growth            = mock.tse_growth
    tse_growth_change_pct = mock.tse_growth_change_pct

    # ---- 実データ / fallback を組み合わせて MarketData を構築 ----

    # USD/JPY は「変化率」ではなく「変化幅（円）」で持つ
    usdjpy_price  = _price(usdjpy_r, mock.usdjpy)
    usdjpy_prev   = _prev_close(usdjpy_r, mock.usdjpy)
    usdjpy_change = round(usdjpy_price - usdjpy_prev, 4)

    return MarketData(
        # 日本株
        nikkei=_price(nikkei_r, mock.nikkei),
        nikkei_change_pct=_change_pct(nikkei_r, mock.nikkei_change_pct),
        # TOPIX: 1306.T ETF の騰落率を使い、指数値はモック値をそのまま表示
        # （ETF の price 自体は TOPIX の指数値と異なるため price は mock を使用）
        topix=mock.topix,
        topix_change_pct=_change_pct(topix_r, mock.topix_change_pct),
        tse_growth=tse_growth,
        tse_growth_change_pct=tse_growth_change_pct,

        # 為替
        usdjpy=usdjpy_price,
        usdjpy_change=usdjpy_change,

        # 米国株
        sp500=_price(sp500_r, mock.sp500),
        sp500_change_pct=_change_pct(sp500_r, mock.sp500_change_pct),
        nasdaq=_price(nasdaq_r, mock.nasdaq),
        nasdaq_change_pct=_change_pct(nasdaq_r, mock.nasdaq_change_pct),
        sox=sox_price,
        sox_change_pct=sox_change_pct,

        # 金利（すべて mock フォールバック）
        us_2y_yield=us_2y_yield,
        us_10y_yield=us_10y_yield,
        jp_10y_yield=jp_10y_yield,

        # コモディティ
        wti_crude=_price(wti_r, mock.wti_crude),
        wti_change_pct=_change_pct(wti_r, mock.wti_change_pct),
        gold=_price(gold_r, mock.gold),
        gold_change_pct=_change_pct(gold_r, mock.gold_change_pct),

        # ボラティリティ
        vix=_price(vix_r, mock.vix),

        # 追加データ（yfinance では取得困難のため mock）
        turnover_trillion_yen=mock.turnover_trillion_yen,
        advance_decline_ratio=mock.advance_decline_ratio,
    )


# ============================================================
# 内部ヘルパー: 1銘柄を安全に取得する
# ============================================================

def _fetch_ticker(symbol: str, label: str) -> Optional[dict]:
    """
    1銘柄を yfinance で取得し、以下を返す:
        {
            "symbol"     : str,   # ティッカーシンボル
            "price"      : float, # 最新終値
            "prev_close" : float, # 前日終値
            "change_pct" : float, # 前日比 (%)
        }

    データが空・取得失敗の場合は None を返す（呼び出し元が fallback を担う）。
    """
    try:
        import yfinance as yf

        ticker = yf.Ticker(symbol)

        # 直近5日分の履歴を取得（市場が閉まっている日があっても2日分確保できるよう余裕を持つ）
        hist = ticker.history(period="5d")

        if hist is None or hist.empty:
            print(f"  [警告] {label} ({symbol}): データが空です → mock にフォールバック")
            return None

        # 終値列が存在するか確認
        if "Close" not in hist.columns:
            print(f"  [警告] {label} ({symbol}): Close 列が見つかりません → mock にフォールバック")
            return None

        # 有効な終値が2件以上あることを確認
        close_series = hist["Close"].dropna()
        if len(close_series) < 2:
            print(f"  [警告] {label} ({symbol}): 終値データが1件以下 → mock にフォールバック")
            return None

        price      = float(close_series.iloc[-1])
        prev_close = float(close_series.iloc[-2])

        if prev_close == 0:
            print(f"  [警告] {label} ({symbol}): 前日終値が0 → change_pct を 0.0 にします")
            change_pct = 0.0
        else:
            change_pct = round((price - prev_close) / prev_close * 100, 4)

        print(f"  [OK]   {label} ({symbol}): {price:,.2f}  ({change_pct:+.2f}%)")

        return {
            "symbol"     : symbol,
            "price"      : round(price, 4),
            "prev_close" : round(prev_close, 4),
            "change_pct" : change_pct,
        }

    except Exception as e:
        print(f"  [エラー] {label} ({symbol}): {e} → mock にフォールバック")
        return None


# ============================================================
# 内部ヘルパー: 取得結果から値を安全に取り出す
# ============================================================

def _price(result: Optional[dict], fallback: float) -> float:
    """price を返す。result が None なら fallback を使う。"""
    if result is None:
        return fallback
    return result["price"]


def _prev_close(result: Optional[dict], fallback: float) -> float:
    """prev_close を返す。result が None なら fallback を使う。"""
    if result is None:
        return fallback
    return result["prev_close"]


def _change_pct(result: Optional[dict], fallback: float) -> float:
    """change_pct を返す。result が None なら fallback を使う。"""
    if result is None:
        return fallback
    return result["change_pct"]
