# -*- coding: utf-8 -*-
#
# This file is part of COUNTER-Robots.
# Copyright (C) 2018 CERN.
#
# COUNTER-Robots is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test counter robots."""

import pytest

from counter_robots import (
    ClassifierBuilder,
    counter_preset,
    extended_preset,
    file_patterns,
    is_machine,
    is_robot,
    is_robot_or_machine,
)


def test_version():
    """Test version string."""
    from counter_robots import __version__

    assert __version__


def test_is_robot():
    machine_ua = "PostmanRuntime/7.30.0"
    robot_ua = "AdsBot-Google (+http://www.google.com/adsbot.html)"
    assert is_robot(machine_ua) is not True
    assert is_robot(robot_ua) is True


def test_is_machine():
    machine_ua = "Wget/1.14 (linux-gnu)"
    robot_ua = "AdsBot-Google (+http://www.google.com/adsbot.html)"
    assert is_machine(machine_ua) is True
    assert is_machine(robot_ua) is not True


def test_is_robot_or_machine():
    machine_ua = "Wget/1.14 (linux-gnu)"
    robot_ua = "AdsBot-Google (+http://www.google.com/adsbot.html)"
    assert is_robot_or_machine(machine_ua) is True
    assert is_robot_or_machine(robot_ua) is True


def test_baseline_is_case_sensitive():
    """The COUNTER baseline matches case-sensitively, so CamelCase bots evade it."""
    assert is_robot("YisouSpider") is False


@pytest.fixture
def extended_classifier():
    return ClassifierBuilder().use(counter_preset).use(extended_preset).build()


@pytest.mark.parametrize(
    "ua",
    [
        "YisouSpider",
        "LinkedInBot/1.0 (compatible; Mozilla/5.0)",
        "Googlebot/2.1 (+http://www.google.com/bot.html)",
        "Screaming Frog SEO Spider/23.2",
        "Google-NotebookLM",
    ],
)
def test_extended_preset_robots(extended_classifier, ua):
    """The extended preset catches crawlers the case-sensitive baseline misses."""
    assert extended_classifier.is_robot(ua) is True


@pytest.mark.parametrize(
    "ua",
    [
        "python-requests/2.31",  # crawler-user-agents http-library
        "Python/3.10 aiohttp/3.10.5",
        "GDAL/3.12.1",  # curated tool list
        "siril/1.4",
    ],
)
def test_extended_preset_machines(extended_classifier, ua):
    """The extended preset tags HTTP libraries and research tools as machines."""
    assert extended_classifier.is_machine(ua) is True


def test_extended_preset_tools_case_insensitive(extended_classifier):
    """The curated tools list is matched case-insensitively."""
    assert extended_classifier.is_machine("gdal/3.12.1") is True


def test_extended_preset_keeps_browsers(extended_classifier):
    chrome = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
    )
    assert extended_classifier.is_robot(chrome) is False
    assert extended_classifier.is_machine(chrome) is False


def test_external_file_via_builder(tmp_path):
    """A deployment can add its own list file through the builder."""
    f = tmp_path / "instance_robots.txt"
    f.write_text("# my instance\nMyCustomScraper\n")
    classifier = (
        ClassifierBuilder()
        .use(counter_preset)
        .robots(file_patterns(str(f)), ignore_case=True)
        .build()
    )
    assert classifier.is_robot("MyCustomScraper/1.0") is True
    assert classifier.is_robot("PostmanRuntime/7.30.0") is not True
