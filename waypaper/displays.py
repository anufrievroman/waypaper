"""This module checks avaliable displays depending on the display server"""

import os

def detect_display_server():
    if os.environ.get('WAYLAND_DISPLAY'):
        return "Wayland"
    else:
        return "Xorg"

def get_wayland_displays():
    displays = []
    wayland_socket = os.environ.get('WAYLAND_DISPLAY')
    if wayland_socket:
        displays.append(f"wayland-{wayland_socket}")
    return displays

def get_xorg_displays():
    displays = []
    xorg_display = os.environ.get('DISPLAY')
    if xorg_display:
        displays.append(f"xorg-{xorg_display}")
    return displays

def main(display_server):
    available_displays = []

    if display_server.lower() == "wayland":
        displays = get_wayland_displays()
    else:
        displays = get_xorg_displays()
    available_displays.extend(displays)

    if not available_displays:
        print("No displays found.")
    else:
        print("Available displays:")
        for display in available_displays:
            print(display)

if __name__ == "__main__":
    display_server = detect_display_server()
    print(f"The system is running under: {display_server}")
    main(display_server)
