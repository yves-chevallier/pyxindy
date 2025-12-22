# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Documentation index page.
- makeindex4 compatibility for makeindex options and multi-file inputs.
- makeindex4 support for `.ist` styles via `.xdy` conversion.
- makeglossaries compatibility `-i` flag.
- Additional CLI tests for makeindex4 and makeglossaries.

### Changed

- Documentation logos.
- makeindex4 now supports optional range suppression via `-r`.

### Fixed

- Documentation fixes.
- Runtime error fixes.

## [0.0.5] - 2025-12-17

### Added

- License.
- Badges.

### Changed

- Documentation theme and logos.
- Background logo.

## [0.0.4] - 2025-12-17

### Changed

- Documentation updates.

### Fixed

- Mike integration.

## [0.0.3] - 2025-12-16

### Added

- Core xindy port (raw reader, index builder, markup renderer).
- TeX tooling (tex2xindy, makeindex4, makeglossaries).
- Snapshots and tests.
- CLI and CI workflow.
- Documentation and MkDocs site.

### Changed

- Migrated project structure and packaging.
- Renamed package.
- Updated README.

### Fixed

- Ruff issues and CI publishing fixes.
