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
    get_levels,
    pandas_to_ohlc,
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


# ---------------------------------------------------------------------------
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
