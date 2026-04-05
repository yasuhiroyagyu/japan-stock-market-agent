"""
services/event_data.py
経済イベント取得サービス

今日の注目経済イベントを取得します。

【実際のAPIに差し替えるには】
- Investing.com の経済カレンダーAPI
- Trading Economics API
- J-Quants の日本株イベントカレンダー
- Bloomberg Economic Calendar API
"""

import json
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.types import EventData
from config import DATA_MODE, MOCK_DATA_PATH


def fetch_events() -> list:
    """
    今日の注目経済イベントを取得する
    DATA_MODE に応じてモック/実データを切り替えます
    """
    if DATA_MODE == "live":
        return fetch_live_events()
    else:
        return fetch_mock_events()


def fetch_mock_events() -> list:
    """
    サンプルデータからイベント情報を読み込む
    """
    with open(MOCK_DATA_PATH, "r", encoding="utf-8") as f:
        raw = json.load(f)

    events = []
    for e in raw.get("events", []):
        events.append(EventData(
            name=e["name"],
            description=e["description"],
            expected_impact=e["expected_impact"],
            time_jst=e.get("time_jst", ""),
            importance=e.get("importance", "中"),
        ))

    return events


def fetch_live_events() -> list:
    """
    実際のAPIから今日のイベントを取得する

    TODO: 以下のいずれかのAPIを使ってください

    オプション1: Investing.com スクレイピング（非公式）
    オプション2: Trading Economics API
      - https://tradingeconomics.com/api/
      - 月次プランで経済カレンダーが取得可能

    オプション3: FinancialModelingPrep
      - https://financialmodelingprep.com/developer/docs/
      - /v3/economic_calendar エンドポイント

    例（Trading Economics）:
    import requests
    today = datetime.now().strftime("%Y-%m-%d")
    url = f"https://api.tradingeconomics.com/calendar/country/japan,united-states/{today}"
    headers = {"Authorization": "Client your_api_key"}
    response = requests.get(url, headers=headers)
    data = response.json()
    # ... データを EventData に変換 ...
    """
    print("[警告] イベントAPIが未設定です。モックイベントを使用します。")
    return fetch_mock_events()


def get_boj_watch_events() -> list:
    """
    日銀関連の固定イベントを生成する
    実際の日銀スケジュールは日本銀行のウェブサイトを参照

    TODO: 日銀の政策会合スケジュールをAPIまたは手動で管理してください
    参考: https://www.boj.or.jp/mopo/mpmsche_mbo/index.htm/
    """
    today = datetime.now()
    month = today.month

    # 簡易スケジュール（実際は公式発表を参照すること）
    boj_events = []

    # 月に応じた日銀関連コメント（簡易版）
    if month in [1, 4, 7, 10]:
        boj_events.append(EventData(
            name="日銀展望レポート（Outlook Report）",
            description="四半期ごとの経済・物価見通し。金融政策スタンスの変化を確認する重要文書。",
            expected_impact="タカ派的内容なら円高・金利上昇→輸出株逆風",
            time_jst="14:00頃",
            importance="高",
        ))

    return boj_events
