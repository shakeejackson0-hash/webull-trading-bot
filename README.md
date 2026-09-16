# Webull Trading Bot

A simple, configurable trading bot for Webull using the **official** Webull OpenAPI Python SDK.

> **Important**: This is for educational purposes. Trading involves risk of loss. Always start with the **sandbox/test environment** and paper trading. Never risk money you cannot afford to lose. Past performance is not indicative of future results.

## Features

- Official Webull OpenAPI SDK (supports US, HK, JP, etc.)
- Configurable simple strategies (SMA crossover example included)
- Account info, positions, and order management
- Easy to extend with your own strategies
- Environment variables for secure credentials

## Prerequisites

1. **Webull Account** with OpenAPI access approved  
   - Apply at: [Webull US OpenAPI](https://www.webull.com/center#openApiManagement) (or your region's portal)
   - Approval usually takes 1–2 business days
2. **App Key** and **App Secret** from the Webull developer portal
3. Python 3.8 – 3.14

## Setup

```bash
git clone https://github.com/shakeejackson0-hash/webull-trading-bot.git
cd webull-trading-bot
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configure credentials

Copy the example env file and fill in your details:

```bash
cp .env.example .env
```

Edit `.env`:

```
WEBULL_APP_KEY=your_app_key_here
WEBULL_APP_SECRET=your_app_secret_here
WEBULL_REGION=us
WEBULL_ENDPOINT=api.sandbox.webull.com   # Use sandbox first!
WEBULL_ACCOUNT_ID=                       # Leave blank to auto-fetch first account
```

**Sandbox (recommended for testing):**
- Endpoint: `api.sandbox.webull.com`
- Events: `events-api.sandbox.webull.com`

**Production:**
- Endpoint: `api.webull.com`

## Usage

### 1. Test connection & list accounts

```bash
python bot.py --action accounts
```

### 2. Check balance / positions

```bash
python bot.py --action balance
python bot.py --action positions
```

### 3. Run the example strategy (SMA crossover)

```bash
python bot.py --action run --symbol AAPL --dry-run
```

Remove `--dry-run` only when you are ready to place real orders (start in sandbox!).

### 4. Place a manual limit order (example)

```bash
python bot.py --action place --symbol AAPL --side BUY --qty 1 --price 180 --dry-run
```

## Project Structure

```
webull-trading-bot/
├── bot.py              # Main entry point
├── config.py           # Configuration loader
├── strategies/
│   └── sma_crossover.py  # Example strategy
├── requirements.txt
├── .env.example
└── README.md
```

## Adding Your Own Strategy

1. Create a new file in `strategies/`
2. Implement a class with a `generate_signal(data) -> str` method (`"BUY"`, `"SELL"`, or `"HOLD"`)
3. Import and use it in `bot.py`

## Disclaimer

This software is provided "as is" without warranty of any kind. The authors are not responsible for any financial losses incurred through the use of this bot. Use at your own risk. Always test thoroughly in the sandbox environment before going live.

## License

MIT
