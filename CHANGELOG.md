Change Log
===========

0.1.18
-------
- Added ``ohlc`` parameter (default ``None``) to ``plot_support_resistance`` and
  ``plot_sup_res_date``; accepts a ``(opens, highs, lows, closes)`` 4-tuple of
  numeric sequences and renders the price series as OHLC candlestick bars using
  matplotlib Rectangle patches (green = bullish, red = bearish) while all
  trendline overlays continue to work unchanged; ``hist`` still controls extrema
  detection so the existing API is fully preserved (closes #29)

0.1.17
-------
- Added ``get_horizontal_levels(h, pctbound=0.05, extmethod=..., accuracy=2,
  min_touches=2)`` function; detects flat support and resistance zones by
  clustering pivot prices within a relative tolerance, returning
  ``(support_levels, resistance_levels)`` where each entry is
  ``(mean_price, touch_count, pivot_indices)``; accepts the same
  ``h`` formats as :func:`calc_support_resistance` (closes #13)

0.1.16
-------
- Added ``extend_to_end`` parameter (default ``False``) to
  ``plot_support_resistance`` and ``plot_sup_res_date``; when ``True``, trend
  lines are drawn all the way to the last bar rather than stopping at the first
  price-crossing or out-of-range breakout, matching the community workaround
  described in #17 (closes #17)

0.1.15
-------
- Added ``ax`` parameter (default ``None``) to ``plot_support_resistance`` and
  ``plot_sup_res_date``; when an existing ``matplotlib.axes.Axes`` object is
  supplied the plot is drawn into that axes, enabling embedding in subplots;
  when ``None`` the previous behaviour (create a new figure) is preserved
  (closes #26)

0.1.14
-------
- Added ``include_edge`` parameter (default ``False``) to ``get_extrema`` and
  ``calc_support_resistance``; when ``True``, the first and last data points are
  eligible to be detected as local extrema via one-sided comparison with their
  sole neighbour, eliminating the one-bar lag at series boundaries (closes #19)

0.1.13
-------
- Added ``show_average`` parameter (default ``True``) to
  ``plot_support_resistance`` and ``plot_sup_res_date``; set to ``False`` to
  hide the average support/resistance lines from the plot (closes #16)
- Added upfront validation of the ``accuracy`` parameter in
  ``calc_support_resistance`` and ``get_extrema``: raises a clear
  ``ValueError('accuracy must be a positive even integer')`` instead of a
  cryptic findiff traceback when an odd or non-integer value is supplied;
  the default remains ``accuracy=2`` (closes #25)

0.1.12
-------
- `calc_support_resistance` and `get_extrema` now accept string names for their
  integer method constants (e.g. ``method='METHOD_NCUBED'`` in addition to
  ``method=METHOD_NCUBED``); invalid strings raise a clear ``ValueError``
  (closes #14)
- Added `pandas_to_ohlc(df, low_col=None, high_col=None, close_col=None)` helper
  that converts any OHLC pandas DataFrame (yfinance, ccxt, or custom) into the
  ``(low_series, high_series)`` tuple expected by trendln functions;
  auto-detects standard column names case-insensitively (closes #15)

0.1.11
-------
- Added `get_levels(calc_result, x, price, n=3)` function: given a pre-computed
  `calc_support_resistance` result, evaluates all trend lines at a given series
  index to return the nearest support levels, nearest resistance levels (each as
  `(level, strength, slope, intercept)` sorted by proximity) and the
  risk-to-reward ratios of each resistance level versus the nearest support
  (closes #11)
- Added `title`, `y_axis_label`, and `series_label` parameters to `plot_support_resistance` and `plot_sup_res_date` for customizable plot titles, y-axis labels, and series legend labels (thanks xeonvs)

0.1.8
-------
- Initial release

0.1.10
-------
- Fixed error in ybar for linear regression equation
- Added parameter error checking to avoid crashing with not easily understood messages (thanks ravi2007147)
- Added ability to pass tuple with Low and/or High values for separate minima and/or maxima trend lines
- Added library function for getting local minima/maxima as a separate operation
- Fixed bug in plotting when empty range occurred (thanks 5xcor)
- Refactored the pandas minima/maxima code for performance
- Refactored several other places to eliminate duplicate code and improve performance
- Added accuracy parameter for numerical differentiation method
- Test coverage for important part of the new functionality
