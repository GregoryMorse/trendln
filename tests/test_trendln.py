"""
Tests for trendln support/resistance calculation.

Covers every extmethod × method combination using deterministic synthetic data
so results are reproducible without network access (no yfinance required).
"""

import math

import numpy as np
import pandas as pd
import pytest

from trendln import (
    calc_support_resistance,
    get_extrema,
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

def _deep_equal(a, b):
    """Recursive equality that treats two NaNs as equal."""
    if isinstance(a, float) and isinstance(b, float):
        if math.isnan(a) and math.isnan(b):
            return True
        return a == b
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
        assert minimaIdxs == [6, 12, 18]
        assert maximaIdxs == [6, 12, 18]


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
