import trendln
import matplotlib.pyplot as plt
# this will serve as an example for security or index closing prices, or low and high prices
import yfinance as yf # requires yfinance - pip install yfinance
tick = yf.Ticker('^GSPC') # S&P500
hist = tick.history(period="max", rounding=True)
mins, maxs = trendln.calc_support_resistance(hist[-1000:].Close)
minimaIdxs, pmin, mintrend, minwindows = trendln.calc_support_resistance((hist[-1000:].Low, None)) #support only
mins, maxs = trendln.calc_support_resistance((hist[-1000:].Low, hist[-1000:].High))
(minimaIdxs, pmin, mintrend, minwindows), (maximaIdxs, pmax, maxtrend, maxwindows) = mins, maxs
minimaIdxs, maximaIdxs = trendln.get_extrema(hist[-1000:].Close)
maximaIdxs = trendln.get_extrema((None, hist[-1000:].High)) #maxima only
minimaIdxs, maximaIdxs = trendln.get_extrema((hist[-1000:].Low, hist[-1000:].High))
fig = trendln.plot_support_resistance(hist[-1000:].Close) # requires matplotlib - pip install matplotlib
plt.savefig('suppres.svg', format='svg')
plt.show()
plt.clf() #clear figure
fig = trendln.plot_sup_res_date((hist[-1000:].Low, hist[-1000:].High), hist[-1000:].index) #requires pandas
plt.savefig('suppres.svg', format='svg')
plt.show()
plt.clf() #clear figure
curdir = '.'
trendln.plot_sup_res_learn(curdir, hist)
