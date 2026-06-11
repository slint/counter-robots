# -*- coding: utf-8 -*-
#
# This file is part of COUNTER-Robots.
# Copyright (C) 2018-2025 CERN.
# Copyright (C) 2025 Graz University of Technology.
#
# COUNTER-Robots is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Library for COUNTER-compliant detection of machines and robots.

The classifier is composed from one or more presets and used directly::

    from counter_robots import ClassifierBuilder, counter_preset

    classifier = ClassifierBuilder().use(counter_preset).build()
    classifier.is_robot(user_agent)

The module-level :func:`is_robot`, :func:`is_machine` and
:func:`is_robot_or_machine` keep working as before, backed by a default classifier
built from the generic COUNTER preset.
"""

import re
from importlib.resources import files

__version__ = "2026.6"


#
# Loading helpers
#


def patterns_from(text):
    """Read regex patterns from list text (drop blank lines and ``#`` comments)."""
    return [line for line in text.splitlines() if line and not line.startswith("#")]


def _read_package(filename):
    return (files(__package__) / "data" / filename).read_text()


def package_patterns(filename):
    """Read regex patterns from a file packaged under ``counter_robots/data``."""
    return patterns_from(_read_package(filename))


def file_patterns(path):
    """Read regex patterns from an external file."""
    with open(path, encoding="utf-8") as fp:
        return patterns_from(fp.read())


#
# Core
#


class _PatternSet:
    """Compiled matcher for one category, supporting mixed case sensitivity.

    Patterns can be added case-sensitively or case-insensitively, stored as at
    most two compiled regexes and OR-matched.
    """

    def __init__(self, cs_patterns, ci_patterns):
        self._cs = re.compile("|".join(cs_patterns)) if cs_patterns else None
        self._ci = (
            re.compile("|".join(ci_patterns), re.IGNORECASE) if ci_patterns else None
        )

    def matches(self, value):
        if not value:
            return False
        return bool(
            (self._cs and self._cs.search(value))
            or (self._ci and self._ci.search(value))
        )


class Classifier:
    """Immutable classifier of user agents.

    Build one with :class:`ClassifierBuilder`.
    """

    def __init__(self, robots, machines):
        self._robots = robots
        self._machines = machines

    def is_robot(self, user_agent):
        """Determine if a user agent is a robot/crawler/spider."""
        return self._robots.matches(user_agent)

    def is_machine(self, user_agent):
        """Determine if a user agent is a machine (script, library, tool)."""
        return self._machines.matches(user_agent)

    def is_robot_or_machine(self, user_agent):
        """Determine if a user agent is a robot or a machine."""
        return self.is_robot(user_agent) or self.is_machine(user_agent)


class ClassifierBuilder:
    """Fluent builder for a :class:`Classifier`.

    Every method returns ``self``; :meth:`build` freezes an immutable classifier.
    A preset is any callable taking the builder, applied with :meth:`use`.
    """

    def __init__(self):
        self._cs_robots, self._ci_robots = [], []
        self._cs_machines, self._ci_machines = [], []

    def robots(self, patterns, ignore_case=False):
        """Add robot patterns (case-sensitive unless ``ignore_case``)."""
        (self._ci_robots if ignore_case else self._cs_robots).extend(patterns)
        return self

    def machines(self, patterns, ignore_case=False):
        """Add machine patterns (case-sensitive unless ``ignore_case``)."""
        (self._ci_machines if ignore_case else self._cs_machines).extend(patterns)
        return self

    def use(self, preset):
        """Apply a preset, any callable that adds sources to this builder."""
        preset(self)
        return self

    def build(self):
        """Freeze and return the :class:`Classifier`."""
        return Classifier(
            _PatternSet(self._cs_robots, self._ci_robots),
            _PatternSet(self._cs_machines, self._ci_machines),
        )


#
# Presets
#

# crawler-user-agents tags that denote a machine (script/library) rather than a
# crawler; every other tag is treated as a robot.
_MACHINE_TAGS = frozenset({"http-library", "browser-automation"})


def counter_preset(builder):
    """Generic COUNTER baseline: atmire robots and Make-Data-Count machines."""
    builder.robots(package_patterns("robot.txt"))
    builder.machines(package_patterns("machine.txt"))


def extended_preset(builder):
    """Extended detection from the maintained crawler-user-agents dataset.

    Adds the crawler-user-agents patterns split by tag (HTTP libraries and
    browser-automation tools as machines, every other tag as robots), matched
    case-sensitively as that dataset intends, plus a curated list of non-browser
    tools and CLIs the dataset does not cover, matched case-insensitively.
    """
    import crawleruseragents

    robots, machines = [], []
    for entry in crawleruseragents.CRAWLER_USER_AGENTS_DATA:
        bucket = machines if _MACHINE_TAGS.intersection(entry["tags"]) else robots
        bucket.append(entry["pattern"])
    builder.robots(robots)
    builder.machines(machines)
    builder.machines(package_patterns("machine_extra.txt"), ignore_case=True)


#
# Default classifier and backwards-compatible module-level API
#


def default_classifier():
    """Build the default classifier (the generic COUNTER baseline)."""
    return ClassifierBuilder().use(counter_preset).build()


_default = None


def _get_default():
    global _default
    if _default is None:
        _default = default_classifier()
    return _default


def is_robot(user_agent):
    """Determine if a user agent is a robot/crawler/spider (default classifier)."""
    return _get_default().is_robot(user_agent)


def is_machine(user_agent):
    """Determine if a user agent is a machine (default classifier)."""
    return _get_default().is_machine(user_agent)


def is_robot_or_machine(user_agent):
    """Determine if a user agent is a robot or a machine (default classifier)."""
    return _get_default().is_robot_or_machine(user_agent)


__all__ = (
    "__version__",
    "Classifier",
    "ClassifierBuilder",
    "counter_preset",
    "extended_preset",
    "default_classifier",
    "package_patterns",
    "file_patterns",
    "patterns_from",
    "is_machine",
    "is_robot",
    "is_robot_or_machine",
)
