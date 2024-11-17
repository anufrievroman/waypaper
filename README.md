# Waypaper

GUI wallpaper setter for Wayland and Xorg window managers. It works as a frontend for popular wallpaper backends like `swaybg`, `swww`, `wallutils`, `hyprpaper`, `mpvpaper` and `feh`. See details in [the documentation](https://anufrievroman.gitbook.io/waypaper).

![screenshot](screen.jpg)

## Features

- Vim keys
- Support for GIF animations (with `swww` or `mpvpaper`)
- Support for videos (with `mpvpaper`)
- Support for multiple monitors (with `swww` or `swaybg` or `hyprpaper` or `mpvpaper`)
- Works on Wayland (with `swww` or `swaybg` or `hyprpaper` or `wallutils` or `mpvpaper`)
- Works on Xorg (with `feh` or `wallutils`)
- Restores wallpaper at launch of your WM
- Caching for fast loading

## Installation

You need to install at least one of the backends and Waypaper, which works as a frontend.

### 1. Install a backend

Install a preferred backend from your package manager: [swww](https://github.com/Horus645/swww) or [swaybg](https://github.com/swaywm/swaybg) or [hyprpaper](https://github.com/hyprwm/hyprpaper) on Wayland or [feh](https://github.com/derf/feh) on Xorg or [mpvpaper](https://github.com/GhostNaN/mpvpaper) or [wallutils](https://github.com/xyproto/wallutils) on both.

### 2. Install Waypaper

Waypaper is available as a package in different repositories listed below:

#### On all distributions

`pipx install waypaper`

If `pipx` is not found, you first need to install `pipx` from your package manager, it's sometimes called `python-pipx`.

#### On Arch-based distributions

`yay -S waypaper`

The [waypaper](https://aur.archlinux.org/packages/waypaper) package and developer package [waypaper-git](https://aur.archlinux.org/packages/waypaper-git) are available in AUR, thanks to *metak*. Please upvote to support the project.

#### On NixOS

The `waypaper` package is available thanks to Basil Keeler.

#### On OpenSUSE

Users of OpenSUSE [reported issue with installation](https://github.com/anufrievroman/waypaper/issues/30) via `pipx install waypaper`. This might be resolved by installing the `python311-pycairo-devel` package.

#### On Fedora

Waypaper is available in an external repository owned by Solopasha. You can add this repository as `sudo dnf copr enable solopasha/hyprland` and install as `sudo dnf install waypaper`.

### Dependencies

- `swww` or `swaybg` or `feh` or `wallutils` or `hyprpaper` or `mpvpaper`
- gobject python library (it might be called `python-gobject` or `python3-gi` or `python3-gobject` in your package manager.)
- `python-importlib_metadata`
- `python-imageio`
- `python-imageio-ffmpeg`
- `python-screeninfo`
- `python-platformdirs`

## Usage

`waypaper` command will run GUI application.

### Options

To restore your wallpaper at launch, add `waypaper --restore` to your startup config.

See more [details on user arguments in the documentation](https://anufrievroman.gitbook.io/waypaper/usage).

### Configuration

See [configuration details in the documentation](https://anufrievroman.gitbook.io/waypaper/configuration).

### Keybindings

See [list of keybindings in the documentation](https://anufrievroman.gitbook.io/waypaper/keybindings).

### Troubleshooting

See typical problems [explained in the documentation](https://anufrievroman.gitbook.io/waypaper/troubleshooting)

## Contribution

Feel free to propose PR and suggest the improvements. I'll highly appreciate help with packaging for various distributions. If you wish to contribute with translation into your language, please see the `translations.py` file. Here a few guiding principles for creating pull requests:

- Please do not apply automatic code formatting tools on the entire code base.
- Please do separate pull requests for each feature, don't combine unrelated changes into one PR.
- For big changes, please open an issue first to discuss, otherwise PR might be declined.

## Support

I am not a professional developer and work on open-source projects in my free time. If you'd like to support the development, consider donations via [buymeacoffee](https://www.buymeacoffee.com/angryprofessor) or cryptocurrencies:

- BTC `bc1qpkzmutdqfxkce34skt09vll97s5smpa0r2tyzj`
- ETH `0x6f1Ce9cA181458Fc153a5f7cBF88044736C3b00C`
- BNB `0x40f22c372758E35C905458cAF8BB17f51ac133d1`
- LTC `ltc1qtu33qyv2xlzxda5mmrmk943zpksq8q75tuh85p`
