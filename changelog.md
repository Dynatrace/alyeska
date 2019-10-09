# Changelog

---

## Unreleased

### Added

- #36 Support parametrized queries in `sqlagent`

### Deprecated

- Deprecated some `sqlagent` functions: `plan_tasks`, `execute_tasks`, `process_batch`, `gather_subtasks`, `run_subtasks`, `execute_sql`, and `run_sql`.

---

## 0.3.0a0 - 2019-10-07

### Added

- Changed the default behavior of `compose_sh` to check that Task files actually exist
- A new `--no-check` flag in `compose_sh` to skip checking for Task file presence
- Created changelog.md
- A new dependency: packaging >= 19.2

### Fixed

- ReadTheDocs documentation now builds properly

### Removed

- The check_environment function has been removed.

---

## 0.2.0a0 - 2019-09-11

### Added

- New issue templates for bug reports and feature requests
- Alyeska is now available on PyPI
- Alyeska documentation is now on ReadTheDocs
- Minor documentation upgrades

---

## 0.1.0a0 - 2019-08-23

- First stable alpha release

---

[Unreleased]: https://github.com/Dynatrace/alyeska/tree/master
[0.2.0a0]: https://github.com/Dynatrace/alyeska/tree/v0.3.0a
[0.2.0a0]: https://github.com/Dynatrace/alyeska/tree/v0.2.0a
[0.1.0a0]: https://github.com/Dynatrace/alyeska/tree/v0.1.0a

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
