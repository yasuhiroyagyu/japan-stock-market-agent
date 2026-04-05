"""
logic/scoring.py
各種スコア算出ロジック（0〜100の数値）

各スコアの意味:
- risk_on          : 日本株リスクオン度（高いほどリスク選好相場）
- yen_weakness_boost: 円安追い風度（高いほど円安恩恵が大きい）
- rate_risk        : 金利警戒度（高いほど金利上昇リスクが大きい）
- growth_headwind  : グロース逆風度（高いほどグロース株に不利）
- cyclical_advantage: 景気敏感優位度（高いほど景気敏感株が有利）
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.types import MarketData, MarketScores
from config import VIX_HIGH, VIX_VERY_HIGH, US10Y_HIGH


def clamp(value: float, min_val: int = 0, max_val: int = 100) -> int:
    """値を0〜100の整数に収める"""
    return max(min_val, min(max_val, int(round(value))))


def calculate_scores(data: MarketData) -> MarketScores:
    """
    市場データから各種スコアを算出する

    各スコアは独立したロジックで計算し、最後に0〜100に正規化します。
    """

    # ========================
    # 1. 日本株リスクオン度（0〜100）
    # ========================
    # 高いスコア = リスク選好（株高・円安・VIX低）
    # 低いスコア = リスク回避（株安・円高・VIX高）

    risk_on_raw = 50.0

    # 米株が上昇 → リスクオン加点
    risk_on_raw += data.sp500_change_pct * 5

    # VIXが低い → リスクオン加点
    if data.vix < 15:
        risk_on_raw += 15
    elif data.vix < VIX_HIGH:
        risk_on_raw += 5
    elif data.vix < VIX_VERY_HIGH:
        risk_on_raw -= 15
    else:
        risk_on_raw -= 30

    # 日経平均が上昇 → 加点
    risk_on_raw += data.nikkei_change_pct * 4

    # 円安（ドル高）→ 加点（リスク選好の側面がある）
    risk_on_raw += data.usdjpy_change * 5

    risk_on = clamp(risk_on_raw)

    # ========================
    # 2. 円安追い風度（0〜100）
    # ========================
    # 高いスコア = 円安が強く、輸出株への追い風大
    # 低いスコア = 円高、輸出株への逆風

    yen_raw = 50.0
    # ドル円の変化幅で判定（1円の変化は±20点）
    yen_raw += data.usdjpy_change * 20

    # ドル円の絶対水準でも補正（150円以上なら追加加点）
    if data.usdjpy >= 155:
        yen_raw += 20
    elif data.usdjpy >= 150:
        yen_raw += 10
    elif data.usdjpy <= 140:
        yen_raw -= 10

    yen_weakness_boost = clamp(yen_raw)

    # ========================
    # 3. 金利警戒度（0〜100）
    # ========================
    # 高いスコア = 金利上昇リスクが高い（グロース・不動産に不利）
    # 低いスコア = 金利安定・低下（グロースに有利）

    rate_raw = 0.0

    # 米10年金利の水準で判定
    # 3.0%未満 → 警戒低い
    # 4.0%以上 → 警戒高い
    # 5.0%以上 → 非常に高い
    rate_raw += max(0, (data.us_10y_yield - 3.0)) * 30

    # 日本10年金利も考慮
    rate_raw += max(0, (data.jp_10y_yield - 0.5)) * 20

    # 日米金利差の変化（逆イールドは要注意）
    if data.us_2y_yield > data.us_10y_yield:  # 逆イールド
        rate_raw += 10

    rate_risk = clamp(rate_raw)

    # ========================
    # 4. グロース逆風度（0〜100）
    # ========================
    # 高いスコア = グロース株に不利な環境
    # 低いスコア = グロース株に有利な環境

    growth_raw = 0.0

    # 金利が高い → グロース逆風
    if data.us_10y_yield >= US10Y_HIGH:
        growth_raw += 30
    elif data.us_10y_yield >= 4.0:
        growth_raw += 15

    # VIXが高い → グロース逆風
    if data.vix >= VIX_VERY_HIGH:
        growth_raw += 30
    elif data.vix >= VIX_HIGH:
        growth_raw += 15

    # NASDAQが下落 → グロース逆風
    if data.nasdaq_change_pct < -1.0:
        growth_raw += 20
    elif data.nasdaq_change_pct < -0.5:
        growth_raw += 10

    # 東証グロースが日経を大幅アンダーパフォーム → 逆風確認
    growth_gap = data.nikkei_change_pct - data.tse_growth_change_pct
    if growth_gap > 1.0:
        growth_raw += 15

    growth_headwind = clamp(growth_raw)

    # ========================
    # 5. 景気敏感優位度（0〜100）
    # ========================
    # 高いスコア = 景気敏感株（自動車・素材・商社）が有利
    # 低いスコア = ディフェンシブ株が相対的に優位

    cyclical_raw = 50.0

    # 米株が強い → 景気敏感に追い風
    cyclical_raw += data.sp500_change_pct * 5

    # 円安 → 輸出系景気敏感株に追い風
    cyclical_raw += data.usdjpy_change * 8

    # 原油高 → 資源・商社に追い風
    cyclical_raw += data.wti_change_pct * 5

    # SOX高 → 半導体（景気敏感の一種）に追い風
    cyclical_raw += data.sox_change_pct * 3

    # VIX高 → 景気敏感に逆風
    if data.vix >= VIX_HIGH:
        cyclical_raw -= 20

    cyclical_advantage = clamp(cyclical_raw)

    return MarketScores(
        risk_on=risk_on,
        yen_weakness_boost=yen_weakness_boost,
        rate_risk=rate_risk,
        growth_headwind=growth_headwind,
        cyclical_advantage=cyclical_advantage,
    )
