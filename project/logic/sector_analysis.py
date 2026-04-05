"""
logic/sector_analysis.py
セクター別影響分析ロジック

市場データをもとに各セクターへの追い風・逆風・中立を判定します。
ルールを追加・変更したい場合はこのファイルを編集してください。
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.types import MarketData, SectorImpact
from config import (
    USDJPY_WEAK_YEN_THRESHOLD, USDJPY_STRONG_YEN_THRESHOLD,
    US10Y_HIGH, VIX_HIGH,
    SOX_STRONG_UP, SOX_STRONG_DOWN,
    OIL_RISING, OIL_FALLING,
)


def analyze_sectors(data: MarketData) -> SectorImpact:
    """
    市場データからセクター別の影響を分析する

    ルール一覧:
    - 円安 → 輸出株（自動車・機械）追い風
    - 円高 → 内需・医薬品追い風、輸出逆風
    - 金利高 → 銀行・保険追い風、不動産・グロース逆風
    - 原油高 → 商社・資源追い風、空運・消費逆風
    - 原油安 → 空運・消費追い風、商社・資源逆風
    - SOX高 → 半導体追い風
    - SOX安 → 半導体逆風
    - VIX高 → グロース・小型株逆風

    Returns:
        SectorImpact: 追い風・逆風・中立セクターのリスト
    """
    tailwind = []   # 追い風
    headwind = []   # 逆風
    neutral = []    # 中立

    # ---- 各セクターへの影響を判定 ----

    # 1. 輸出関連（自動車・機械）
    #    円安 → 追い風、円高 → 逆風
    if data.usdjpy_change >= USDJPY_WEAK_YEN_THRESHOLD:
        tailwind.append(
            f"自動車・機械・輸出製造業"
            f"（理由: 円安{data.usdjpy:.2f}円 → 海外売上の円換算が増加、採算改善）"
        )
    elif data.usdjpy_change <= USDJPY_STRONG_YEN_THRESHOLD:
        headwind.append(
            f"自動車・機械・輸出製造業"
            f"（理由: 円高進行 → 輸出採算が悪化、海外収益の目減り懸念）"
        )
    else:
        neutral.append("自動車・機械・輸出製造業（為替変動が限定的）")

    # 2. 半導体・電子部品
    #    SOX高 → 追い風、SOX安 → 逆風
    if data.sox_change_pct >= SOX_STRONG_UP:
        tailwind.append(
            f"半導体・電子部品"
            f"（理由: SOX{data.sox_change_pct:+.1f}% → 米国半導体株の上昇が東エレク・レーザーテックに波及）"
        )
    elif data.sox_change_pct <= SOX_STRONG_DOWN:
        headwind.append(
            f"半導体・電子部品"
            f"（理由: SOX{data.sox_change_pct:+.1f}% → 半導体セクター全体に売り圧力）"
        )
    else:
        neutral.append("半導体・電子部品（SOXの動きは限定的）")

    # 3. 銀行・保険
    #    金利高 → 追い風（利ざや拡大）、金利低 → 逆風
    if data.us_10y_yield >= US10Y_HIGH or data.jp_10y_yield >= 1.0:
        tailwind.append(
            f"銀行・保険・金融"
            f"（理由: 金利高水準 → 預貸金利ざや拡大、保険の運用利回り改善）"
        )
    elif data.us_10y_yield < 4.0 and data.jp_10y_yield < 0.8:
        headwind.append(
            "銀行・保険・金融（理由: 金利低下 → 利ざやの縮小圧力）"
        )
    else:
        neutral.append("銀行・保険・金融（金利環境は中立）")

    # 4. 商社・資源・エネルギー
    #    原油高 → 追い風、原油安 → 逆風
    if data.wti_change_pct >= OIL_RISING:
        tailwind.append(
            f"総合商社・資源・エネルギー"
            f"（理由: 原油高{data.wti_crude:.1f}ドル → 資源関連の利益拡大期待）"
        )
    elif data.wti_change_pct <= OIL_FALLING:
        headwind.append(
            f"総合商社・資源・エネルギー"
            f"（理由: 原油安 → 資源関連の利益縮小懸念）"
        )
    else:
        neutral.append("総合商社・資源・エネルギー（原油価格は安定）")

    # 5. 不動産・REIT
    #    金利高 → 逆風（借入コスト増・割引率上昇）
    if data.us_10y_yield >= US10Y_HIGH or data.jp_10y_yield >= 1.0:
        headwind.append(
            "不動産・REIT（理由: 金利上昇 → 物件価値の割引率上昇、借入コスト増）"
        )
    else:
        neutral.append("不動産・REIT（金利環境は中立）")

    # 6. グロース・テック（高PER）
    #    金利高 または VIX高 → 逆風
    is_growth_adverse = (
        data.us_10y_yield >= US10Y_HIGH or
        data.vix >= VIX_HIGH or
        data.tse_growth_change_pct < data.nikkei_change_pct - 0.5
    )
    if is_growth_adverse:
        reasons = []
        if data.us_10y_yield >= US10Y_HIGH:
            reasons.append(f"金利高（{data.us_10y_yield:.2f}%）→ DCF計算での将来利益の現在価値が低下")
        if data.vix >= VIX_HIGH:
            reasons.append(f"VIX高（{data.vix:.1f}）→ リスク回避で高PER株売り")
        headwind.append(
            f"グロース・テック（高PER銘柄）（理由: {'、'.join(reasons)}）"
        )
    else:
        neutral.append("グロース・テック（金利・リスク環境は比較的落ち着いている）")

    # 7. 空運・陸運
    #    原油高 → 逆風（燃料コスト増）、原油安 → 追い風
    if data.wti_change_pct >= OIL_RISING:
        headwind.append(
            "空運・陸運（理由: 原油高 → 燃料費コストが上昇、採算を圧迫）"
        )
    elif data.wti_change_pct <= OIL_FALLING:
        tailwind.append(
            "空運・陸運（理由: 原油安 → 燃料費低下によるコスト削減効果）"
        )
    else:
        neutral.append("空運・陸運（燃料コスト変動は軽微）")

    # 8. 内需・小売・食品（ディフェンシブ）
    #    リスクオフ・円高局面で相対的に強い
    if data.vix >= VIX_HIGH and data.usdjpy_change <= USDJPY_STRONG_YEN_THRESHOLD:
        tailwind.append(
            "内需・小売・食品（理由: リスクオフ＋円高 → 輸出株売りの裏返しでディフェンシブ株に資金流入）"
        )
    else:
        neutral.append("内需・小売・食品（市場環境は中立）")

    # 9. 医薬品・ヘルスケア
    #    リスクオフ局面で買われやすいディフェンシブ
    if data.vix >= VIX_HIGH:
        tailwind.append(
            "医薬品・ヘルスケア（理由: リスクオフ局面でディフェンシブ性が評価されやすい）"
        )
    else:
        neutral.append("医薬品・ヘルスケア（中立、個別材料次第）")

    # 10. 電力・ガス（公益）
    #     高金利局面では配当利回り魅力が相対的に低下
    if data.us_10y_yield >= US10Y_HIGH:
        headwind.append(
            "電力・ガス（公益）（理由: 高金利 → 配当利回りの相対的な魅力が低下）"
        )
    else:
        neutral.append("電力・ガス（公益）（金利環境は安定）")

    return SectorImpact(
        tailwind=tailwind,
        headwind=headwind,
        neutral=neutral,
    )
