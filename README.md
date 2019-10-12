# trendln

Support and Resistance Trend lines Calculator for Financial Analysis
====================================================================

[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/trendln)](https://pypi.python.org/pypi/trendln)
[![PyPI - Version](https://img.shields.io/pypi/v/trendln.svg?maxAge=60)](https://pypi.python.org/pypi/trendln)
[![PyPI - Status](https://img.shields.io/pypi/status/trendln.svg?maxAge=60)](https://pypi.python.org/pypi/trendln)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/trendln.svg?maxAge=2592000&label=installs&color=%2327B1FF)](https://pypi.python.org/pypi/trendln)
[![PyPI - License](https://img.shields.io/pypi/l/trendln)](https://pypi.python.org/pypi/trendln)
[![PyPI - Implementation](https://img.shields.io/pypi/implementation/trendln)](https://pypi.python.org/pypi/trendln)
[![GitHub stars](https://img.shields.io/github/stars/GregoryMorse/trendln?style=social)](https://github.com/GregoryMorse/trendln)

Note
----

[Changelog »](./CHANGELOG.md)

---

==> Check out this article on [Programmatic Identification of Support/Resistance Trend lines with Python](https://medium.com/p/d797a4a90530)
for details on how the library works and its features.

---

Quick Start
===========

Calculation Only
----------------

The **calc_support_resistance** function will calculate all support and
resistance information including local extrema, average and their
trend lines using several different methods:

	import trendln
	# this will serve as an example for security or index closing prices
	import yfinance as yf # pip install yfinance
	tick = yf.Ticker('^GSPC') # S&P500
	hist = tick.history(period="max", rounding=True)
	minimaIdxs, maximaIdxs, pmin, pmax, mintrend, maxtrend =
		calc_support_resistance(hist[-1000:])
	minimaIdxs, maximaIdxs, pmin, pmax, mintrend, maxtrend =
		calc_support_resistance(
		# list of data
		hist,

		# METHOD_NAIVE - any local minima or maxima only for a single interval
		# METHOD_NAIVECONSEC - any local minima or maxima including those for consecutive constant intervals
		# METHOD_NUMDIFF (default) - numerical differentiation determined local minima or maxima (requires findiff)
		extmethod = METHOD_NUMDIFF,
		
		# METHOD_NCUBED - simple exhuastive 3 point search (slowest)
		# METHOD_NSQUREDLOGN - 2 point sorted slope search (fast)
		# METHOD_HOUGHPOINTS - Hough line transform optimized for points
		# METHOD_HOUGHLINES - Hough line transform (requires scikit-image)
		# METHOD_PROBHOUGH - Probabilistic Hough line transform (requires scikit-image)
		method=METHOD_NSQUREDLOGN,
		
		# window size when searching for trend lines prior to merging together
		window=125,
		
		# maximum percentage slope standard error
		errpct = 0.005,
		
		# only for METHOD_PROBHOUGH, number of iterations to run
		hough_prob_iter=10,
		
		# sort by area under wrong side of curve, otherwise sort by slope standard error
		sortError=False)
	# minimaIdxs - sorted list of indexes to the local minima
	# maximaIdxs - sorted list of indexes to the local maxima
	# pmin - [slope, intercept] of average best fit line through all local minima points
	# pmax - [slope, intercept] of average best fit line through all local maxima points
	# mintrend - sorted list containing (points, result) for local minima trend lines
	# maxtrend - sorted list containing (points, result) for local maxima trend lines
		# points - list of indexes to points in trend line
		# result - (slope, intercept, SSR, slopeErr, interceptErr, areaAvg)
			# slope - slope of best fit trend line
			# intercept - y-intercept of best fit trend line
			# SSR - sum of squares due to regression
			# slopeErr - standard error of slope
			# interceptErr - standard error of intercept
			# areaAvg - Reimann sum area of difference between best fit trend line and actual data points averaged per time unit

Plotting Calculations
---------------------
The **plot_support_resistance** function will calculate and plot the average
and top 2 support and resistance lines, along with marking extrema used with
a maximum history length, and otherwise identical arguments to the
calculation function.

	fig = plot_support_resistance(hist, 1000)
	fig = plot_support_resistance(
		hist,
		MaxDays, # maximum time period used from the data provided
		extmethod = METHOD_NUMDIFF,
		method=METHOD_NSQUREDLOGN,
		window=125,
		errpct = 0.005,
		hough_prob_iter=10,
		sortError=False)
	# fig - returns matplotlib.pyplot.gcf() or the current figure
	plt.savefig('suppres.svg', format='svg')
	plt.show()
	
![Example output of plotting support resistance](https://github.com/GregoryMorse/trendln/blob/master/img/suppres.svg)

Installation
------------

Install ``trendln`` using ``pip``:

    $ pip install trendln --upgrade --no-cache-dir


Install ``trendln`` using ``conda``:

    $ conda install -c GregoryMorse trendln


Requirements
------------

* [Python](https://www.python.org) >= 2.7, 3.4+
* [Pandas](https://github.com/pydata/pandas) >= 0.23.1
* [Numpy](http://www.numpy.org) >= 1.11.1


License
-------

**trendln** is distributed under the **MIT License**. See the [LICENSE](./LICENSE) file in the release for details.

Support
-------

Any questions, issues or ideas can kindly be submitted for review.

**Gregory Morse**
<gregory.morse@live.com>
