# 🕒 trap daily stamp

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![日本語](https://img.shields.io/badge/日本語-README_ja.md-blue)](README_ja.md)

![trap daily stamp](docs/trap-daily-stamp.png)

## 📝 Overview

trap daily stamp is an application that implements time-varying stamps by regularly updating stamp images. It utilizes traQ's stamp image update events to achieve real-time stamp image updates.

## ✨ Features

The application provides various types of stamps that change over time:
- 📅 Day (曜日)
- 📆 Month (月)
- 📅 Date (日付)
- ⏰ Hour (時間)
- 🌤️ Weather (天気)
- 🌡️ Temperature (気温)

## 🚀 Deployment

This application is designed to be deployed on traP's internal PaaS, NeoShowcase.

### 🔧 Prerequisites

1. Generate requirements.txt:
```bash
uv pip compile pyproject.toml > requirements.txt
```

### ⚙️ NeoShowcase Configuration

#### Basic Settings
- Deploy Type: Runtime
- Build Type: BuildPack
- URLs: https://{domain} -> 8080/TCP

#### 🔐 Environment Variables
Required environment variables:
- `BASE_APP_URL`: Base URL of the application
- `BASE_URL`: Base URL for the service
- `BOT_ACCESS_TOKEN`: Access token for the bot
- `BOT_VERIFICATION_TOKEN`: Verification token for the bot
- `OPEN_WEATHER_API_KEY`: API key for OpenWeather
- `PYTHONPATH`: Set to `/workspace/ns-repo`
- `SECRET_COOKIE`: Secret cookie for session management
- `TARGET_LATITUDE`: Latitude for weather information
- `TARGET_LONGITUDE`: Longitude for weather information

## 🙏 Acknowledgments

This project uses [AiotraQ](https://github.com/toshi-pono/aiotraq). 
AiotraQ is used for interacting with traQ's API and implementing traQ Bot functionality.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
