# Waypaper

GUI wallpaper setter for Wayland and Xorg window managers. It works as a frontend for popular wallpaper backends like `swaybg`, `swww`, `wallutils` and `feh`. You can check a [demo on reddit](https://www.reddit.com/r/unixporn/comments/15lbhuc/hyprland_waypaper_gui_wallpaper_setter_for_wayland/).

![screenshot](screenshot.jpg)

## Features

- Vim keys
- Support for GIF animations (with `swww`)
- Support for multiple monitors (with `swww`)
- Works on both Wayland (with `swww` or `swaybg` or `wallutils`) and Xorg (with `feh` or `wallutils`)
- Restores wallpaper at launch of your WM
- Caching for fast loading
- Translated in en, fr, de, ru, pl
  
## Installation

You need to install at least one of the backends and Waypaper, which works as a frontend.

### 1. Install a backend

Install a preferred backend from your package manager: [swww](https://github.com/Horus645/swww) or [swaybg](https://github.com/swaywm/swaybg) on Wayland or [feh](https://github.com/derf/feh) on Xorg or [wallutils](https://github.com/xyproto/wallutils) on both.

### 2. Install Waypaper

Waypaper is available as a package in different repositories listed below:

#### On all distributions

`pipx install waypaper`

If `pipx` is not found, you first need to install `pipx` from your package manager, it's sometimes called `python-pipx`.

#### On Arch-based distributions

`yay -S waypaper-git`

The [waypaper-git](https://aur.archlinux.org/packages/waypaper-git) package is available in AUR, thanks to *metak*. Please upvote to support the project.

#### On NixOS

The `waypaper` package is available thanks to Basil Keeler.

### Dependencies

- `swww` or `swaybg` or `feh` or `wallutils`
- gobject python library (it might be called `python-gobject` or `python3-gi` or `python3-gobject` in your package manager.)
- `python-importlib_metadata`
- `python-platformdirs`

## Usage

`waypaper` command will run GUI application. Make sure to choose the backend that you installed.

To restore your wallpaper at launch, add `waypaper --restore` to your startup config. For example:

**In Hyprland**

`exec-once=waypaper --restore`

**In Sway or I3**

`exec waypaper --restore`
 
To see the list of hotkeys, press `?`.

### Options

`--restore` - sets the last chosen wallpaper. Useful at launch of the window manager.

`--random` - sets a random wallpaper. Makes sense only together with `--restore` key.

`--backend XXX` - specifies which backend to use, which can be either `swaybg`, `swww`, `feh`, or `wallutils`. Useful if you use waypaper on both Wayland and Xorg on the same machine. By default, last used backend is used.

`--fill XXX` - specifies filling type, which can be eiher `fill`, `stretch`, `fit`, `center`, or `tile`.

If you wish to change language, change `laguage` variable in `.config/waypaper/config.ini` file. Supported options are `en`, `de`, `fr`, `ru`, `pl`.

## Troubleshooting

- If wallpaper does not change, first, try to launch waypaper in the terminal and see the output. Also, try to change it via command line using chosen backend to make sure that backend by itself works correctly.
- If application does not run, make sure to install `gobject` library (it might be called `python-gobject` or `python3-gi` in your package manager). Although it is supposed to be installed automatically with the package.
- Please understand that not all backends work on all systems. `feh` is only for Xorg, while `swww` and `swaybg` are only for Wayland.
- If you use different WMs on the same system, specify the backend when you restore the wallpaper at launch. For example: `waypaper --restore --backend feh` or use `wallutils` which works on both Wayland and Xorg.

## Roadmap

- Additional options for ~subfolders~, ~color~, ~sorting~, ~randomizing~ and setting a uniform color.
- ~Support for other backends like swww, feh, wallutils~, and maybe hyprpaper.
- ~Better keyboard-driven experience and hjkl support.~
- ~Support for multiple monitors with swww~ and swaybg
- Display animated previews of gif wallpapers
- Translations

## Contributions

Feel free to propose PR and suggest the improvements. I'll also appreciate any help with packaging for various distributions. Also, if you wish to contribute with translation into your language, plese translate `translation_en.py` file, and I'll do the rest.

If you'd like to support the development, consider [donations](https://www.buymeacoffee.com/angryprofessor).
