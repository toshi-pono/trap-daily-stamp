# 🕒 trap daily stamp

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![English](https://img.shields.io/badge/English-README.md-blue)](README.md)

![trap daily stamp](docs/trap-daily-stamp.png)

## 📝 概要

trap daily stampは、スタンプ画像を定期的に更新することで時間によって変化するスタンプを実現するアプリケーションです。traQのスタンプ画像更新イベントを利用して、リアルタイムなスタンプ画像の更新を実現しています。

## ✨ 機能

アプリケーションは以下のような時間によって変化するスタンプを提供します：
- 📅 曜日
- 📆 月
- 📅 日付
- ⏰ 時間
- 🌤️ 天気
- 🌡️ 気温

## 🚀 デプロイ

このアプリケーションはtraPの部内PaaSであるNeoShowcaseにデプロイすることを想定しています。

### 🔧 前提条件

1. requirements.txtの生成:
```bash
uv pip compile pyproject.toml > requirements.txt
```

### ⚙️ NeoShowcase設定

#### 基本設定
- Deploy Type: Runtime
- Build Type: BuildPack
- URLs: https://{domain} -> 8080/TCP

#### 🔐 環境変数
必要な環境変数：
- `BASE_APP_URL`: アプリケーションのベースURL
- `BASE_URL`: サービスのベースURL
- `BOT_ACCESS_TOKEN`: Botのアクセストークン
- `BOT_VERIFICATION_TOKEN`: Botの検証トークン
- `OPEN_WEATHER_API_KEY`: OpenWeatherのAPIキー
- `PYTHONPATH`: `/workspace/ns-repo`に設定
- `SECRET_COOKIE`: セッション管理用のシークレットクッキー
- `TARGET_LATITUDE`: 天気情報を取得する緯度
- `TARGET_LONGITUDE`: 天気情報を取得する経度

## 🙏 謝辞

このプロジェクトは[AiotraQ](https://github.com/toshi-pono/aiotraq)を使用しています。
AiotraQはtraQのAPIとの連携やtraQ Botの実装に使用されています。

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています - 詳細はLICENSEファイルを参照してください。 