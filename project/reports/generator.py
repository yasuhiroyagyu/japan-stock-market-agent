"""
reports/generator.py
日本語レポート生成モジュール

市場データ・レジーム・セクター分析・スコアを受け取り、
最終的な日本語レポートを文字列として生成します。

【将来の拡張ポイント】
- Discord通知: discordwebhook ライブラリを使用
- LINE通知: LINE Messaging API
- メール送信: smtplib or SendGrid
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.types import MarketData, MarketRegime, SectorImpact, MarketScores, MarketReport


def generate_report(report: MarketReport) -> str:
    """
    MarketReport からフォーマットされた日本語レポートを生成する

    Args:
        report: 全データをまとめたMarketReportオブジェクト

    Returns:
        str: フォーマットされたレポート文字列
    """
    data = report.market_data
    regime = report.regime
    sectors = report.sector_impact
    scores = report.scores
    events = report.events

    lines = []

    # ヘッダー
    lines.append("=" * 60)
    lines.append(f"  本日の日本株市場サマリー　{report.report_date}")
    if report.data_source == "mock":
        lines.append("  ※ サンプルデータモードで動作中")
    lines.append("=" * 60)
    lines.append("")

    # 市場スナップショット
    lines.append("【 市場スナップショット 】")
    lines.append(_format_market_snapshot(data))
    lines.append("")

    # 市場レジームと総評
    lines.append("# 本日の市場レジーム")
    lines.append(f"  {regime.regime}")
    lines.append("")
    lines.append("# 総評")
    lines.append(f"  {regime.summary}")
    lines.append("")

    # 重要変化
    lines.append("# 重要変化")
    if regime.key_changes:
        for i, change in enumerate(regime.key_changes, 1):
            lines.append(f"  ①" if i == 1 else f"  ②" if i == 2 else f"  ③")
            lines.append(f"    {change}")
    else:
        lines.append("  特段の大きな変化は見られません")
    lines.append("")

    # 主因
    lines.append("# 日本株を動かしている主因")
    if regime.main_drivers:
        for i, (factor_name, factor_desc) in enumerate(regime.main_drivers, 1):
            lines.append(f"  要因{i}: 【{factor_name}】")
            lines.append(f"    {factor_desc}")
    else:
        lines.append("  明確な主因は特定できません")
    lines.append("")

    # セクター別インパクト
    lines.append("# セクター別インパクト")
    lines.append("  ▼ 追い風セクター")
    if sectors.tailwind:
        for s in sectors.tailwind:
            lines.append(f"    ✓ {s}")
    else:
        lines.append("    特になし")

    lines.append("  ▼ 逆風セクター")
    if sectors.headwind:
        for s in sectors.headwind:
            lines.append(f"    ✗ {s}")
    else:
        lines.append("    特になし")

    lines.append("  ▼ 中立セクター")
    if sectors.neutral:
        for s in sectors.neutral[:3]:  # 中立は多くなるので上位3件に絞る
            lines.append(f"    ─ {s}")
    else:
        lines.append("    特になし")
    lines.append("")

    # 今日の注目イベント
    lines.append("# 今日の注目イベント")
    if events:
        for event in events:
            importance_marker = "⚡" if event.importance == "高" else "▶" if event.importance == "中" else "▷"
            lines.append(f"  {importance_marker} イベント名: {event.name}（{event.time_jst} JST）")
            lines.append(f"    注目ポイント: {event.description}")
            lines.append(f"    想定される影響: {event.expected_impact}")
            lines.append("")
    else:
        lines.append("  本日の主要経済イベントはありません")
        lines.append("")

    # スコア
    lines.append("# 市場環境スコア（0〜100）")
    lines.append(_format_score_bar("日本株リスクオン度  ", scores.risk_on))
    lines.append(_format_score_bar("円安追い風度       ", scores.yen_weakness_boost))
    lines.append(_format_score_bar("金利警戒度         ", scores.rate_risk))
    lines.append(_format_score_bar("グロース逆風度     ", scores.growth_headwind))
    lines.append(_format_score_bar("景気敏感優位度     ", scores.cyclical_advantage))
    lines.append("")

    # 行動スタンス
    lines.append("# 行動スタンス")
    stances = _generate_action_stances(regime, sectors, scores, data)
    for stance in stances:
        lines.append(f"  ● {stance}")
    lines.append("")

    # 将来の拡張用フッター
    lines.append("-" * 60)
    lines.append("  ※ このレポートは市場理解の補助ツールです。投資判断は自己責任でお願いします。")
    lines.append("  ※ 将来の拡張: Discord/LINE通知、Web UIダッシュボードに対応予定。")
    lines.append("-" * 60)

    return "\n".join(lines)


def _format_market_snapshot(data: MarketData) -> str:
    """市場データのスナップショットを整形する"""
    snapshot_lines = []

    def fmt_idx(name: str, val: float, chg_pct: float, decimals: int = 2) -> str:
        arrow = "▲" if chg_pct >= 0 else "▼"
        color = "+" if chg_pct >= 0 else ""
        return f"  {name:<20} {val:>10,.{decimals}f}  {arrow} {color}{chg_pct:.2f}%"

    def fmt_rate(name: str, val: float) -> str:
        return f"  {name:<20} {val:>10.2f}%"

    snapshot_lines.append("  ─── 日本株 ───────────────────────────")
    snapshot_lines.append(fmt_idx("日経平均", data.nikkei, data.nikkei_change_pct, 0))
    snapshot_lines.append(fmt_idx("TOPIX", data.topix, data.topix_change_pct, 1))
    snapshot_lines.append(fmt_idx("東証グロース", data.tse_growth, data.tse_growth_change_pct, 1))

    snapshot_lines.append("  ─── 為替 ─────────────────────────────")
    usdjpy_arrow = "▲" if data.usdjpy_change >= 0 else "▼"
    snapshot_lines.append(
        f"  {'USD/JPY（ドル円）':<20} {data.usdjpy:>10.2f}円  {usdjpy_arrow} {data.usdjpy_change:+.2f}円"
    )

    snapshot_lines.append("  ─── 米国株 ───────────────────────────")
    snapshot_lines.append(fmt_idx("S&P500", data.sp500, data.sp500_change_pct, 0))
    snapshot_lines.append(fmt_idx("NASDAQ", data.nasdaq, data.nasdaq_change_pct, 0))
    snapshot_lines.append(fmt_idx("SOX（半導体）", data.sox, data.sox_change_pct, 0))

    snapshot_lines.append("  ─── 金利 ─────────────────────────────")
    snapshot_lines.append(fmt_rate("米2年金利", data.us_2y_yield))
    snapshot_lines.append(fmt_rate("米10年金利", data.us_10y_yield))
    snapshot_lines.append(fmt_rate("日本10年金利", data.jp_10y_yield))

    snapshot_lines.append("  ─── コモディティ / ボラ ───────────────")
    snapshot_lines.append(fmt_idx("WTI原油($/bbl)", data.wti_crude, data.wti_change_pct, 1))
    snapshot_lines.append(fmt_idx("金($/oz)", data.gold, data.gold_change_pct, 0))
    snapshot_lines.append(f"  {'VIX（恐怖指数）':<20} {data.vix:>10.1f}")

    if data.turnover_trillion_yen is not None:
        snapshot_lines.append(f"  {'売買代金（兆円）':<20} {data.turnover_trillion_yen:>10.1f}兆円")
    if data.advance_decline_ratio is not None:
        snapshot_lines.append(f"  {'騰落レシオ':<20} {data.advance_decline_ratio:>10.1f}%")

    return "\n".join(snapshot_lines)


def _format_score_bar(label: str, score: int, width: int = 20) -> str:
    """スコアをテキストバーとして表示する"""
    filled = int(score / 100 * width)
    bar = "█" * filled + "░" * (width - filled)
    return f"  {label}: [{bar}] {score:3d}/100"


def _generate_action_stances(
    regime: MarketRegime,
    sectors: SectorImpact,
    scores: MarketScores,
    data: MarketData,
) -> list:
    """
    市場状況に応じた行動スタンスを生成する
    最大3〜4件の具体的なスタンスを提示
    """
    stances = []

    # スタンス1: 相場全体への姿勢
    if scores.risk_on >= 65:
        stances.append(
            "相場全体はリスクオン。強気目線を維持しつつ、勢いのあるセクターに集中投資を検討。"
        )
    elif scores.risk_on <= 35:
        stances.append(
            "リスクオフ色が強い。無理な押し目買いは避け、現金比率を高めて次の好機を待つ。"
        )
    else:
        stances.append(
            "相場は方向感に乏しい。銘柄選別を重視し、好業績・低バリュエーション銘柄を選ぶ。"
        )

    # スタンス2: 注目セクター
    if sectors.tailwind:
        top_sector = sectors.tailwind[0].split("（")[0]
        stances.append(
            f"追い風セクター（{top_sector}）に短期的な注目が集まりやすい。"
            "ただしエントリーは過熱感の有無を確認してから。"
        )

    # スタンス3: 回避すべきセクター
    if sectors.headwind:
        top_headwind = sectors.headwind[0].split("（")[0]
        stances.append(
            f"逆風セクター（{top_headwind}）は慎重に。"
            "保有している場合はリスク量の見直しを。"
        )

    # スタンス4: 為替・金利への具体的な対応
    if scores.yen_weakness_boost >= 65:
        stances.append(
            "円安トレンドが継続中。為替ヘッジなしの輸出株・外国株ファンドが追い風を受けやすい。"
        )
    elif scores.rate_risk >= 65:
        stances.append(
            "金利警戒度が高い。高PER・高配当の不動産株は要注意。デュレーションの短い銘柄に絞る。"
        )

    return stances[:4]  # 最大4件


def generate_json_report(report: MarketReport) -> dict:
    """
    APIレスポンス用にレポートをJSON形式に変換する

    Returns:
        dict: JSON変換可能な辞書
    """
    data = report.market_data
    regime = report.regime
    sectors = report.sector_impact
    scores = report.scores
    events = report.events

    return {
        "report_date": report.report_date,
        "data_source": report.data_source,
        "market_snapshot": {
            "nikkei": {"value": data.nikkei, "change_pct": data.nikkei_change_pct},
            "topix": {"value": data.topix, "change_pct": data.topix_change_pct},
            "tse_growth": {"value": data.tse_growth, "change_pct": data.tse_growth_change_pct},
            "usdjpy": {"value": data.usdjpy, "change": data.usdjpy_change},
            "sp500": {"value": data.sp500, "change_pct": data.sp500_change_pct},
            "nasdaq": {"value": data.nasdaq, "change_pct": data.nasdaq_change_pct},
            "sox": {"value": data.sox, "change_pct": data.sox_change_pct},
            "us_2y_yield": data.us_2y_yield,
            "us_10y_yield": data.us_10y_yield,
            "jp_10y_yield": data.jp_10y_yield,
            "wti_crude": {"value": data.wti_crude, "change_pct": data.wti_change_pct},
            "gold": {"value": data.gold, "change_pct": data.gold_change_pct},
            "vix": data.vix,
        },
        "regime": {
            "name": regime.regime,
            "summary": regime.summary,
            "key_changes": regime.key_changes,
            "main_drivers": [
                {"factor": name, "description": desc}
                for name, desc in regime.main_drivers
            ],
        },
        "sectors": {
            "tailwind": sectors.tailwind,
            "headwind": sectors.headwind,
            "neutral": sectors.neutral,
        },
        "scores": {
            "risk_on": scores.risk_on,
            "yen_weakness_boost": scores.yen_weakness_boost,
            "rate_risk": scores.rate_risk,
            "growth_headwind": scores.growth_headwind,
            "cyclical_advantage": scores.cyclical_advantage,
        },
        "events": [
            {
                "name": e.name,
                "description": e.description,
                "expected_impact": e.expected_impact,
                "time_jst": e.time_jst,
                "importance": e.importance,
            }
            for e in events
        ],
        "action_stances": _generate_action_stances(regime, sectors, scores, data),
    }
