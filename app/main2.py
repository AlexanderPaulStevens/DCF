import yfinance as yf

apple = yf.Ticker("AAPL")
data = apple.info  # fundamentals, financials, history, etc.

print(data)
