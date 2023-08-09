# Waypaper

GUI wallpaper setter for Wayland-based window managers that works as a frontend for popular backends like `swaybg` and `swww`.

![screenshot](screenshot.jpg)

## Features

- GUI wallpaper selection
- Support for GIF animations (with `swww` backend)
- Works on Wayland. It's your wayland replacement of `nitrogen`.
- Restores wallpaper on launch of your WM with `waypaper --restore`
  
## Installation

`pipx install waypaper` (you may need to install `pipx` from your package manager first, it's sometimes called `python-pipx`)

Also, install `swaybg` or `swww` from your package manager.

### Dependencies

- `swaybg` or `swww`
- gobject python library (it might be called `python-gobject` or `python3-gi` or `python3-gobject` in your package manager.)

## Usage

`waypaper` will run GUI application.

To restore the chosen wallpaper at launch, add `waypaper --restore` to your startup config. For example, in your Hyprland config you can write:

`exec-once=waypaper --restore`

## Troubleshooting

- If wallpaper does not change, make sure that `swaybg` or `swww` is installed.
- If application does not run, much sure to install gobject library (it might be called `python-gobject` or `python3-gi` in your package manager)

## Roadmap

- Support for other backends like ~swww~, hyprpaper and xorg backends.
- Additional options for search in ~subfolders~, background colors etc.
- Dynamic grid of thumbnails that adopts to the application width.

## Contributions

Feel free to propose PR and suggest the improvements. However, I don't have much time to add features to this project.
If you'd like to support the development, consider [donations](https://www.buymeacoffee.com/angryprofessor).
