"""
logic/regime.py
市場レジーム（相場環境）の判定ロジック

ルールベースで現在の市場状態を判定します。
判定ロジックを変更したい場合はこのファイルを編集してください。
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.types import MarketData, MarketRegime
from config import (
    USDJPY_WEAK_YEN_THRESHOLD, USDJPY_STRONG_YEN_THRESHOLD,
    US10Y_HIGH, US10Y_RISING_CHANGE,
    VIX_HIGH, VIX_VERY_HIGH,
    SOX_STRONG_UP, SOX_STRONG_DOWN,
    OIL_RISING, OIL_FALLING,
    US_STOCK_STRONG_UP, US_STOCK_STRONG_DOWN,
)


def determine_regime(data: MarketData) -> MarketRegime:
    """
    市場データからレジームを判定する

    優先順位:
    1. リスクオフ（VIX高騰） → 最優先
    2. 強い半導体主導
    3. 円安主導
    4. 金利上昇主導
    5. リスクオン（穏やか上昇）
    6. その他

    Returns:
        MarketRegime: 判定された市場レジームと関連情報
    """

    # ---- 各フラグを判定 ----
    is_yen_weak = data.usdjpy_change >= USDJPY_WEAK_YEN_THRESHOLD
    is_yen_strong = data.usdjpy_change <= USDJPY_STRONG_YEN_THRESHOLD
    is_rate_high = data.us_10y_yield >= US10Y_HIGH
    is_vix_high = data.vix >= VIX_HIGH
    is_vix_very_high = data.vix >= VIX_VERY_HIGH
    is_sox_up = data.sox_change_pct >= SOX_STRONG_UP
    is_sox_down = data.sox_change_pct <= SOX_STRONG_DOWN
    is_oil_up = data.wti_change_pct >= OIL_RISING
    is_oil_down = data.wti_change_pct <= OIL_FALLING
    is_us_stock_up = data.sp500_change_pct >= US_STOCK_STRONG_UP
    is_us_stock_down = data.sp500_change_pct <= US_STOCK_STRONG_DOWN
    is_growth_down = data.tse_growth_change_pct < data.nikkei_change_pct - 0.5

    # ---- レジーム名と総評の決定（優先順位順） ----

    # 1. 強いリスクオフ
    if is_vix_very_high:
        regime = "強いリスクオフ相場"
        summary = (
            f"VIXが{data.vix:.1f}と急騰し、強烈なリスクオフ状態です。"
            "投資家が一斉にリスク資産を売却しており、安全資産（円・金・米国債）に資金が集まっています。"
            "相場全体で様子見姿勢が強く、無理な押し目買いは禁物です。"
        )

    # 2. リスクオフ（VIX高いが超過ではない）
    elif is_vix_high and is_us_stock_down:
        regime = "リスクオフ・慎重相場"
        summary = (
            f"VIXが{data.vix:.1f}と警戒水準に達し、米株も軟調です。"
            "市場全体にリスク回避ムードが漂っており、ディフェンシブ株や高配当株への逃避が見られます。"
            "短期的にはポジションを抑えた慎重なスタンスが有効です。"
        )

    # 3. 半導体主導の強気（SOX急騰）
    elif is_sox_up and data.nikkei_change_pct > 0:
        regime = "半導体・AI主導の強気相場"
        summary = (
            f"SOXが{data.sox_change_pct:+.1f}%と大幅上昇し、半導体・AI関連株が相場を牽引しています。"
            "米エヌビディアやAI投資の拡大期待が日本の半導体関連銘柄にも波及しており、"
            "東京エレクトロンやレーザーテックなどの主力株に資金が集中しています。"
        )

    # 4. 円安主導・輸出株優位
    elif is_yen_weak and not is_vix_high:
        regime = "円安主導・輸出株優位相場"
        summary = (
            f"ドル円が{data.usdjpy:.2f}円（+{data.usdjpy_change:.2f}円）と円安が進行し、"
            "自動車・機械などの輸出株に追い風が吹いています。"
            "日米金利差の拡大が円安の主因とみられ、しばらくこの流れが続く可能性があります。"
        )

    # 5. 円高・内需シフト
    elif is_yen_strong:
        regime = "円高リスク・内需株へのシフト相場"
        summary = (
            f"ドル円が{data.usdjpy:.2f}円（{data.usdjpy_change:.2f}円）と円高が進行しています。"
            "輸出関連株の採算悪化懸念から、内需・ディフェンシブ株への資金シフトが起きやすい局面です。"
        )

    # 6. 金利上昇・グロース逆風
    elif is_rate_high and is_growth_down:
        regime = "金利上昇によるグロース逆風相場"
        summary = (
            f"米10年金利が{data.us_10y_yield:.2f}%と高水準を維持し、"
            "将来の利益を現在価値に割り引くグロース株（高PER銘柄）に逆風が吹いています。"
            "東証グロース指数の下落幅が日経平均を上回っており、バリュー株優位の展開です。"
        )

    # 7. 原油上昇・商社資源優位
    elif is_oil_up:
        regime = "原油高・資源株優位相場"
        summary = (
            f"WTI原油が{data.wti_crude:.1f}ドル（{data.wti_change_pct:+.1f}%）と上昇し、"
            "総合商社や石油・エネルギー関連株に追い風が吹いています。"
            "一方、航空・運輸・消費関連にはコスト増の逆風となります。"
        )

    # 8. リスクオン（穏やかな上昇局面）
    elif is_us_stock_up and not is_vix_high:
        regime = "リスクオン・じり高相場"
        summary = (
            "米株が底堅く推移し、リスク選好ムードが続いています。"
            "特定のテーマに偏らず幅広い業種に買いが入る展開で、"
            "相場全体としては落ち着いた強気局面といえます。"
        )

    # 9. 方向感なし
    else:
        regime = "方向感乏しい相場（様子見局面）"
        summary = (
            "明確なテーマや方向感が出ていない膠着相場です。"
            "重要経済指標や決算発表を前に投資家が様子見姿勢を強めており、"
            "売買代金も低調になりやすい局面です。次の材料待ちの状態といえます。"
        )

    # ---- 重要変化ポイントの生成 ----
    key_changes = _build_key_changes(data)

    # ---- 主因の生成 ----
    main_drivers = _build_main_drivers(data)

    return MarketRegime(
        regime=regime,
        summary=summary,
        key_changes=key_changes,
        main_drivers=main_drivers,
    )


def _build_key_changes(data: MarketData) -> list:
    """
    市場の重要変化ポイントを最大3件生成する
    """
    changes = []

    # ドル円の変化
    if abs(data.usdjpy_change) >= 0.3:
        direction = "円安" if data.usdjpy_change > 0 else "円高"
        changes.append(
            f"【為替】ドル円が{data.usdjpy:.2f}円と{direction}進行"
            f"（{data.usdjpy_change:+.2f}円）。"
            f"{'輸出株に追い風' if data.usdjpy_change > 0 else '輸出株に逆風、内需株が相対優位'}。"
        )

    # 米10年金利の変化
    if data.us_10y_yield >= US10Y_HIGH:
        changes.append(
            f"【米金利】米10年金利が{data.us_10y_yield:.2f}%と高水準を維持。"
            "グロース株・不動産の割引率上昇リスクが継続。"
        )

    # SOXの動き
    if abs(data.sox_change_pct) >= 1.0:
        direction = "急騰" if data.sox_change_pct > 0 else "急落"
        changes.append(
            f"【半導体】SOX指数が{data.sox_change_pct:+.1f}%と{direction}。"
            f"{'東京エレクトロン・レーザーテックなど半導体関連株に波及' if data.sox_change_pct > 0 else '半導体セクター全体に売り圧力'}。"
        )

    # VIXの変化
    if data.vix >= VIX_HIGH:
        changes.append(
            f"【リスク】VIXが{data.vix:.1f}と警戒水準に上昇。"
            "市場の不安感が高まっており、小型株・グロース株は売られやすい状況。"
        )

    # 原油の変化
    if abs(data.wti_change_pct) >= 1.5:
        direction = "急騰" if data.wti_change_pct > 0 else "急落"
        changes.append(
            f"【原油】WTIが{data.wti_crude:.1f}ドルと{direction}（{data.wti_change_pct:+.1f}%）。"
            f"{'商社・資源株に追い風、空運・消費に逆風' if data.wti_change_pct > 0 else '商社・資源株に逆風、空運・消費に追い風'}。"
        )

    # 日経平均の大幅変動
    if abs(data.nikkei_change_pct) >= 1.0:
        direction = "大幅高" if data.nikkei_change_pct > 0 else "大幅安"
        changes.append(
            f"【日本株】日経平均が{data.nikkei:,.0f}円（{data.nikkei_change_pct:+.2f}%）と{direction}。"
        )

    # 上位3件を返す（重要なものが多い場合は絞る）
    return changes[:3] if len(changes) >= 3 else changes


def _build_main_drivers(data: MarketData) -> list:
    """
    相場を動かしている主因を3つ選択する
    各要因にスコアをつけて上位3つを選ぶ
    """
    drivers_with_score = []

    # ドル円
    usdjpy_score = abs(data.usdjpy_change) * 30
    if usdjpy_score > 10:
        direction = "円安が進行" if data.usdjpy_change > 0 else "円高が進行"
        drivers_with_score.append((usdjpy_score, (
            "ドル円",
            f"{direction}（{data.usdjpy:.2f}円、{data.usdjpy_change:+.2f}円）。"
            f"{'輸出株の採算改善期待が市場を支えています' if data.usdjpy_change > 0 else '輸出株の採算悪化懸念が重しになっています'}。"
        )))

    # 米10年金利
    rate_score = abs(data.us_10y_yield - 4.0) * 20 + (10 if data.us_10y_yield >= US10Y_HIGH else 0)
    drivers_with_score.append((rate_score, (
        "米10年金利",
        f"{data.us_10y_yield:.2f}%と{'高水準' if data.us_10y_yield >= US10Y_HIGH else '安定'}。"
        f"{'グロース・不動産には逆風、銀行・保険には追い風' if data.us_10y_yield >= US10Y_HIGH else '金利警戒感は一服、バランスのとれた環境'}。"
    )))

    # 米国株（S&P500）
    us_score = abs(data.sp500_change_pct) * 15
    if us_score > 5:
        direction = "堅調" if data.sp500_change_pct > 0 else "軟調"
        drivers_with_score.append((us_score, (
            "米国株（S&P500）",
            f"{direction}（{data.sp500_change_pct:+.2f}%）。"
            "前日の米国市場の流れが翌朝の日本株の方向性に影響を与えています。"
        )))

    # SOX（半導体）
    sox_score = abs(data.sox_change_pct) * 20
    if sox_score > 15:
        direction = "大幅高" if data.sox_change_pct > 0 else "大幅安"
        drivers_with_score.append((sox_score, (
            "SOX指数（半導体）",
            f"{direction}（{data.sox_change_pct:+.2f}%）。"
            "AI・半導体テーマへの資金流入/流出が東京エレクトロンなど主力銘柄の株価を動かしています。"
        )))

    # VIX
    vix_score = max(0, (data.vix - 15) * 5)
    if data.vix >= VIX_HIGH:
        drivers_with_score.append((vix_score, (
            "VIX（恐怖指数）",
            f"{data.vix:.1f}と高水準。"
            "市場参加者のリスク回避姿勢が強まっており、小型・グロース株が売られやすい環境です。"
        )))

    # 原油
    oil_score = abs(data.wti_change_pct) * 10
    if oil_score > 8:
        direction = "上昇" if data.wti_change_pct > 0 else "下落"
        drivers_with_score.append((oil_score, (
            "WTI原油",
            f"{direction}（{data.wti_crude:.1f}ドル、{data.wti_change_pct:+.1f}%）。"
            f"{'商社・資源関連株への追い風、空運・消費への逆風' if data.wti_change_pct > 0 else '资源株への逆風、消費・空運には下支え'}。"
        )))

    # スコアで降順ソートして上位3つを返す
    drivers_with_score.sort(key=lambda x: x[0], reverse=True)
    return [d for _, d in drivers_with_score[:3]]
