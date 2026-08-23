# Commodities MA Crossover Backtester

A backtest of a simple moving-average crossover trading strategy, tested across six commodities to understand *when and why* trend-following works — not just whether it does.

## TL;DR

Tested MA(20,50) crossover on copper, aluminum, silver, gold, crude oil, and platinum (2020–2025, net of a 0.1% per-trade cost). Results varied dramatically by asset:

| Asset | Strategy Sharpe | Buy & Hold Sharpe | Strategy Return | Buy & Hold Return | Outperformed? |
|---|---|---|---|---|---|
| Copper | 0.50 | 0.40 | 1.55x | 1.41x | ✅ |
| Aluminum | 0.61 | 0.40 | 1.77x | 1.39x | ✅ |
| Silver | 0.13 | 0.45 | 0.94x | 1.61x | ❌ |
| Crude Oil | 0.37 | -0.36 | 1.09x | 1.17x | 🔶 mixed |
| Gold | -0.21 | 0.75 | 0.80x | 1.72x | ❌ |
| Platinum | -0.47 | 0.11 | 0.37x | 0.91x | ❌ (worst) |

**Initial hypothesis:** the strategy would work best on "trending" assets. Gold falsified this — it had the smoothest, most consistent uptrend in the sample, and the strategy still lost money on it.

**Revised conclusion:** performance isn't explained by trending vs. not-trending. It's explained by whether an asset has *distinguishable regime shifts* — the strategy's inherent signal lag only pays off when a trend is large and well-defined enough (copper, aluminum) to absorb the cost of entering/exiting late. Smooth persistent trends (gold) and choppy/sideways action (silver, platinum) both punish the lag instead.

## Why this matters

MA crossover is one of the simplest possible trend-following strategies — if its performance depends this heavily on the *shape* of an asset's price history rather than a fixed edge, that's a useful, generalizable lesson about backtesting any strategy: a single "it works" or "it doesn't work" result on one asset tells you very little without testing across varied conditions.

## Methodology

- **Strategy:** long when 20-day MA > 50-day MA, short when 20-day MA < 50-day MA
- **Data:** daily close prices via `yfinance`, Jan 2020 – Jan 2025
- **Costs:** 0.1% deducted per trade (on every signal change)
- **Metrics:** cumulative return and annualized Sharpe ratio, strategy vs. buy-and-hold
- **No lookahead bias:** signal is shifted forward one day before being applied to returns (uses yesterday's signal on today's return, not today's signal on today's return)

## Repo structure

```
├── backtest.py              # single-asset version (original, copper)
├── multi_asset_backtest.py  # runs the strategy across multiple tickers, outputs comparison table + chart
├── README.md
└── LICENSE
```

## Requirements

```bash
pip install yfinance pandas matplotlib
```

## Limitations — read before taking any of this as trading advice

- **Single time period.** 2020–2025 was an unusual macro environment (pandemic crash, commodity supercycle, high inflation) — results may not generalize to other periods.
- **Single strategy variant.** Only MA(20,50) was tested; no parameter sweep across different window lengths.
- **Small sample.** Six assets is not enough to draw a statistically rigorous conclusion — the "regime shift" theory is a reasonable, evidence-backed explanation, not a proven law.
- **Simplified cost model.** Flat 0.1% per trade; no slippage, bid-ask spread, or position-sizing effects modeled.
- **This is a learning project, not investment advice.** Nothing here should be used to make real trading decisions.

## About

Built by Saikrishna Krishna Sethu, a Mineral & Metallurgical Engineering student at IIT (ISM) Dhanbad, as part of self-directed prep toward commodities-trading quant roles. Feedback welcome — especially from anyone with real trading/quant experience who can point out where the reasoning falls short.
