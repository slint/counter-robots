..
    This file is part of COUNTER-Robots.
    Copyright (C) 2018-2025 CERN.
    Copyright (C) 2025 Graz University of Technology.

    COUNTER-Robots is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.

Changes
=======

Version 2026.6 (unreleased)

- refactor: composable, class-based API. ``Classifier`` (built by
  ``ClassifierBuilder``) exposes ``is_robot`` / ``is_machine`` /
  ``is_robot_or_machine``. Lists are added as presets, callables that add sources
  to the builder and are applied with ``builder.use(...)``; ``counter_preset`` is
  the generic COUNTER baseline. The module-level ``is_robot`` / ``is_machine`` /
  ``is_robot_or_machine`` remain as a backwards-compatible default classifier built
  from ``counter_preset``.

- feat: ``extended_preset`` adds detection from the maintained
  ``crawler-user-agents`` dataset (a new dependency), split by tag so HTTP
  libraries and browser-automation tools are machines and every other tag is a
  robot (case-sensitive, as that dataset intends), plus a curated
  ``machine_extra.txt`` of non-browser tools and CLIs it does not cover, matched
  case-insensitively.

Version 2025.11 (released on 2025-11-04)

- chore(setup): update dependencies
- fix: pkg_resources DeprecationWarning

Version 2025.2 (released on 2025-02-13)

- User agents lists update.

Version 2018.6 (released on 2018-06-15)

- Initial public release.
