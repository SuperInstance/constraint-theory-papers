#!/usr/bin/env python3
"""Tests for telephone-game.py pure functions: score_facts, count_novel_claims."""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import importlib.util
spec = importlib.util.spec_from_file_location("telephone_game", os.path.join(os.path.dirname(__file__), "telephone-game.py"))
telephone_game = importlib.util.module_from_spec(spec)
spec.loader.exec_module(telephone_game)

score_facts = telephone_game.score_facts
count_novel_claims = telephone_game.count_novel_claims
KEY_FACTS = telephone_game.KEY_FACTS
ORIGINAL = telephone_game.ORIGINAL


class TestScoreFacts:
    def test_returns_dict(self):
        result = score_facts("some text")
        assert isinstance(result, dict)

    def test_exact_match(self):
        text = "The MV Epsilon sailed on March 14, 2024."
        result = score_facts(text)
        assert "ship_name" in result
        assert result["ship_name"] == "EXACT"
        assert "date" in result
        assert result["date"] == "EXACT"

    def test_partial_match(self):
        text = "The ship Epsilon traveled in March 2024."
        result = score_facts(text)
        # "Epsilon" should partially match "MV Epsilon"
        if "ship_name" in result:
            assert result["ship_name"] in ("EXACT", "PARTIAL")

    def test_no_match(self):
        text = "Once upon a time there was a boat."
        result = score_facts(text)
        assert len(result) == 0 or all(v not in ("EXACT", "PARTIAL") for v in result.values())

    def test_all_facts_in_original(self):
        """The original text should contain most key facts."""
        result = score_facts(ORIGINAL)
        assert len(result) >= 10  # Should find most facts

    def test_case_insensitive(self):
        text = "the mv epsilon traveled to são paulo"
        result = score_facts(text)
        assert "ship_name" in result
        assert "destination" in result

    def test_multiple_facts(self):
        text = """
        The MV Epsilon carried 4,200 containers to São Paulo.
        The strait was 1.2 nautical miles wide.
        The turn was 47 degrees over 12 minutes.
        Speed was 14 knots with ±0.3 degrees tolerance.
        """
        result = score_facts(text)
        assert len(result) >= 5


class TestCountNovelClaims:
    def test_returns_int(self):
        result = count_novel_claims("hello world", "hello")
        assert isinstance(result, int)

    def test_identical_text_zero_novel(self):
        text = "The ship sailed the ocean blue"
        result = count_novel_claims(text, text)
        assert result == 0

    def test_completely_different_text(self):
        original = "apple banana cherry"
        tile = "xylophone yak zebra"
        result = count_novel_claims(original, tile)
        assert result == 3

    def test_filters_common_words(self):
        original = "The ship was very big"
        tile = "The boat was very large"
        result = count_novel_claims(original, tile)
        # "boat" and "large" are novel, common words filtered
        assert result == 2

    def test_empty_tile(self):
        result = count_novel_claims("some text", "")
        assert result == 0

    def test_empty_original(self):
        result = count_novel_claims("", "novel content here")
        # "content" and "novel" survive after common word filter
        assert result >= 2

    def test_original_to_tile(self):
        """The original compressed into a tile should have some novel words."""
        tile = """
        In March 2024, a container vessel navigated a narrow strait.
        The navigation system experienced numerical drift due to
        floating-point precision issues. The crew intervened manually.
        """
        result = count_novel_claims(ORIGINAL, tile)
        assert result > 0
        assert result < 100  # But not absurdly many


class TestKeyFactsIntegrity:
    def test_key_facts_has_expected_entries(self):
        expected_keys = {"ship_name", "date", "containers", "destination", "speed"}
        assert expected_keys.issubset(set(KEY_FACTS.keys()))

    def test_key_facts_values_are_strings(self):
        for key, value in KEY_FACTS.items():
            assert isinstance(value, str)
            assert len(value) > 0
