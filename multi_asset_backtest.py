import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

def run_ma_crossover_backtest(ticker, name, start="2020-01-01", end="2025-01-01", trade_cost=0.001):
    """
    Runs the exact same MA(20,50) crossover strategy built for copper,
    on any ticker. Returns a dict of results so we can compare across assets.
    """
    data = yf.download(ticker, start=start, end=end)

    data['MA20'] = data['Close'].rolling(window=20).mean()
    data['MA50'] = data['Close'].rolling(window=50).mean()

    data['Signal'] = 0
    data.loc[data['MA20'] > data['MA50'], 'Signal'] = 1
    data.loc[data['MA20'] < data['MA50'], 'Signal'] = -1

    data['Daily_Return'] = data['Close'].pct_change()
    data['Strategy_Return'] = data['Signal'].shift(1) * data['Daily_Return']

    # transaction costs, same as the copper version
    data['Trade'] = (data['Signal'] != data['Signal'].shift(1)).astype(int)
    data['Cost'] = data['Trade'] * trade_cost
    data['Strategy_Return_NetCost'] = data['Strategy_Return'] - data['Cost']

    data['Cumulative_Strategy_NetCost'] = (1 + data['Strategy_Return_NetCost']).cumprod()
    data['Cumulative_BuyHold'] = (1 + data['Daily_Return']).cumprod()

    sharpe_strategy = (data['Strategy_Return_NetCost'].mean() / data['Strategy_Return_NetCost'].std()) * (252 ** 0.5)
    sharpe_buyhold = (data['Daily_Return'].mean() / data['Daily_Return'].std()) * (252 ** 0.5)

    num_trades = data['Trade'].sum()

    result = {
        'Asset': name,
        'Ticker': ticker,
        'Strategy_Final': data['Cumulative_Strategy_NetCost'].iloc[-1],
        'BuyHold_Final': data['Cumulative_BuyHold'].iloc[-1],
        'Strategy_Sharpe': sharpe_strategy,
        'BuyHold_Sharpe': sharpe_buyhold,
        'Num_Trades': num_trades,
        'Outperformed': data['Cumulative_Strategy_NetCost'].iloc[-1] > data['Cumulative_BuyHold'].iloc[-1]
    }
    return result, data


# --- Run across multiple commodities ---
# HG=F  = Copper (original)
# ALI=F = Aluminum
# SI=F  = Silver (as a second "metal" comparison point)
# CL=F  = Crude Oil (a genuinely different commodity type -- energy, not metal)

assets = [
    ("HG=F", "Copper"),
    ("ALI=F", "Aluminum"),
    ("SI=F", "Silver"),
    ("CL=F", "Crude Oil"),
]

results = []
all_data = {}

for ticker, name in assets:
    try:
        result, data = run_ma_crossover_backtest(ticker, name)
        results.append(result)
        all_data[name] = data
        print(f"{name} ({ticker}): done")
    except Exception as e:
        print(f"{name} ({ticker}): FAILED -- {e}")

# --- Summary table ---
summary = pd.DataFrame(results)
summary = summary[['Asset', 'Ticker', 'Strategy_Final', 'BuyHold_Final',
                     'Strategy_Sharpe', 'BuyHold_Sharpe', 'Num_Trades', 'Outperformed']]
print("\n=== SUMMARY ACROSS ASSETS ===")
print(summary.to_string(index=False))

# --- Plot all cumulative returns together for visual comparison ---
plt.figure(figsize=(14, 8))
for name, data in all_data.items():
    plt.plot(data.index, data['Cumulative_Strategy_NetCost'], label=f"{name} - Strategy")
    plt.plot(data.index, data['Cumulative_BuyHold'], label=f"{name} - Buy&Hold", linestyle='--')
plt.legend()
plt.title("MA(20,50) Crossover Strategy vs Buy & Hold — Across Commodities")
plt.ylabel("Cumulative Return (multiplier)")
plt.show()
