# trendln

Support and Resistance Trend lines Calculator for Financial Analysis
====================================================================

[![Python version](https://img.shields.io/badge/python-2.7,%203.4+-blue.svg?style=flat)](https://pypi.python.org/pypi/trendln)
[![PyPi version](https://img.shields.io/pypi/v/trendln.svg?maxAge=60)](https://pypi.python.org/pypi/trendln)
[![PyPi status](https://img.shields.io/pypi/status/trendln.svg?maxAge=60)](https://pypi.python.org/pypi/trendln)
[![PyPi downloads](https://img.shields.io/pypi/dm/trendln.svg?maxAge=2592000&label=installs&color=%2327B1FF)](https://pypi.python.org/pypi/trendln)

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

	calc_support_resistance()

Plotting Calculations
---------------------
The **plot_support_resistance** function will calculate and plot the average
and top 2 support and resistance lines, along with marking extrema used with
a maximum history length, and otherwise identical arguments to the
calculation function.

	plot_support_resistance()

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
