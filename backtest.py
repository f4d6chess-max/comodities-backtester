import yfinance as yf
import matplotlib.pyplot as plt

copper = yf.download("HG=F", start="2020-01-01", end="2025-01-01")
print(copper.head())
copper['Close'].plot(figsize=(12,6), title="Copper Futures Price")
plt.show()
copper['MA20'] = copper['Close'].rolling(window=20).mean()
copper['MA50'] = copper['Close'].rolling(window=50).mean()

copper[['Close', 'MA20', 'MA50']].plot(figsize=(12,6), title="Copper with Moving Averages")
plt.show()
copper['Signal'] = 0
copper.loc[copper['MA20'] > copper['MA50'], 'Signal'] = 1
copper.loc[copper['MA20'] < copper['MA50'], 'Signal'] = -1
copper['Daily_Return'] = copper['Close'].pct_change()
copper['Strategy_Return'] = copper['Signal'].shift(1) * copper['Daily_Return']
copper['Cumulative_Strategy'] = (1 + copper['Strategy_Return']).cumprod()
copper['Cumulative_BuyHold'] = (1 + copper['Daily_Return']).cumprod()

sharpe_strategy = (copper['Strategy_Return'].mean() / copper['Strategy_Return'].std()) * (252 ** 0.5)
sharpe_buyhold = (copper['Daily_Return'].mean() / copper['Daily_Return'].std()) * (252 ** 0.5)

print(f"Strategy Sharpe: {sharpe_strategy:.2f}")
print(f"Buy & Hold Sharpe: {sharpe_buyhold:.2f}")

signal_changes = (copper['Signal'] != copper['Signal'].shift(1)).sum()
print(f"Number of signal changes: {signal_changes}")

copper[['Cumulative_Strategy', 'Cumulative_BuyHold']].plot(figsize=(12,6), title="Strategy vs Buy & Hold")
plt.show()

# Transaction costs: assume 0.1% cost per trade (round-trip), applied whenever the signal changes
trade_cost = 0.001  # 0.1% -- realistic-ish for futures

copper['Trade'] = (copper['Signal'] != copper['Signal'].shift(1)).astype(int)
copper['Cost'] = copper['Trade'] * trade_cost
copper['Strategy_Return_NetCost'] = copper['Strategy_Return'] - copper['Cost']
copper['Cumulative_Strategy_NetCost'] = (1 + copper['Strategy_Return_NetCost']).cumprod()

sharpe_strategy_netcost = (copper['Strategy_Return_NetCost'].mean() / copper['Strategy_Return_NetCost'].std()) * (252 ** 0.5)

print(f"Strategy Sharpe (net of costs): {sharpe_strategy_netcost:.2f}")
print(f"Final cumulative return, net of costs: {copper['Cumulative_Strategy_NetCost'].iloc[-1]:.2f}x")

copper[['Cumulative_Strategy', 'Cumulative_Strategy_NetCost', 'Cumulative_BuyHold']].plot(figsize=(12,6), title="Strategy vs Strategy (net of costs) vs Buy & Hold")
plt.show()
print(copper)
