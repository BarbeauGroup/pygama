import pytest
import numpy as np
from numpy.testing import assert_
import matplotlib.pyplot as plt
import pickle as pl
import pygama.math.histogram as pgh
import pygama.math.peak_fitting as pf
from pygama.pargen import energy_cal


def test_peak_match():
    expected_peaks_kev = [ 1460, 2614.5 ]
    peaks_adu = [ 78.676315, 288.4798, 603.18506, 1337.4973, 2019.3586, 3225.7288, 3907.59, 5795.8213, 8470.816 ]
    pars, i_matches = energy_cal.poly_match(peaks_adu, expected_peaks_kev, deg=0, atol=10)
    print(i_matches)
    assert_(np.array_equal(i_matches, [5, 7]), f'bad i_matches {i_matches}')
