"""
main.py
日本株市場分析エージェント - メイン実行ファイル

【実行方法】
  CLIで実行:
    python main.py              # サンプルデータで実行
    DATA_MODE=live python main.py  # 実データで実行（要yfinance設定）

  FastAPI サーバーとして起動:
    python main.py --server

  特定のモードを指定:
    DATA_MODE=mock python main.py
    DATA_MODE=live python main.py

【FastAPI エンドポイント】
  GET /report        → 日本語レポートのテキスト
  GET /report/json   → JSON形式のレポート
  GET /health        → ヘルスチェック
"""

import sys
import os
import argparse
from datetime import datetime

# プロジェクトルートをパスに追加（モジュールのインポートのため）
sys.path.insert(0, os.path.dirname(__file__))

from services.market_data import fetch_market_data
from services.event_data import fetch_events, get_boj_watch_events
from logic.regime import determine_regime
from logic.sector_analysis import analyze_sectors
from logic.scoring import calculate_scores
from reports.generator import generate_report, generate_json_report
from models.types import MarketReport
from config import DATA_MODE


def run_analysis() -> MarketReport:
    """
    市場分析のメインフロー
    1. データ取得 → 2. レジーム判定 → 3. セクター分析 → 4. スコア算出 → 5. レポート生成

    Returns:
        MarketReport: 全データをまとめたレポートオブジェクト
    """
    print("[1/5] 市場データを取得中...")
    market_data = fetch_market_data()

    print("[2/5] イベント情報を取得中...")
    events = fetch_events()
    boj_events = get_boj_watch_events()
    all_events = events + boj_events  # 通常イベント + 日銀イベントを結合

    print("[3/5] 市場レジームを判定中...")
    regime = determine_regime(market_data)

    print("[4/5] セクター影響を分析中...")
    sector_impact = analyze_sectors(market_data)

    print("[5/5] スコアを算出中...")
    scores = calculate_scores(market_data)

    report = MarketReport(
        market_data=market_data,
        regime=regime,
        sector_impact=sector_impact,
        scores=scores,
        events=all_events,
        report_date=datetime.now().strftime("%Y年%m月%d日 %H:%M"),
        data_source=DATA_MODE,
    )

    return report


def run_cli():
    """CLIモードでレポートを表示する"""
    print("\n" + "─" * 60)
    print("  🇯🇵 日本株市場分析エージェント 起動中...")
    print(f"  データモード: {DATA_MODE.upper()}")
    print("─" * 60 + "\n")

    report = run_analysis()
    report_text = generate_report(report)

    print("\n" + report_text)


def run_server():
    """FastAPI サーバーモードで起動する"""
    try:
        import uvicorn
        from fastapi import FastAPI
        from fastapi.responses import PlainTextResponse, JSONResponse
    except ImportError:
        print("[エラー] FastAPI/Uvicorn が未インストールです。")
        print("  pip install fastapi uvicorn を実行してください。")
        sys.exit(1)

    app = FastAPI(
        title="日本株市場分析API",
        description="日本株の市場環境を分析し、日本語レポートを生成するAPI",
        version="1.0.0",
    )

    @app.get("/health")
    def health_check():
        """ヘルスチェックエンドポイント"""
        return {"status": "ok", "data_mode": DATA_MODE}

    @app.get("/report", response_class=PlainTextResponse)
    def get_text_report():
        """日本語テキストレポートを返す"""
        report = run_analysis()
        return generate_report(report)

    @app.get("/report/json")
    def get_json_report():
        """JSON形式のレポートを返す"""
        report = run_analysis()
        return JSONResponse(content=generate_json_report(report))

    from config import API_HOST, API_PORT
    print(f"\n FastAPI サーバー起動中: http://{API_HOST}:{API_PORT}")
    print(f"  ドキュメント: http://{API_HOST}:{API_PORT}/docs")
    print(f"  レポート取得: http://{API_HOST}:{API_PORT}/report")
    uvicorn.run(app, host=API_HOST, port=API_PORT)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="日本株市場分析エージェント",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python main.py                  # CLIでレポートを表示（サンプルデータ）
  python main.py --server         # FastAPIサーバーとして起動
  DATA_MODE=live python main.py   # 実データを使用（yfinance設定が必要）
        """
    )
    parser.add_argument(
        "--server",
        action="store_true",
        help="FastAPIサーバーとして起動する",
    )
    args = parser.parse_args()

    if args.server:
        run_server()
    else:
        run_cli()
