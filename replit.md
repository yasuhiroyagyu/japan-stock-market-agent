# Workspace

## Overview

pnpm workspace monorepo using TypeScript. Each package manages its own dependencies.
Also includes a standalone Python project for Japanese stock market analysis.

## Stack

- **Monorepo tool**: pnpm workspaces
- **Node.js version**: 24
- **Package manager**: pnpm
- **TypeScript version**: 5.9
- **API framework**: Express 5
- **Database**: PostgreSQL + Drizzle ORM
- **Validation**: Zod (`zod/v4`), `drizzle-zod`
- **API codegen**: Orval (from OpenAPI spec)
- **Build**: esbuild (CJS bundle)
- **Python**: 3.11 (installed for the Japan stock market analysis agent)

## Key Commands

- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from OpenAPI spec
- `pnpm --filter @workspace/db run push` — push DB schema changes (dev only)
- `pnpm --filter @workspace/api-server run dev` — run API server locally

See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details.

## Japan Stock Market Analysis Agent (Python)

A Python CLI/API tool that generates daily Japanese stock market reports.

### Directory: `project/`

```
project/
  main.py              # エントリーポイント (CLI + FastAPI)
  config.py            # 設定・定数
  requirements.txt     # 依存パッケージ
  services/
    market_data.py     # 市場データ取得（mock/live切り替え可）
    event_data.py      # 経済イベント取得
  logic/
    regime.py          # 市場レジーム判定
    sector_analysis.py # セクター別影響分析
    scoring.py         # スコア算出（0〜100）
  reports/
    generator.py       # 日本語レポート生成
  models/
    types.py           # データ構造定義
  sample_data/
    mock_market.json   # サンプルデータ
```

### How to Run

```bash
# CLIで実行（サンプルデータ）
cd project && python3 main.py

# FastAPIサーバーとして起動
cd project && python3 main.py --server

# 実データモード（要yfinance設定）
cd project && DATA_MODE=live python3 main.py
```

### API Endpoints (FastAPI)

- `GET /health` — Health check
- `GET /report` — Plain text Japanese report
- `GET /report/json` — JSON format report

### Dependencies

```bash
pip install fastapi uvicorn  # FastAPIサーバー用
pip install yfinance         # 実データ取得用（オプション）
```
