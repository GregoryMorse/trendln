Change Log
===========

0.1.12
-------
- `calc_support_resistance` and `get_extrema` now accept string names for their
  integer method constants (e.g. ``method='METHOD_NCUBED'`` in addition to
  ``method=METHOD_NCUBED``); invalid strings raise a clear ``ValueError``
  (closes #14)

0.1.11
-------
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
