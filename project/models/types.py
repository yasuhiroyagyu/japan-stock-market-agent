"""
models/types.py
データ構造の定義ファイル
アプリ全体で使用するデータクラスをここで定義します
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class MarketData:
    """市場データを保持するクラス"""

    # 日本株指数
    nikkei: float = 0.0           # 日経平均
    nikkei_change_pct: float = 0.0
    topix: float = 0.0            # TOPIX
    topix_change_pct: float = 0.0
    tse_growth: float = 0.0       # 東証グロース指数
    tse_growth_change_pct: float = 0.0

    # 為替
    usdjpy: float = 0.0           # ドル円
    usdjpy_change: float = 0.0

    # 米国株
    sp500: float = 0.0            # S&P500
    sp500_change_pct: float = 0.0
    nasdaq: float = 0.0           # NASDAQ
    nasdaq_change_pct: float = 0.0
    sox: float = 0.0              # フィラデルフィア半導体指数 (SOX)
    sox_change_pct: float = 0.0

    # 金利
    us_2y_yield: float = 0.0      # 米2年金利 (%)
    us_10y_yield: float = 0.0     # 米10年金利 (%)
    jp_10y_yield: float = 0.0     # 日本10年金利 (%)

    # コモディティ
    wti_crude: float = 0.0        # WTI原油 (ドル/バレル)
    wti_change_pct: float = 0.0
    gold: float = 0.0             # 金 (ドル/オンス)
    gold_change_pct: float = 0.0

    # ボラティリティ
    vix: float = 0.0              # VIX恐怖指数

    # 追加データ（任意）
    turnover_trillion_yen: Optional[float] = None  # 東証売買代金（兆円）
    advance_decline_ratio: Optional[float] = None  # 騰落レシオ


@dataclass
class EventData:
    """イベントデータを保持するクラス"""
    name: str = ""                # イベント名
    description: str = ""         # 説明
    expected_impact: str = ""     # 想定される影響
    time_jst: str = ""            # 時刻（日本時間）
    importance: str = "中"        # 重要度: 高/中/低


@dataclass
class MarketRegime:
    """市場レジーム（相場環境）の判定結果"""
    regime: str = ""              # レジーム名（例：「円安主導の輸出株優位」）
    summary: str = ""             # 総評
    key_changes: list = field(default_factory=list)   # 重要変化（3件）
    main_drivers: list = field(default_factory=list)  # 主因（3件）


@dataclass
class SectorImpact:
    """セクター別影響分析"""
    tailwind: list = field(default_factory=list)   # 追い風セクター
    headwind: list = field(default_factory=list)   # 逆風セクター
    neutral: list = field(default_factory=list)    # 中立セクター


@dataclass
class MarketScores:
    """各種スコア（0〜100）"""
    risk_on: int = 50             # 日本株リスクオン度
    yen_weakness_boost: int = 50  # 円安追い風度
    rate_risk: int = 50           # 金利警戒度
    growth_headwind: int = 50     # グロース逆風度
    cyclical_advantage: int = 50  # 景気敏感優位度


@dataclass
class MarketReport:
    """最終レポートのまとめ"""
    market_data: MarketData = field(default_factory=MarketData)
    regime: MarketRegime = field(default_factory=MarketRegime)
    sector_impact: SectorImpact = field(default_factory=SectorImpact)
    scores: MarketScores = field(default_factory=MarketScores)
    events: list = field(default_factory=list)
    report_date: str = ""
    data_source: str = "mock"     # "mock" or "live"
