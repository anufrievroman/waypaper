# Changelog

## 2.9

### Added
- Automatic wallpaper change (slideshow): a GUI panel to start/stop the `waypaperd` daemon and set the interval, working on both Linux and macOS.
- `gslapper` backend support, with IPC-based playback controls.
- macOS support: installation instructions, an app bundle with icon, system dark-mode matching, backend detection, and window focus fixes.
- `--zen-mode` flag.
- Filter option for the `swww` and `awww` backends.
- Live CSS reload on the `SIGUSR1` signal.
- `$fill` and `$color` keywords for `post_command`.
- Caching progress percentage in the loading label.
- webp support for the `feh` backend.
- Portuguese (Brazilian) translation.

### Fixed
- Dual-monitor wallpapers were overridden by the "All" wallpaper on restore (#165).
- Slideshow daemon now launches correctly on macOS.
- Warn when `socat` is missing, which the `mpvpaper` backend needs (#221).
- Several `linux-wallpaperengine` fixes: `fill_option`, "All" monitors, `disable-parallax`, `noautomute`, kill behavior, and launch notifications.
- Expand `~` in the stylesheet path.
- Missing pt-BR translation attributes that crashed GUI startup.
- Suppress the missing keybindings file error.

### Changed
- Quote dynamic tokens in `post_command` (security hardening).
- Use `pgrep -f` instead of `ps aux` for process lookup (performance).
- GTK CSS provider priority moved to the user level.
