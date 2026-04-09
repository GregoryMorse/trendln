"""
Tests for trendln support/resistance calculation.

Covers every extmethod × method combination using deterministic synthetic data
so results are reproducible without network access (no yfinance required).
"""

import math

import numpy as np
import pandas as pd
import pytest

import warnings
warnings.filterwarnings("ignore", message="FinDiff is deprecated")

from trendln import (
    calc_support_resistance,
    get_extrema,
    get_horizontal_levels,
    get_levels,
    pandas_to_ohlc,
    plot_support_resistance,
    plot_sup_res_date,
    METHOD_NAIVE,
    METHOD_NAIVECONSEC,
    METHOD_NUMDIFF,
    METHOD_NCUBED,
    METHOD_NSQUREDLOGN,
    METHOD_HOUGHPOINTS,
    METHOD_HOUGHLINES,
    METHOD_PROBHOUGH,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _deep_equal(a, b, rel_tol=1e-9):
    """Recursive equality that treats two NaNs as equal and compares
    floats/numpy scalars approximately to tolerate minor FP differences."""
    import numbers
    # Unwrap numpy 0-d scalars to Python scalars for uniform handling
    if hasattr(a, 'item') and hasattr(a, 'ndim') and a.ndim == 0:
        a = a.item()
    if hasattr(b, 'item') and hasattr(b, 'ndim') and b.ndim == 0:
        b = b.item()
    # Numeric (float or int) comparison
    if isinstance(a, numbers.Number) and isinstance(b, numbers.Number):
        fa, fb = float(a), float(b)
        if math.isnan(fa) and math.isnan(fb):
            return True
        if math.isnan(fa) or math.isnan(fb):
            return False
        return math.isclose(fa, fb, rel_tol=rel_tol, abs_tol=1e-15)
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        return len(a) == len(b) and all(_deep_equal(x, y) for x, y in zip(a, b))
    return a == b


def assert_result(actual, expected):
    assert _deep_equal(actual, expected), f"\nActual:   {actual}\nExpected: {expected}"


# ---------------------------------------------------------------------------
# Shared test data
# ---------------------------------------------------------------------------

# Perfect zigzag: minima at 6, 12, 18 (value 0); maxima at 3, 9, 15, 21 (value 3)
DATA_SIMPLE = [float(x) for x in [0, 1, 2, 3, 2, 1, 0, 1, 2, 3, 2, 1, 0, 1, 2, 3, 2, 1, 0, 1, 2, 3, 2, 1, 0]]

RESULT_SIMPLE = (
    (
        [6, 12, 18],
        [0.0, 0.0],
        [([6, 12, 18], (0.0, 0.0, 0.0, 0.0, 0.0, 0.0))],
        [[([6, 12, 18], (0.0, 0.0, 0.0, 0.0, 0.0, 0.0))]],
    ),
    (
        [3, 9, 15, 21],
        [0.0, 3.0],
        [([3, 9, 15, 21], (0.0, 3.0, 0.0, 0.0, 0.0, 0.0))],
        [[([3, 9, 15, 21], (0.0, 3.0, 0.0, 0.0, 0.0, 0.0))]],
    ),
)

# Zigzag with consecutive equal values (tests NAIVECONSEC vs NAIVE behaviour)
DATA_CONSEC = [float(x) for x in [0, 1, 2, 3, 2, 1, 1, 1, 2, 4, 3, 2, 2, 2, 3, 5, 4, 3, 3, 3, 4, 6, 5, 4, 4]]

# Expected results for DATA_CONSEC vary by extmethod (see below).
_CONSEC_MAXIMA = (
    [3, 9, 15, 21],
    [0.16666666666666677, 2.499999999999998],
    [([3, 9, 15, 21], (0.16666666666666666, 2.5, 0.0, 0.0, 0.0, 0.0))],
    [[([3, 9, 15, 21], (0.16666666666666666, 2.5, 0.0, 0.0, 0.0, 0.0))]],
)

RESULT_CONSEC_NAIVE = (
    ([], [float("nan"), float("nan")], [], [[]]),
    _CONSEC_MAXIMA,
)

RESULT_CONSEC_NAIVECONSEC = (
    (
        [7, 13, 19],
        [0.1666666666666666, -0.1666666666666652],
        [([7, 13, 19], (0.16666666666666666, -0.16666666666666652, 0.0, 0.0, 0.0, 0.0))],
        [[([7, 13, 19], (0.16666666666666666, -0.16666666666666652, 0.0, 0.0, 0.0, 0.0))]],
    ),
    _CONSEC_MAXIMA,
)

RESULT_CONSEC_NUMDIFF = (
    ([23], [float("nan"), float("nan")], [], [[]]),
    _CONSEC_MAXIMA,
)


# ---------------------------------------------------------------------------
# calc_support_resistance – simple data, all extmethods + all trend methods
# ---------------------------------------------------------------------------

class TestSimpleDataAllMethods:
    def test_naive(self):
        assert_result(calc_support_resistance(DATA_SIMPLE, extmethod=METHOD_NAIVE), RESULT_SIMPLE)

    def test_naiveconsec(self):
        assert_result(calc_support_resistance(DATA_SIMPLE, extmethod=METHOD_NAIVECONSEC), RESULT_SIMPLE)

    def test_numdiff_default(self):
        assert_result(calc_support_resistance(DATA_SIMPLE), RESULT_SIMPLE)

    def test_method_ncubed(self):
        assert_result(calc_support_resistance(DATA_SIMPLE, method=METHOD_NCUBED), RESULT_SIMPLE)

    def test_method_nsquredlogn(self):
        assert_result(calc_support_resistance(DATA_SIMPLE, method=METHOD_NSQUREDLOGN), RESULT_SIMPLE)

    def test_method_houghpoints(self):
        assert_result(calc_support_resistance(DATA_SIMPLE, method=METHOD_HOUGHPOINTS), RESULT_SIMPLE)

    def test_method_houghlines(self):
        assert_result(calc_support_resistance(DATA_SIMPLE, method=METHOD_HOUGHLINES), RESULT_SIMPLE)

    def test_method_probhough(self):
        assert_result(calc_support_resistance(DATA_SIMPLE, method=METHOD_PROBHOUGH), RESULT_SIMPLE)


# ---------------------------------------------------------------------------
# calc_support_resistance – input type variants
# ---------------------------------------------------------------------------

class TestInputTypes:
    def test_list(self):
        assert_result(calc_support_resistance(DATA_SIMPLE), RESULT_SIMPLE)

    def test_numpy_array(self):
        assert_result(calc_support_resistance(np.array(DATA_SIMPLE)), RESULT_SIMPLE)

    def test_pandas_series(self):
        assert_result(calc_support_resistance(pd.Series(DATA_SIMPLE)), RESULT_SIMPLE)

    def test_tuple_both(self):
        mins, maxs = calc_support_resistance((DATA_SIMPLE, DATA_SIMPLE))
        # With identical low/high data the minima and maxima come from the same series
        assert isinstance(mins, tuple) and len(mins) == 4
        assert isinstance(maxs, tuple) and len(maxs) == 4

    def test_tuple_support_only(self):
        result = calc_support_resistance((DATA_SIMPLE, None))
        # Only a single 4-tuple returned when one side is None
        assert isinstance(result, tuple) and len(result) == 4

    def test_tuple_resistance_only(self):
        result = calc_support_resistance((None, DATA_SIMPLE))
        assert isinstance(result, tuple) and len(result) == 4


# ---------------------------------------------------------------------------
# calc_support_resistance – consecutive-equal data (extmethod differences)
# ---------------------------------------------------------------------------

class TestConsecData:
    def test_naive(self):
        assert_result(
            calc_support_resistance(DATA_CONSEC, extmethod=METHOD_NAIVE),
            RESULT_CONSEC_NAIVE,
        )

    def test_naiveconsec(self):
        assert_result(
            calc_support_resistance(DATA_CONSEC, extmethod=METHOD_NAIVECONSEC),
            RESULT_CONSEC_NAIVECONSEC,
        )

    def test_numdiff(self):
        assert_result(
            calc_support_resistance(DATA_CONSEC),
            RESULT_CONSEC_NUMDIFF,
        )

    def test_numdiff_ncubed(self):
        assert_result(
            calc_support_resistance(DATA_CONSEC, method=METHOD_NCUBED),
            RESULT_CONSEC_NUMDIFF,
        )

    def test_numdiff_houghpoints(self):
        assert_result(
            calc_support_resistance(DATA_CONSEC, method=METHOD_HOUGHPOINTS),
            RESULT_CONSEC_NUMDIFF,
        )

    def test_numdiff_houghlines(self):
        assert_result(
            calc_support_resistance(DATA_CONSEC, method=METHOD_HOUGHLINES),
            RESULT_CONSEC_NUMDIFF,
        )

    def test_numdiff_probhough(self):
        assert_result(
            calc_support_resistance(DATA_CONSEC, method=METHOD_PROBHOUGH),
            RESULT_CONSEC_NUMDIFF,
        )


# ---------------------------------------------------------------------------
# get_extrema
# ---------------------------------------------------------------------------

class TestGetExtrema:
    def test_both_series(self):
        minimaIdxs, maximaIdxs = get_extrema(DATA_SIMPLE)
        assert minimaIdxs == [6, 12, 18]
        assert maximaIdxs == [3, 9, 15, 21]

    def test_maxima_only_tuple(self):
        result = get_extrema((None, DATA_SIMPLE))
        assert result == [3, 9, 15, 21]

    def test_minima_only_tuple(self):
        result = get_extrema((DATA_SIMPLE, None))
        assert result == [6, 12, 18]

    def test_separate_low_high(self):
        minimaIdxs, maximaIdxs = get_extrema((DATA_SIMPLE, DATA_SIMPLE))
        # First tuple element = support series (finds minima); second = resistance series (finds maxima)
        assert minimaIdxs == [6, 12, 18]
        assert maximaIdxs == [3, 9, 15, 21]


# ---------------------------------------------------------------------------
# include_edge — edge pivot detection (issue #19)
# ---------------------------------------------------------------------------

class TestIncludeEdge:
    """Tests for include_edge parameter on get_extrema and calc_support_resistance."""

    # DATA_SIMPLE starts at 0 (index 0 is a minimum) and ends at 0 (index 24
    # is a minimum).  With include_edge=False (default) neither endpoint is
    # returned; with include_edge=True both should be detected.

    def test_default_exclude_endpoints(self):
        minimaIdxs, _ = get_extrema(DATA_SIMPLE)
        assert 0 not in minimaIdxs
        assert 24 not in minimaIdxs

    def test_include_edge_first_minimum(self):
        # DATA_SIMPLE[0]=0.0 < DATA_SIMPLE[1]=1.0 → qualifies as minimum
        minimaIdxs, _ = get_extrema(DATA_SIMPLE, include_edge=True)
        assert 0 in minimaIdxs

    def test_include_edge_last_minimum(self):
        # DATA_SIMPLE[24]=0.0 < DATA_SIMPLE[23]=1.0 → qualifies as minimum
        minimaIdxs, _ = get_extrema(DATA_SIMPLE, include_edge=True)
        assert 24 in minimaIdxs

    def test_include_edge_no_false_positive_maximum_at_minimum_endpoint(self):
        # index 0 is a minimum, NOT a maximum
        _, maximaIdxs = get_extrema(DATA_SIMPLE, include_edge=True)
        assert 0 not in maximaIdxs

    def test_include_edge_maximum_endpoint(self):
        # Build a series that ends on a high: [0,1,2,3,2,1,0,...,3] - last value is high
        data = DATA_SIMPLE[:-1] + [3.0]   # override last value to 3.0 > 1.0 (second-to-last)
        _, maximaIdxs = get_extrema(data, include_edge=True)
        assert (len(data) - 1) in maximaIdxs

    def test_include_edge_works_all_extmethods(self):
        for em in (METHOD_NAIVE, METHOD_NAIVECONSEC, METHOD_NUMDIFF):
            minimaIdxs, _ = get_extrema(DATA_SIMPLE, extmethod=em, include_edge=True)
            assert 0 in minimaIdxs
            assert 24 in minimaIdxs

    def test_include_edge_via_calc_support_resistance(self):
        result = calc_support_resistance(DATA_SIMPLE, extmethod=METHOD_NAIVE,
                                         include_edge=True)
        minimaIdxs = result[0][0]
        assert 0 in minimaIdxs
        assert 24 in minimaIdxs

    def test_include_edge_invalid_type_raises(self):
        with pytest.raises(ValueError, match='include_edge'):
            get_extrema(DATA_SIMPLE, include_edge=1)

    def test_include_edge_does_not_duplicate_existing_extrema(self):
        # If a boundary point is already in the list, it should not appear twice
        minimaIdxs, _ = get_extrema(DATA_SIMPLE, include_edge=True)
        assert minimaIdxs.count(0) == 1
        assert minimaIdxs.count(24) == 1


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# plot_support_resistance options
# ---------------------------------------------------------------------------

import os
os.environ.setdefault('MPLBACKEND', 'Agg')

class TestPlotOptions:
    """Tests for plot_support_resistance keyword parameters."""

    def test_show_average_true_returns_figure(self):
        import matplotlib
        fig = plot_support_resistance(DATA_SIMPLE, show_average=True)
        assert isinstance(fig, matplotlib.figure.Figure)

    def test_show_average_false_returns_figure(self):
        import matplotlib
        fig = plot_support_resistance(DATA_SIMPLE, show_average=False)
        assert isinstance(fig, matplotlib.figure.Figure)

    def test_show_average_false_fewer_lines(self):
        """With show_average=False the average lines (Avg. Support/Resistance)
        should not appear as legend entries."""
        import matplotlib
        import matplotlib.pyplot as plt
        plt.figure()
        fig_with = plot_support_resistance(DATA_SIMPLE, show_average=True)
        labels_with = [t.get_text() for t in fig_with.axes[0].get_legend().get_texts()]
        plt.figure()
        fig_without = plot_support_resistance(DATA_SIMPLE, show_average=False)
        labels_without = [t.get_text() for t in fig_without.axes[0].get_legend().get_texts()]
        plt.close('all')
        assert any('Avg.' in l for l in labels_with)
        assert not any('Avg.' in l for l in labels_without)

    def test_ax_param_draws_into_provided_axes(self):
        """When ax is supplied the plot is drawn into that axes object."""
        import matplotlib.pyplot as plt
        fig, (ax1, ax2) = plt.subplots(1, 2)
        returned_fig = plot_support_resistance(DATA_SIMPLE, ax=ax2)
        # The returned figure must be the same object that was passed
        assert returned_fig is fig
        # ax2 must have content (lines drawn on it)
        assert len(ax2.lines) > 0
        # ax1 must be empty (nothing was drawn on it)
        assert len(ax1.lines) == 0
        plt.close('all')

    def test_ax_param_none_creates_new_figure(self):
        """Default (ax=None) still creates and returns a new Figure."""
        import matplotlib
        import matplotlib.pyplot as plt
        plt.close('all')
        fig = plot_support_resistance(DATA_SIMPLE)
        assert isinstance(fig, matplotlib.figure.Figure)
        plt.close('all')

    def test_ax_param_plot_sup_res_date_passthrough(self):
        """plot_sup_res_date forwards ax to plot_support_resistance."""
        import pandas as pd
        import matplotlib.pyplot as plt
        idx = pd.date_range('2020-01-01', periods=len(DATA_SIMPLE), freq='D')
        fig, ax = plt.subplots()
        returned_fig = plot_sup_res_date(DATA_SIMPLE, idx, ax=ax)
        assert returned_fig is fig
        assert len(ax.lines) > 0
        plt.close('all')

    def test_extend_to_end_returns_figure(self):
        """extend_to_end=True still returns a Figure without error."""
        import matplotlib
        import matplotlib.pyplot as plt
        fig = plot_support_resistance(DATA_SIMPLE, extmethod=METHOD_NAIVE,
                                      extend_to_end=True)
        assert isinstance(fig, matplotlib.figure.Figure)
        plt.close('all')

    def test_extend_to_end_lines_reach_last_bar(self):
        """With extend_to_end=True trend lines should extend to len_h (one
        past the last data index), i.e. the chart edge."""
        import matplotlib.pyplot as plt
        fig = plot_support_resistance(DATA_SIMPLE, extmethod=METHOD_NAIVE,
                                      numbest=2, extend_to_end=True)
        ax = fig.axes[0]
        len_h = len(DATA_SIMPLE)
        # Trend lines are labeled 'Support' or 'Resistance' (the first of each
        # group); average lines are labeled 'Avg. Support' / 'Avg. Resistance'
        trend_labels = {'Support', 'Resistance'}
        trendlines = [ln for ln in ax.lines
                      if ln.get_label() in trend_labels]
        assert len(trendlines) > 0
        for ln in trendlines:
            assert ln.get_xdata()[-1] == len_h
        plt.close('all')

    def test_extend_to_end_false_may_stop_early(self):
        """With extend_to_end=False (default) lines are allowed to stop before
        the last bar. This test just confirms no error and a figure is returned."""
        import matplotlib
        import matplotlib.pyplot as plt
        fig = plot_support_resistance(DATA_SIMPLE, extmethod=METHOD_NAIVE,
                                      extend_to_end=False)
        assert isinstance(fig, matplotlib.figure.Figure)
        plt.close('all')

    def test_extend_to_end_date_passthrough(self):
        """plot_sup_res_date forwards extend_to_end to plot_support_resistance."""
        import matplotlib
        import pandas as pd
        import matplotlib.pyplot as plt
        idx = pd.date_range('2020-01-01', periods=len(DATA_SIMPLE), freq='D')
        fig = plot_sup_res_date(DATA_SIMPLE, idx, extmethod=METHOD_NAIVE,
                                extend_to_end=True)
        assert isinstance(fig, matplotlib.figure.Figure)
        plt.close('all')


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------

class TestValidation:
    def test_invalid_h_type(self):
        with pytest.raises(ValueError):
            calc_support_resistance("not an array")

    def test_window_must_be_int(self):
        with pytest.raises(ValueError):
            calc_support_resistance(DATA_SIMPLE, window=125.0)

    def test_errpct_must_be_float(self):
        with pytest.raises(ValueError):
            calc_support_resistance(DATA_SIMPLE, errpct=1)

    def test_hough_scale_must_be_float(self):
        with pytest.raises(ValueError):
            calc_support_resistance(DATA_SIMPLE, hough_scale=1)

    def test_hough_prob_iter_must_be_int(self):
        with pytest.raises(ValueError):
            calc_support_resistance(DATA_SIMPLE, hough_prob_iter=10.0)

    def test_mismatched_tuple_lengths(self):
        with pytest.raises(ValueError):
            calc_support_resistance((DATA_SIMPLE, DATA_SIMPLE[:-1]))

    def test_tuple_both_none_raises(self):
        with pytest.raises(ValueError):
            calc_support_resistance((None, None))

    def test_accuracy_must_be_int(self):
        with pytest.raises(ValueError, match='accuracy'):
            calc_support_resistance(DATA_SIMPLE, accuracy=2.0)

    def test_accuracy_must_be_positive(self):
        with pytest.raises(ValueError, match='accuracy'):
            calc_support_resistance(DATA_SIMPLE, accuracy=0)

    def test_accuracy_must_be_even(self):
        with pytest.raises(ValueError, match='accuracy'):
            calc_support_resistance(DATA_SIMPLE, accuracy=1)

    def test_accuracy_odd_raises_on_get_extrema(self):
        with pytest.raises(ValueError, match='accuracy'):
            get_extrema(DATA_SIMPLE, accuracy=3)

    def test_accuracy_even_values_accepted(self):
        # 2, 4, 6, 8 should all be accepted without error
        for acc in (2, 4, 6, 8):
            calc_support_resistance(DATA_SIMPLE, accuracy=acc)

    def test_include_edge_must_be_bool_calc(self):
        with pytest.raises(ValueError, match='include_edge'):
            calc_support_resistance(DATA_SIMPLE, include_edge=1)


# ---------------------------------------------------------------------------
# String aliases for method / extmethod constants (issue #14)
# ---------------------------------------------------------------------------

class TestStringMethodAliases:
    """calc_support_resistance and get_extrema accept string names for their
    integer method constants, e.g. 'METHOD_NCUBED' as well as METHOD_NCUBED."""

    # --- method parameter ---

    def test_method_string_ncubed(self):
        assert_result(
            calc_support_resistance(DATA_SIMPLE, method='METHOD_NCUBED'),
            calc_support_resistance(DATA_SIMPLE, method=METHOD_NCUBED),
        )

    def test_method_string_nsquredlogn(self):
        assert_result(
            calc_support_resistance(DATA_SIMPLE, method='METHOD_NSQUREDLOGN'),
            calc_support_resistance(DATA_SIMPLE, method=METHOD_NSQUREDLOGN),
        )

    def test_method_string_houghpoints(self):
        assert_result(
            calc_support_resistance(DATA_SIMPLE, method='METHOD_HOUGHPOINTS'),
            calc_support_resistance(DATA_SIMPLE, method=METHOD_HOUGHPOINTS),
        )

    def test_method_string_houghlines(self):
        assert_result(
            calc_support_resistance(DATA_SIMPLE, method='METHOD_HOUGHLINES'),
            calc_support_resistance(DATA_SIMPLE, method=METHOD_HOUGHLINES),
        )

    def test_method_string_probhough(self):
        assert_result(
            calc_support_resistance(DATA_SIMPLE, method='METHOD_PROBHOUGH'),
            calc_support_resistance(DATA_SIMPLE, method=METHOD_PROBHOUGH),
        )

    # --- extmethod parameter ---

    def test_extmethod_string_naive(self):
        assert_result(
            calc_support_resistance(DATA_SIMPLE, extmethod='METHOD_NAIVE'),
            calc_support_resistance(DATA_SIMPLE, extmethod=METHOD_NAIVE),
        )

    def test_extmethod_string_naiveconsec(self):
        assert_result(
            calc_support_resistance(DATA_SIMPLE, extmethod='METHOD_NAIVECONSEC'),
            calc_support_resistance(DATA_SIMPLE, extmethod=METHOD_NAIVECONSEC),
        )

    def test_extmethod_string_numdiff(self):
        assert_result(
            calc_support_resistance(DATA_SIMPLE, extmethod='METHOD_NUMDIFF'),
            calc_support_resistance(DATA_SIMPLE, extmethod=METHOD_NUMDIFF),
        )

    def test_get_extrema_string_extmethod(self):
        assert get_extrema(DATA_SIMPLE, extmethod='METHOD_NAIVE') == \
               get_extrema(DATA_SIMPLE, extmethod=METHOD_NAIVE)

    # --- invalid string raises clearly ---

    def test_invalid_method_string_raises(self):
        with pytest.raises(ValueError, match='METHOD_BOGUS'):
            calc_support_resistance(DATA_SIMPLE, method='METHOD_BOGUS')

    def test_invalid_extmethod_string_raises(self):
        with pytest.raises(ValueError, match='METHOD_BOGUS'):
            get_extrema(DATA_SIMPLE, extmethod='METHOD_BOGUS')
# pandas_to_ohlc
# ---------------------------------------------------------------------------

class TestPandasToOhlc:
    """Tests for trendln.pandas_to_ohlc()."""

    def _df(self, columns, values=None):
        """Build a minimal DataFrame with given column names."""
        n = 10
        if values is None:
            values = {c: [float(i) for i in range(n)] for c in columns}
        return pd.DataFrame(values)

    # --- auto-detection: standard casing ---

    def test_standard_columns_returns_tuple(self):
        df = self._df(['Low', 'High', 'Close'])
        result = pandas_to_ohlc(df)
        assert isinstance(result, tuple) and len(result) == 2
        assert list(result[0]) == list(df['Low'])
        assert list(result[1]) == list(df['High'])

    def test_lowercase_columns_auto_detected(self):
        df = self._df(['low', 'high', 'close'])
        result = pandas_to_ohlc(df)
        assert isinstance(result, tuple) and len(result) == 2

    def test_mixed_case_columns_auto_detected(self):
        df = self._df(['LOW', 'HIGH', 'CLOSE'])
        result = pandas_to_ohlc(df)
        assert isinstance(result, tuple) and len(result) == 2

    # --- fallback to close only ---

    def test_close_only_returns_series(self):
        df = self._df(['Open', 'Close'])
        result = pandas_to_ohlc(df)
        assert isinstance(result, pd.Series)
        assert list(result) == list(df['Close'])

    def test_explicit_close_col(self):
        df = self._df(['Date', 'Price'], values={'Date': list(range(10)), 'Price': [float(i) for i in range(10)]})
        result = pandas_to_ohlc(df, close_col='Price')
        assert isinstance(result, pd.Series)
        assert list(result) == list(df['Price'])

    # --- explicit column names ---

    def test_explicit_low_high_cols(self):
        df = self._df(['lo', 'hi', 'cl'], values={'lo': [1.0]*10, 'hi': [2.0]*10, 'cl': [1.5]*10})
        result = pandas_to_ohlc(df, low_col='lo', high_col='hi')
        assert isinstance(result, tuple) and len(result) == 2
        assert list(result[0]) == [1.0] * 10
        assert list(result[1]) == [2.0] * 10

    def test_explicit_low_only_returns_series(self):
        df = self._df(['lo', 'cl'], values={'lo': [1.0]*10, 'cl': [1.5]*10})
        result = pandas_to_ohlc(df, low_col='lo')
        assert isinstance(result, pd.Series)
        assert list(result) == [1.0] * 10

    def test_explicit_high_only_returns_series(self):
        df = self._df(['hi', 'cl'], values={'hi': [2.0]*10, 'cl': [1.5]*10})
        result = pandas_to_ohlc(df, high_col='hi')
        assert isinstance(result, pd.Series)
        assert list(result) == [2.0] * 10

    # --- result is valid input to calc_support_resistance ---

    def test_output_feeds_calc_support_resistance(self):
        low = [float(x) for x in [0, 1, 2, 3, 2, 1, 0, 1, 2, 3, 2, 1, 0, 1, 2, 3, 2, 1, 0, 1, 2, 3, 2, 1, 0]]
        high = [v + 3.0 for v in low]
        df = pd.DataFrame({'Low': low, 'High': high, 'Close': [(l + h) / 2 for l, h in zip(low, high)]})
        ohlc = pandas_to_ohlc(df)
        result = calc_support_resistance(ohlc)
        assert isinstance(result, tuple) and len(result) == 2

    # --- error cases ---

    def test_non_dataframe_raises(self):
        with pytest.raises(ValueError, match='DataFrame'):
            pandas_to_ohlc([1, 2, 3])

    def test_unknown_explicit_col_raises(self):
        df = self._df(['Low', 'High'])
        with pytest.raises(ValueError, match="'BadCol'"):
            pandas_to_ohlc(df, low_col='BadCol')

    def test_no_price_columns_raises(self):
        df = self._df(['Open', 'Volume'], values={'Open': [1.0]*10, 'Volume': [100]*10})
        with pytest.raises(ValueError, match='No suitable price column'):
            pandas_to_ohlc(df)


# ---------------------------------------------------------------------------
# get_levels
# ---------------------------------------------------------------------------

# DATA_SIMPLE: flat support at 0.0 (3 pivot points), flat resistance at 3.0
# (4 pivot points).  Trend lines are exact so evaluated level == intercept
# regardless of x.

class TestGetLevels:
    """Tests for trendln.get_levels()."""

    def _result(self, price=1.5, x=20, n=3):
        calc = calc_support_resistance(DATA_SIMPLE, extmethod=METHOD_NAIVE)
        return get_levels(calc, x, price, n)

    # --- basic classification and ordering ---

    def test_support_below_price(self):
        supports, resistances, _ = self._result(price=1.5)
        assert len(supports) == 1
        inf_lvl, strength, slope, intercept = supports[0]
        assert math.isclose(inf_lvl, 0.0)
        assert strength == 3
        assert math.isclose(slope, 0.0)
        assert math.isclose(intercept, 0.0)

    def test_resistance_above_price(self):
        _, resistances, _ = self._result(price=1.5)
        assert len(resistances) == 1
        r_lvl, strength, slope, intercept = resistances[0]
        assert math.isclose(r_lvl, 3.0)
        assert strength == 4
        assert math.isclose(slope, 0.0)
        assert math.isclose(intercept, 3.0)

    # --- risk-to-reward ratio ---

    def test_rr_ratio_basic(self):
        # price=1.5, support=0.0, resistance=3.0 -> RR=(3.0-1.5)/(1.5-0.0)=1.0
        _, _, rr = self._result(price=1.5)
        assert len(rr) == 1
        assert math.isclose(rr[0], 1.0)

    def test_rr_ratio_asymmetric(self):
        # price=0.5, support=0.0, resistance=3.0 -> RR=2.5/0.5=5.0
        _, _, rr = self._result(price=0.5)
        assert len(rr) == 1
        assert math.isclose(rr[0], 5.0)

    # --- edge cases ---

    def test_no_support_gives_none_rr(self):
        # price below all trend lines -> no supports, both levels are resistance
        supports, resistances, rr = self._result(price=-1.0)
        assert len(supports) == 0
        # both 0.0 and 3.0 are above -1.0 -> resistance
        assert len(resistances) == 2
        assert all(r is None for r in rr)

    def test_price_at_support_gives_inf_rr(self):
        # support level exactly equals price -> risk == 0 -> inf
        _, _, rr = self._result(price=0.0)
        assert len(rr) == 1
        assert rr[0] == float('inf')

    def test_price_at_resistance_no_resistance(self):
        # 3.0 is not strictly > price so listed as support, nothing above
        supports, resistances, rr = self._result(price=3.0)
        assert len(resistances) == 0
        assert rr == []
        # both lines (0.0 and 3.0) are <= 3.0 -> both supports
        assert len(supports) == 2

    def test_n_limits_results(self):
        # Only one support and one resistance exist in DATA_SIMPLE, so n doesn't clip further,
        # but verifying the parameter is honoured when n=0.
        supports, resistances, rr = self._result(price=1.5, n=0)
        assert supports == []
        assert resistances == []
        assert rr == []

    def test_supports_sorted_nearest_first(self):
        # Create data with multiple support levels so ordering can be checked.
        # Use a data set where both mintrend and maxtrend produce levels below price.
        calc = calc_support_resistance(DATA_SIMPLE, extmethod=METHOD_NAIVE)
        supports, _, _ = get_levels(calc, 20, 4.0)  # price above all lines (0.0 & 3.0)
        levels = [s[0] for s in supports]
        # Nearest to 4.0 first: 3.0 then 0.0
        assert math.isclose(levels[0], 3.0)
        assert math.isclose(levels[1], 0.0)

    def test_resistances_sorted_nearest_first(self):
        calc = calc_support_resistance(DATA_SIMPLE, extmethod=METHOD_NAIVE)
        _, resistances, _ = get_levels(calc, 20, -1.0)  # price below all lines
        levels = [r[0] for r in resistances]
        # Nearest to -1.0 first: 0.0 then 3.0
        assert math.isclose(levels[0], 0.0)
        assert math.isclose(levels[1], 3.0)

    # --- invalid input ---

    def test_invalid_calc_result_raises(self):
        with pytest.raises(ValueError):
            get_levels(None, 10, 1.5)

    def test_invalid_calc_result_single_side_raises(self):
        # Single-side result (4-tuple) is not accepted
        single = calc_support_resistance((DATA_SIMPLE, None))
        with pytest.raises(ValueError):
            get_levels(single, 10, 1.5)


# ---------------------------------------------------------------------------
# get_horizontal_levels — horizontal clustering (issue #13)
# ---------------------------------------------------------------------------

import math as _math

class TestGetHorizontalLevels:
    """Tests for trendln.get_horizontal_levels()."""

    # DATA_SIMPLE = [0,1,2,3,2,1,0,1,2,3,...,0] (25 pts)
    # Minima are all 0.0 -> a single tight support cluster.
    # Maxima are all 3.0 -> a single tight resistance cluster.

    def test_returns_two_lists(self):
        sup, res = get_horizontal_levels(DATA_SIMPLE, extmethod=METHOD_NAIVE)
        assert isinstance(sup, list)
        assert isinstance(res, list)

    def test_entry_format(self):
        sup, res = get_horizontal_levels(DATA_SIMPLE, extmethod=METHOD_NAIVE)
        assert len(sup) > 0
        mean_price, touch_count, pivot_idxs = sup[0]
        assert isinstance(mean_price, float)
        assert isinstance(touch_count, int)
        assert isinstance(pivot_idxs, list)

    def test_support_cluster_at_zero(self):
        # All minima of DATA_SIMPLE are 0.0 -> should form one cluster
        sup, _ = get_horizontal_levels(DATA_SIMPLE, extmethod=METHOD_NAIVE,
                                        min_touches=2)
        assert len(sup) == 1
        mean_price, touch_count, _ = sup[0]
        assert _math.isclose(mean_price, 0.0, abs_tol=1e-9)
        assert touch_count >= 2

    def test_resistance_cluster_at_three(self):
        # All maxima of DATA_SIMPLE are 3.0 -> should form one cluster
        _, res = get_horizontal_levels(DATA_SIMPLE, extmethod=METHOD_NAIVE,
                                        min_touches=2)
        assert len(res) == 1
        mean_price, touch_count, _ = res[0]
        assert _math.isclose(mean_price, 3.0, abs_tol=1e-9)
        assert touch_count >= 2

    def test_min_touches_one_returns_every_pivot(self):
        sup, res = get_horizontal_levels(DATA_SIMPLE, extmethod=METHOD_NAIVE,
                                          min_touches=1)
        # At min_touches=1 every single pivot is a level
        total_pivots = sum(c[1] for c in sup) + sum(c[1] for c in res)
        assert total_pivots > 0

    def test_high_min_touches_filters_out_clusters(self):
        # DATA_SIMPLE has exactly 3 minima (all 0.0). Require 4 -> no support levels.
        sup, _ = get_horizontal_levels(DATA_SIMPLE, extmethod=METHOD_NAIVE,
                                        min_touches=10)
        assert sup == []

    def test_support_sorted_descending(self):
        # With multiple clusters, support levels should be descending by price
        data = [float(x) for x in [0,1,0,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2]]
        sup, _ = get_horizontal_levels(data, extmethod=METHOD_NAIVE,
                                        min_touches=1, pctbound=0.01)
        prices = [s[0] for s in sup]
        assert prices == sorted(prices, reverse=True)

    def test_resistance_sorted_ascending(self):
        _, res = get_horizontal_levels(DATA_SIMPLE, extmethod=METHOD_NAIVE,
                                        min_touches=1)
        prices = [r[0] for r in res]
        assert prices == sorted(prices)

    def test_pivot_indices_in_range(self):
        sup, res = get_horizontal_levels(DATA_SIMPLE, extmethod=METHOD_NAIVE,
                                          min_touches=1)
        n = len(DATA_SIMPLE)
        for _, _, idxs in sup + res:
            for i in idxs:
                assert 0 <= i < n

    def test_tuple_input_low_high(self):
        # (low, high) tuple: low->support, high->resistance
        sup, res = get_horizontal_levels((DATA_SIMPLE, DATA_SIMPLE),
                                          extmethod=METHOD_NAIVE, min_touches=1)
        assert len(sup) > 0
        assert len(res) > 0

    def test_invalid_pctbound_raises(self):
        with pytest.raises(ValueError, match='pctbound'):
            get_horizontal_levels(DATA_SIMPLE, pctbound=0)

    def test_invalid_pctbound_type_raises(self):
        with pytest.raises(ValueError, match='pctbound'):
            get_horizontal_levels(DATA_SIMPLE, pctbound=5)

    def test_invalid_min_touches_raises(self):
        with pytest.raises(ValueError, match='min_touches'):
            get_horizontal_levels(DATA_SIMPLE, min_touches=0)
