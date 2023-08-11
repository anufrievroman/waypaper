# Waypaper

GUI wallpaper setter for both Wayland and X11 window managers that works as a frontend for popular backends like `swaybg`, `swww`, and `feh`. You can check a [demo on reddit](https://www.reddit.com/r/unixporn/comments/15lbhuc/hyprland_waypaper_gui_wallpaper_setter_for_wayland/).

![screenshot](screenshot.jpg)

## Features

- Support for GIF animations (with `swww`)
- GUI wallpaper selection
- Works on both Wayland (with `swaybg` or `swww`) and X11 (with `feh`)
- Restores wallpaper at launch of your WM
  
## Installation

You need to install at least one of the backends and Waypaper, which works as a frontend.

### 1. Install a backend

Install a preferred backend from your package manager: [swaybg](https://github.com/swaywm/swaybg) or [swww](https://github.com/Horus645/swww) on Wayland or [feh](https://github.com/derf/feh) on x11. You can also install and test all of them.

- [swaybg](https://github.com/swaywm/swaybg) - the wayland backend that supports only static images.
- [swww](https://github.com/Horus645/swww) - the wayland backend that also supports animated GIFs.
- [feh](https://github.com/derf/feh) - the x11 backend that supports static images.

### 2. Install Waypaper (from PyPi)

`pipx install waypaper`

If `pipx` is not found, you first need to install `pipx` from your package manager, it's sometimes called `python-pipx`.

### 2. Install Waypaper (from AUR)

[waypaper-git](https://aur.archlinux.org/packages/waypaper-git) package is available in AUR, thanks to *metak*. So, on arch-based system, you can install it as:

`yay -S waypaper-git`

### Dependencies

- `swaybg` or `swww` or `feh`
- gobject python library (it might be called `python-gobject` or `python3-gi` or `python3-gobject` in your package manager.)

## Usage

`waypaper` command will run GUI application. Make sure to choose the backend that you installed.

To restore your wallpaper at launch, add `waypaper --restore` to your startup config. For example:

**In Hyprland**

`exec-once=waypaper --restore`

**In Sway or I3**

`exec waypaper --restore`
 
### Options

`--restore` - sets the last chosen wallpaper. Useful at launch of the window manager.

`--backend XXX` - specifies which backend to use, which can be either `swaybg`, `swww`, or `feh`. Useful if you use waypaper on both wayland and x11 on the same machine. By default, last used backend is used.

`--fill XXX` - specifies filling type, which can be eiher `fill`, `stretch`, `fit`, `center`, or `tile`.

## Troubleshooting

- If wallpaper does not change, make sure that `swaybg` or `swww` is installed.
- If application does not run, make sure to install gobject library (it might be called `python-gobject` or `python3-gi` in your package manager). Although it is supposed to be installed automatically with the package.
- Please understand that not all backends work on all system, choose the right one for you and stick to it.
- If you use different WMs on the same system, specify the backend when you restore the wallpaper at launch. For example: `waypaper --restore --backend feh`

## Roadmap

- Support for other backends like ~swww~, ~feh~, wbg, and hyprpaper.
- Additional options for ~search in subfolders~, background color, and a uniform color.
- Dynamic grid of thumbnails that adopts to the application width.
- Improve loading of folders with many images.

## Contributions

Feel free to propose PR and suggest the improvements.

If you'd like to support the development, consider [donations](https://www.buymeacoffee.com/angryprofessor).
