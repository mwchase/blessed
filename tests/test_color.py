# -*- coding: utf-8 -*-
"""Tests color algorithms."""

# std imports
import re

# 3rd party
import pytest

# local
from blessed.color import COLOR_DISTANCE_ALGORITHMS
from blessed.colorspace import RGBColor
from blessed.formatters import FormattingString, NullCallableString
# local
from .accessories import TestTerminal, as_subprocess


@pytest.fixture(params=COLOR_DISTANCE_ALGORITHMS.keys())
def all_algorithms(request):
    """All color distance algorithms."""
    return request.param


def test_same_color(all_algorithms):   # pylint: disable=redefined-outer-name
    """The same color should have 0 distance."""
    color = (0, 0, 0)
    assert COLOR_DISTANCE_ALGORITHMS[all_algorithms](color, color) == 0
    color = (255, 255, 255)
    assert COLOR_DISTANCE_ALGORITHMS[all_algorithms](color, color) == 0
    color = (55, 234, 102)
    assert COLOR_DISTANCE_ALGORITHMS[all_algorithms](color, color) == 0


def test_different_color(all_algorithms):   # pylint: disable=redefined-outer-name
    """Different colors should have positive distance."""
    color1 = (0, 0, 0)
    color2 = (0, 0, 1)
    assert COLOR_DISTANCE_ALGORITHMS[all_algorithms](color1, color2) > 0
    color1 = (25, 30, 4)
    color2 = (4, 30, 25)
    assert COLOR_DISTANCE_ALGORITHMS[all_algorithms](color1, color2) > 0
    color1 = (200, 200, 200)
    color2 = (100, 100, 101)
    assert COLOR_DISTANCE_ALGORITHMS[all_algorithms](color1, color2) > 0


def test_color_rgb():
    """Ensure expected sequence is returned"""
    @as_subprocess
    def child():
        t = TestTerminal(force_styling=True)
        color_patterns = r'%s|%s' % (t.caps['color'].pattern, t.caps['color256'].pattern)
        t.number_of_colors = 1 << 24
        assert t.color_rgb(0, 0, 0)('smoo') == u'\x1b[38;2;0;0;0msmoo' + t.normal
        assert t.color_rgb(84, 192, 233)('smoo') == u'\x1b[38;2;84;192;233msmoo' + t.normal

        t.number_of_colors = 256
        assert t.color_rgb(0, 0, 0)('smoo') == t.black + 'smoo' + t.normal
        assert re.match(color_patterns, t.color_rgb(84, 192, 233))

    child()


def test_on_color_rgb():
    """Ensure expected sequence is returned"""
    @as_subprocess
    def child():
        t = TestTerminal(force_styling=True)
        color_patterns = r'%s|%s' % (t.caps['color'].pattern, t.caps['on_color256'].pattern)
        t.number_of_colors = 1 << 24
        assert t.on_color_rgb(0, 0, 0)('smoo') == u'\x1b[48;2;0;0;0msmoo' + t.normal
        assert t.on_color_rgb(84, 192, 233)('smoo') == u'\x1b[48;2;84;192;233msmoo' + t.normal

        t.number_of_colors = 256
        assert t.on_color_rgb(0, 0, 0)('smoo') == t.on_black + 'smoo' + t.normal
        assert re.match(color_patterns, t.on_color_rgb(84, 192, 233))

    child()


def test_set_number_of_colors():
    """Ensure number of colors is supported and cache is cleared"""
    @as_subprocess
    def child():
        t = TestTerminal(force_styling=True)
        for num in (0, 4, 8, 16, 256, 1 << 24):
            t.aqua  # pylint: disable=pointless-statement
            assert 'aqua' in dir(t)
            t.number_of_colors = num
            assert t.number_of_colors == num
            assert 'aqua' not in dir(t)
        with pytest.raises(AssertionError):
            t.number_of_colors = 40

    child()


def test_set_color_distance_algorithm():
    """Ensure algorithm is supported and cache is cleared"""
    @as_subprocess
    def child():
        t = TestTerminal(force_styling=True)
        for algo in COLOR_DISTANCE_ALGORITHMS:
            t.aqua  # pylint: disable=pointless-statement
            assert 'aqua' in dir(t)
            t.color_distance_algorithm = algo
            assert t.color_distance_algorithm == algo
            assert 'aqua' not in dir(t)
        with pytest.raises(AssertionError):
            t.color_distance_algorithm = 'EenieMeenieMineyMo'

    child()


def test_RGBColor():
    """Ensure string is hex color representation"""
    color = RGBColor(0x5a, 0x05, 0xcb)
    assert str(color) == '#5a05cb'


def test_formatter():
    """Ensure return values match terminal attributes"""
    @as_subprocess
    def child():
        t = TestTerminal(force_styling=True)
        t.number_of_colors = 1 << 24
        bold_on_seagreen = t.formatter('bold_on_seagreen')
        assert isinstance(bold_on_seagreen, FormattingString)
        assert bold_on_seagreen == t.bold_on_seagreen

        t.number_of_colors = 0
        bold_on_seagreen = t.formatter('bold_on_seagreen')
        assert isinstance(bold_on_seagreen, FormattingString)
        assert bold_on_seagreen == t.bold_on_seagreen

        bold = t.formatter('bold')
        assert isinstance(bold, FormattingString)
        assert bold == t.bold

        t = TestTerminal()
        t._does_styling = False
        t.number_of_colors = 0
        bold_on_seagreen = t.formatter('bold_on_seagreen')
        assert isinstance(bold_on_seagreen, NullCallableString)
        assert bold_on_seagreen == t.bold_on_seagreen
    child()


def test_formatter_invalid():
    """Ensure NullCallableString for invalid formatters"""
    @as_subprocess
    def child():
        t = TestTerminal(force_styling=True)
        assert isinstance(t.formatter('csr'), NullCallableString)
    child()
