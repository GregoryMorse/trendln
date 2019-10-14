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

This library can calculate and plot trend lines for any time series, not only for its primary intended purpose of financial analysis.

[Changelog »](./CHANGELOG.md)

---

==> Check out this article on [Programmatic Identification of Support/Resistance Trend lines with Python](https://towardsdatascience.com/programmatic-identification-of-support-resistance-trend-lines-with-python-d797a4a90530) or [alternatively here](https://medium.com/@gregory.morse1/programmatic-identification-of-support-resistance-trend-lines-with-python-d797a4a90530)
for details on how the library and its features are implemented and work.

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
	import yfinance as yf # requires yfinance - pip install yfinance
	tick = yf.Ticker('^GSPC') # S&P500
	hist = tick.history(period="max", rounding=True)
	minimaIdxs, maximaIdxs, pmin, pmax, mintrend, maxtrend, minwindows, maxwindows =
		calc_support_resistance(hist[-1000:].Close)
	minimaIdxs, maximaIdxs, pmin, pmax, mintrend, maxtrend, minwindows, maxwindows =
		calc_support_resistance(
		# list of data as float
		hist,

		# METHOD_NAIVE - any local minima or maxima only for a single interval (currently requires pandas)
		# METHOD_NAIVECONSEC - any local minima or maxima including those for consecutive constant intervals (currently requires pandas)
		# METHOD_NUMDIFF (default) - numerical differentiation determined local minima or maxima (requires findiff)
		extmethod = METHOD_NUMDIFF,
		
		# METHOD_NCUBED - simple exhuastive 3 point search (slowest)
		# METHOD_NSQUREDLOGN (default) - 2 point sorted slope search (fast)
		# METHOD_HOUGHPOINTS - Hough line transform optimized for points
		# METHOD_HOUGHLINES - image-based Hough line transform (requires scikit-image)
		# METHOD_PROBHOUGH - image-based Probabilistic Hough line transform (requires scikit-image)
		method=METHOD_NSQUREDLOGN,
		
		# window size when searching for trend lines prior to merging together
		window=125,
		
		# maximum percentage slope standard error
		errpct = 0.005,
		
		# for all METHOD_*HOUGH*, the smallest unit increment for discretization e.g. cents/pennies 0.01
		hough_scale=0.01
		
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
			# areaAvg - Reimann sum area of difference between best fit trend line
			#   and actual data points averaged per time unit
	# minwindows - list of windows each containing mintrend for that window
	# maxwindows - list of windows each containing maxtrend for that window

Plotting Calculations
---------------------
The **plot_support_resistance** function will calculate and plot the average
and top 2 support and resistance lines, along with marking extrema used with
a maximum history length, and otherwise identical arguments to the
calculation function.

	fig = plot_support_resistance(hist[-1000:].Close) # requires matplotlib - pip install matplotlib
	fig = plot_support_resistance(
		hist,
		xformatter = None, #x-axis data formatter turning numeric indexes to display output
		  # e.g. ticker.FuncFormatter(func) otherwise just display numeric indexes
		numbest = 2, #number of best support and best resistance lines to display
		fromwindows = True, #draw numbest best from each window, otherwise draw numbest across whole range
		extmethod = METHOD_NUMDIFF,
		method=METHOD_NSQUREDLOGN,
		window=125,
		errpct = 0.005,
		hough_prob_iter=10,
		sortError=False)
	# fig - returns matplotlib.pyplot.gcf() or the current figure
	plt.savefig('suppres.svg', format='svg')
	plt.show()
	
	fig = plot_sup_res_date(hist[-1000:].Close, hist[-1000:].index) #requires pandas
	fig = plot_sup_res_date( #automatic date formatter based on US trading calendar
		hist,
		idx, #date index from pandas
		numbest = 2,
		fromwindows = True,
		extmethod = METHOD_NUMDIFF,
		method=METHOD_NSQUREDLOGN,
		window=125,
		errpct = 0.005,
		hough_scale=0.01,
		hough_prob_iter=10,
		sortError=False)
	
	plot_sup_res_learn( #draw learning figures, included for reference material only
		curdir, #output directory for png and svg images
		hist) #pandas DataFrame containing Close and date index
	
![Example output of plotting support resistance](https://github.com/GregoryMorse/trendln/blob/master/img/suppres.svg)

Installation
------------

Install ``trendln`` using ``pip``:

    $ pip install trendln --upgrade --no-cache-dir


Install ``trendln`` using ``conda``:

    $ conda install -c GregoryMorse trendln

Installation sanity check:

	import trendln
	#requires yfinance library install, not a package requirement, but used to assist with sanity check
	#pip install yfinance
	directory = '.'
	trendln.test_sup_res(directory) #simple tests that all methods are executing correct, assertion or other error indicates problem

Requirements
------------

* [Python](https://www.python.org) >= 2.7, 3.4+
* [numpy](http://www.numpy.org) >= 1.15
* [findiff](https://github.com/maroba/findiff) >= 0.7.0 (if using default numerical differentiation method)
* [scikit-image](https://scikit-image.org) >= 0.14.0 (if using image-based Hough line transform or its probabilistic variant)
* [pandas](https://github.com/pydata/pandas) >= 0.23.1 (if using date plotting function, or using naive minima/maxima methods)
* [matplotlib](https://matplotlib.org) >= 3.1.0 (if using any plotting function)


License
-------

**trendln** is distributed under the **MIT License**. See the [LICENSE](./LICENSE) file in the release for details.

Support
-------

Any questions, issues or ideas can kindly be submitted for review.

**Gregory Morse**
<gregory.morse@live.com>
