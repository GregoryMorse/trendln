# trendln

Support and Resistance Trend lines Calculator for Financial Analysis
====================================================================

[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/trendln)](https://pypi.python.org/pypi/trendln)
[![PyPI - Version](https://img.shields.io/pypi/v/trendln.svg?maxAge=60)](https://pypi.python.org/pypi/trendln)
[![PyPI - Status](https://img.shields.io/pypi/status/trendln.svg?maxAge=60)](https://pypi.python.org/pypi/trendln)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/trendln.svg?maxAge=2592000&label=installs&color=%2327B1FF)](https://pypi.python.org/pypi/trendln)
[![PyPI - License](https://img.shields.io/pypi/l/trendln)](https://pypi.python.org/pypi/trendln)
[![PyPI - Implementation](https://img.shields.io/pypi/implementation/trendln)](https://pypi.python.org/pypi/trendln)
[![Latest push build on default branch](https://travis-ci.com/GregoryMorse/trendln.svg?branch=master)](https://travis-ci.com/GregoryMorse/trendln)
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
	# this will serve as an example for security or index closing prices, or low and high prices
	import yfinance as yf # requires yfinance - pip install yfinance
	tick = yf.Ticker('^GSPC') # S&P500
	hist = tick.history(period="max", rounding=True)
	mins, maxs = calc_support_resistance(hist[-1000:].Close)
	mins = calc_support_resistance((hist[-1000:].Low, None)) #support only
	mins, maxs = calc_support_resistance((hist[-1000:].Low, hist[-1000:].High))
	(minimaIdxs, pmin, mintrend, minwindows), (maximaIdxs, pmax, maxtrend, maxwindows) = mins, maxs

	(minimaIdxs, pmin, mintrend, minwindows), (maximaIdxs, pmax, maxtrend, maxwindows) =
		calc_support_resistance(
		# list/numpy ndarray/pandas Series of data as bool/int/float and if not a list also unsigned
		# or 2-tuple (support, resistance) where support and resistance are 1-dimensional array-like or one or the other is None
		# can calculate only support, only resistance, both for different data, or both for identical data
		h,

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
		sortError=False,
		
		# accuracy if using METHOD_NUMDIFF for example 5-point stencil is accuracy=3
		accuracy=1)
	# if h is a 2-tuple with one value as None, then a 2-tuple is not returned, but the appropriate tuple instead
	# minimaIdxs - sorted list of indexes to the local minima
	# pmin - [slope, intercept] of average best fit line through all local minima points
	# mintrend - sorted list containing (points, result) for local minima trend lines
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
	
	# maximaIdxs - sorted list of indexes to the local maxima
	# pmax - [slope, intercept] of average best fit line through all local maxima points
	# maxtrend - sorted list containing (points, result) for local maxima trend lines
		#see for mintrend above
	# maxwindows - list of windows each containing maxtrend for that window

The **get_extrema** function will calculate all of the local minima and local maxima
without performing the full trend line calculation.
	
	minimaIdxs, maximaIdxs = get_extrema(hist[-1000:].Close)
	maximaIdxs = get_extrema((None, hist[-1000:].High)) #maxima only
	minimaIdxs, maximaIdxs = get_extrema((hist[-1000:].Low, hist[-1000:].High))
	
	minimaIdxs, maximaIdxs = get_extrema(
		h,
		extmethod=METHOD_NUMDIFF,
		accuracy=1)
	# parameters and results are as per defined for calc_support_resistance

Plotting Calculations
---------------------
The **plot_support_resistance** function will calculate and plot the average
and top 2 support and resistance lines, along with marking extrema used with
a maximum history length, and otherwise identical arguments to the
calculation function.

	fig = plot_support_resistance(hist[-1000:].Close) # requires matplotlib - pip install matplotlib
	plt.savefig('suppres.svg', format='svg')
	plt.show()
	plt.clf() #clear figure
	
	fig = plot_support_resistance(
		hist, #as per h for calc_support_resistance
		xformatter = None, #x-axis data formatter turning numeric indexes to display output
		  # e.g. ticker.FuncFormatter(func) otherwise just display numeric indexes
		numbest = 2, #number of best support and best resistance lines to display
		fromwindows = True, #draw numbest best from each window, otherwise draw numbest across whole range
		pctbound = 0.1, # bound trend line based on this maximum percentage of the data range above the high or below the low
		extmethod = METHOD_NUMDIFF,
		method=METHOD_NSQUREDLOGN,
		window=125,
		errpct = 0.005,
		hough_prob_iter=10,
		sortError=False,
		accuracy=1)
	# other parameters as per calc_support_resistance
	# fig - returns matplotlib.pyplot.gcf() or the current figure
	
	fig = plot_sup_res_date((hist[-1000:].Low, hist[-1000:].High), hist[-1000:].index) #requires pandas
	plt.savefig('suppres.svg', format='svg')
	plt.show()
	plt.clf() #clear figure
	
	fig = plot_sup_res_date( #automatic date formatter based on US trading calendar
		hist, #as per h for calc_support_resistance
		idx, #date index from pandas
		numbest = 2,
		fromwindows = True,
		pctbound = 0.1,
		extmethod = METHOD_NUMDIFF,
		method=METHOD_NSQUREDLOGN,
		window=125,
		errpct = 0.005,
		hough_scale=0.01,
		hough_prob_iter=10,
		sortError=False,
		accuracy=1)
	# other parameters as per plot_support_resistance
	
	plot_sup_res_learn( #draw learning figures, included for reference material only
		curdir, #base output directory for png and svg images, will be saved in 'data' subfolder
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
	directory = '.' # a 'data' folder will be created here if not existing to store images
	trendln.test_sup_res(directory) #simple tests that all methods are executing correct, assertion or other error indicates problem

Requirements
------------

* [Python](https://www.python.org) >= 2.7, 3.4+
* [numpy](http://www.numpy.org) >= 1.15
* [findiff](https://github.com/maroba/findiff) >= 0.7.0 (if using default numerical differentiation method)
* [scikit-image](https://scikit-image.org) >= 0.14.0 (if using image-based Hough line transform or its probabilistic variant)
* [pandas](https://github.com/pydata/pandas) >= 0.23.1 (if using date plotting function, or using naive minima/maxima methods)
* [matplotlib](https://matplotlib.org) >= 2.2.4 (if using any plotting function)


License
-------

**trendln** is distributed under the **MIT License**. See the [LICENSE](./LICENSE) file in the release for details.

Support
-------

Any questions, issues or ideas can kindly be submitted for review.

**Gregory Morse**
<gregory.morse@live.com>
