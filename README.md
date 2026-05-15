# Waypaper

GUI wallpaper setter for Wayland, Xorg, and macOS. It works as a frontend for popular wallpaper backends like `swaybg`, `swww`, `awww`, `wallutils`, `hyprpaper`, `mpvpaper`, `gslapper`, `xwallpaper`, `feh`, `linux-wallpaperengine`, and `macos`. See [demo](https://www.youtube.com/watch?v=O9OL7iH_KVY) and [documentation](https://anufrievroman.gitbook.io/waypaper).

![screenshot](screen.jpg)

## Features

- Vim keys
- Supports GIF animations (with `awww` or `mpvpaper` or `gslapper`)
- Supports videos (with `mpvpaper` or `gslapper`)
- Supports multiple monitors (with `awww` or `swaybg` or `hyprpaper` or `mpvpaper`)
- Works on Wayland (with `awww` or `swww` or `swaybg` or `hyprpaper` or `wallutils` or `mpvpaper` or `gslapper`)
- Works on Xorg (with `feh`, `xwallpaper` or `wallutils`)
- Works on macOS (with `macos`)
- Supports `linux-wallpaperengine` so you can use your animated wallpapers from Steam's Wallpaper Engine
- Restores wallpaper after restart (`waypaper --restore`)
- Fast and minimal (315 kB)

## Installation

Install at least one of the backends and Waypaper, which works as a frontend.

### 1. Install a backend

Install a preferred backend from your package manager: [swww (archived)](https://github.com/Horus645/swww) or [awww](https://codeberg.org/LGFae/awww) or [swaybg](https://github.com/swaywm/swaybg) or [hyprpaper](https://github.com/hyprwm/hyprpaper) on Wayland or [xwallpaper](https://github.com/stoeckmann/xwallpaper) or [feh](https://github.com/derf/feh) on Xorg or [mpvpaper](https://github.com/GhostNaN/mpvpaper) or [gslapper](https://github.com/gurrgur/gslapper) or [wallutils](https://github.com/xyproto/wallutils) on both. Install [linux-wallpaperengine](https://github.com/Almamu/linux-wallpaperengine) if you want to use Steam's Wallpaper Engine animated wallpapers. On macOS, use the built-in `macos` backend.

### 2. Install Waypaper

Install `waypaper`, which is available in different repositories:

#### On all distributions

`pipx install waypaper`

If `pipx` is not found, you first need to install `pipx` from your package manager, it's sometimes called `python-pipx`.

#### On Arch-based distributions

`yay -S waypaper`

The [waypaper](https://aur.archlinux.org/packages/waypaper) package and unstable developer package [waypaper-git](https://aur.archlinux.org/packages/waypaper-git) are available in AUR, thanks to *metak*. Please upvote to support the project.

#### On NixOS

The `waypaper` package is available thanks to Basil Keeler.

#### On OpenSUSE

Users of OpenSUSE [reported issue with installation](https://github.com/anufrievroman/waypaper/issues/30) via `pipx install waypaper`. This can be resolved by installing the `python313-pycairo-devel` and `python313-gobject-devel` packages first.

#### On Fedora

Waypaper is available in an external repository owned by Solopasha. You can add this repository as `sudo dnf copr enable lionheartp/Hyprland` and install as `sudo dnf install waypaper`.

### Dependencies

- `awww` or `swww` or `swaybg` or `xwallpaper` or `feh` or `wallutils` or `hyprpaper` or `mpvpaper` or `gslapper` or `linux-wallpaperengine` or `macos`
- gobject python library (it might be called `python-gobject` or `python3-gi` or `python3-gobject` in your package manager.)
- `python-imageio`
- `python-imageio-ffmpeg`
- `python-screeninfo`
- `python-platformdirs`

## Usage

`waypaper` command will run GUI application.

`waypaperd` runs a simple slideshow daemon that periodically triggers `waypaper --random`.

To restore your wallpaper after restart, add `waypaper --restore` to [your WM startup config](https://anufrievroman.gitbook.io/waypaper/usage).

### Slideshow daemon service

Packaged installations also ship a `waypaperd.service` user unit. You can enable it with:

`systemctl --user daemon-reload && systemctl --user enable --now waypaperd.service`

The unit defaults to a 30-minute interval. To override that without editing the installed unit directly, create a drop-in:

```ini
systemctl --user edit waypaperd.service

[Service]
Environment=WAYPAPERD_INTERVAL=600
```

Then restart the service with `systemctl --user restart waypaperd.service`.

## Documentation

- [CLI options](https://anufrievroman.gitbook.io/waypaper/usage#cli-options)
- [Configuration](https://anufrievroman.gitbook.io/waypaper/configuration)
- [Keybindings](https://anufrievroman.gitbook.io/waypaper/keybindings)
- [Troubleshooting](https://anufrievroman.gitbook.io/waypaper/troubleshooting)
- [Automatically changing wallpaper](https://anufrievroman.gitbook.io/waypaper/usage#automatically-changing-wallpaper)
- [Set wallpaper after restart](https://anufrievroman.gitbook.io/waypaper/usage)

## Contribution

Feel free to propose PR and suggest the improvements. I'll appreciate help with packaging for various distributions. If you wish to contribute with translation into your language, please see the `translations.py` file. Here are a few guiding principles for contribution:

- Please do not apply automatic code formatting tools on the entire code base.
- Please propose features separately, don't combine unrelated changes into one PR.
- For big changes, please open an issue first to discuss, otherwise PR might be declined.
- If the changes involve hundreds of lines of code, probably something is wrong. Most things can be done with small adjustments.

## Support

I am not a professional developer and work on open-source projects in my free time. If you'd like to support the development, consider donations via:

- Cards and PayPal: [BuyMeACoffee](https://www.buymeacoffee.com/angryprofessor)
- BTC `bc1qpkzmutdqfxkce34skt09vll97s5smpa0r2tyzj`
- ETH `0x6f1Ce9cA181458Fc153a5f7cBF88044736C3b00C`
- BNB `0x40f22c372758E35C905458cAF8BB17f51ac133d1`
- LTC `ltc1qtu33qyv2xlzxda5mmrmk943zpksq8q75tuh85p`
- XMR `4AHRhpNYUZcPVN78rbUWAzBuvMKQdpwStS5L3kjunnBMWWW2pjYBko1RUF6nQVpgQPdfAkM3jrEWrWKDHz1h4Ucd4gFCZ9j`
