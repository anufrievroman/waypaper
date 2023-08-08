# Waypaper

GUI wallpaper setter for Wayland-based window managers such as Hyprland or Sway.

![screenshot](screenshot.jpg)

## Installation

`pip install waypaper` or in case of troubles `pipx install waypaper`. Also, install `swaybg` from your package manager.

### Dependencies

- `swaybg`
- gobject python library (it might be called `python-gobject` or `python3-gi` or `python3-gobject` in your package manager.)

## Usage

`waypaper` will run GUI application.

To restore the chosen wallpaper at launch, add `waypaper --restore` to your startup config. For example, in your Hyprland config you can write:

`exec-once=waypaper --restore`

## Troubleshooting

- If wallpaper does not change, make sure that `swaybg` is installed.
- If application does not run, much sure to install gobject library (it might be called `python-gobject` or `python3-gi` in your package manager)

## Roadmap

- Support for other backends like `hyprpaper` and xorg backends.
- Additional options for search in subfolders, background colors etc.
- Dynamic grid of thumbnails that adopts to the application width.

## Contributions

Feel free to propose PR and suggest the improvements. However, I don't have much time to add features to this project.
If you'd like to support the development, consider [donations](https://www.buymeacoffee.com/angryprofessor).
