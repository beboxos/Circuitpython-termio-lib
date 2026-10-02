# Changelog

## 2.0.0

### Fixed
- Coordinates are now really 0-based: `printat(0, 0, ...)` and `printat(1, 0, ...)`
  used to land on the same cell because ANSI positions start at 1.
  **Existing drawings move one cell up/left**; use `set_offset()` if you relied on the old placement.
- `cls()` no longer prints a stray newline and puts the cursor back at the top left.
- `rect()` / `fillrect()` handle widths/heights of 0, 1 and 2 correctly.

### Added
- Colors and styles: `fg=`, `bg=`, `style=` on every drawing function, `color()`, `reset()`.
- Box styles `BOX_ASCII`, `BOX_SINGLE`, `BOX_DOUBLE`, `BOX_ROUND`.
- `window()`, `progress()`, `center()`, `hline()`, `vline()`.
- Cursor helpers: `goto()`, `home()`, `cursor()`, `save_cursor()`, `restore_cursor()`,
  `clear_line()`, `clear_eol()`, `set_offset()`.
- Unit tests and GitHub Actions CI.

### Changed
- Each shape is sent in a single write (faster on slow serial links).
- `char` / `fillchar` arguments are now optional; old positional calls still work.

## 1.0.0
- First release: `cls`, `printat`, `rect`, `fillrect`.
