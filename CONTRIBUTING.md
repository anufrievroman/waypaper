# Contributing

## Getting Started

1. Create a python venv
``` bash
    python3 -m venv $HOME/.venvs/waypaper
```
2. Install the build tools
``` bash
    $HOME/.venvs/waypaper/bin/pip install --upgrade build
```
3. Use the venv's python to run the setup.py
``` bash
    $HOME/.venvs/waypaper/bin/python -m build
```
4. You can now call the waypaper __main__.py with the venv python to test functionality

## Setting up the service manually

1. Edit ``` waypaperd.service ``` to point to your copy of waypaperd
2. Copy ``` waypaperd.service ``` to ``` $HOME/.config/systemd/user/ ```
3. Run ``` systemctl --user start waypaperd.service ``` to start it
4. Run ``` systemctl --user enable waypaperd.servic ``` to enable it to run every time you log in
5. Run ``` systemctl --user status waypaperd.service ``` to check if it's running properly

## Installing

-- TODO: get instructions for building when ready to deploy to AUR/PyPi
