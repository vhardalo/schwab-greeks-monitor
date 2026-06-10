# Schwab 0DTE Options Greeks & Liquidity Monitor

A production-ready quantitative trading terminal dashboard built using Python that interfaces directly with the Charles Schwab API. This system bypasses traditional options chain information fatigue by dynamically filtering, analyzing, and isolating high-probability 0DTE (Zero Days to Expiration) contracts for active intraday momentum trading.

## 📺 Live Video Demonstration
Watch a video walkthrough showing the real-time institutional terminal layout in action:

[![Schwab API Greeks Scanner](https://img.shields.io/badge/YouTube-Video_Walkthrough-red?style=for-the-badge&logo=youtube)](https://youtu.be/HX4jIMBm-_0)

---

## ⚡ Core Algorithmic Strategy & Architecture

The application acts as a **Gamma Acceleration Hunter**, specifically optimized to be run side-by-side with systematic technical indicators (such as an opening range breakout strategy).

1. **The Momentum Sweet Spot:** The background script queries the complete 0DTE options chain every 5 seconds, running an optimization filter to isolate the specific Call and Put contracts sitting closest to a target **0.40 Delta threshold**. This represents the statistical sweet spot where contract elasticity and Gamma acceleration expand exponentially during a sudden directional breakout.
2. **Institutional Liquidity Guardrails:** To eliminate execution slippage and protect against wide bid-ask spreads, the backend routes the data through a dual-pronged liquidity matrix requiring a strict baseline of daily volume and resting open interest. Ghost strikes or illiquid contracts are immediately filtered out.
3. **High-Performance Terminal UI:** Built utilizing the `Rich` console engine, the application employs fluid, in-place screen updates using `rich.live.Live`. This avoids brute-force terminal clearing, preventing screen flickering and maintaining a clean visual profile under fast market conditions.
4. **Automated Session Management:** The backend architecture manages the complete OAuth2 token authentication lifecycle, running automated access token recovery sequences smoothly to maintain data stream continuity without manual browser authentication restarts.

---

## 🛠️ Visual Interface Layout

The console structures raw JSON market data blocks into a clean, scannable institutional grid panel:

```text
 ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
 ┃  ⚡ TARGETED MOMENTUM RECON  |  Underlying: SPY = $751.57                                             ┃
 ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
 🎯 Strategy Target: High-Elasticity 0DTE Contracts (~0.40 Delta)
 ────────────────────────────────────────────────────────────────────────────────────────────────────────
 ┌─────────────────┬────────────────────────────────────────┬──────────────────────────────────────────┐
 │ GREEK METRIC    │ 🟩 OPTIMAL CALL OPTION                 │ 🟥 OPTIMAL PUT OPTION                    │
 ├─────────────────┼────────────────────────────────────────┼──────────────────────────────────────────┤
 │ Strike          │ 753.0                                  │ 750.0                                    │
 │ Bid / Ask       │ $1.01 x $1.02                          │ $0.99 x $1.00                            │
 │ Daily Volume    │ 24,530                                 │ 19,812                                   │
 │ Open Interest   │ 12,400                                 │ 8,950                                    │
 ├─────────────────┼────────────────────────────────────────┼──────────────────────────────────────────┤
 │ Delta (Speed)   │ +0.36                                  │ -0.36                                    │
 │ Gamma (Accel)   │ 0.0920                                 │ 0.0890                                   │
 │ Theta (Decay)   │ -0.99                                  │ -1.02                                    │
 │ Vega (Vol)      │ 0.0770                                 │ 0.0770                                   │
 └─────────────────┴────────────────────────────────────────┴──────────────────────────────────────────┘
 [dim]Strategy Target: High-Elasticity 0DTE (~0.40 Delta) | Refresh: 5s[/dim]
```
---
## 🚀 Quick Start & Intallation

### 1. Clone the Rpository
### 2. Install Dependecies
```bash
python3 -m pip install -r requirements.txt
(requires `requests`,`rich`, and `phython-dotenv`)
```
### 3. Configure Your Environment Secrets
Create a secure local configuration file to house your Schwab Developer Portal application credentials:
```bash
touch .env
```
Populate `.env` with your client details:
```bash
SCHWAB_APP_KEY=your_developer_app_key_here
SCHWAB_APP_SECRET=your_developer_app_secret_here
```
### 4. Initialize Authentication & Run
Generate your structural token baseline, then launch the live tracker:
```bash
python3 schwab_auth.py
python3 monitor_greeks.py
```
---
## 🛡️ Production Design Guardrails

* **API Rate Limiting Compliance:**  API Rate Limiting Compliance: The background fetch engine is structurally throttled to a 5-second cadence. This explicitly respects Charles Schwab’s API rate guidelines to completely mitigate `429 Too Many Requests` overhead, matching the execution frequency with structural clearing house batch calculations.

* **Security Isolation:** Tokens (`schwab_tokens.json`), local data audit caches (`sample_chain.json`), and environment primitives (`.env`) are explicitly blacklisted via `.gitignore` to guarantee deployment safety and completely eliminate credential leakage risks.