"""English translations of the program interface"""

MSG_NAME = "Waypaper"
MSG_DESC = "GUI wallpaper setter for Wayland and X11. It works as a frontend for feh, swaybg, wallutils, and swww."
MSG_INFO = "For more information, visit:\nhttps://github.com/anufrievroman/waypaper"

MSG_ARG_HELP = "print version of the program"
MSG_ARG_FILL = "specify how to fill the screen with chosen image"
MSG_ARG_REST = "restore last wallpaper"
MSG_ARG_BACK = "specify which backend to use to set wallpaper"

MSG_PATH = "Selected image path:"
MSG_SELECT = "Select"
MSG_REFRESH = "Refresh"
MSG_EXIT = "Exit"
MSG_SUBFOLDERS = "Subfolders"
MSG_CHANGEFOLDER = "Change wallpaper folder"
MSG_CACHING = "Caching wallpapers..."
MSG_SETWITH = "Wallpaper was set with"

MSG_HELP = "Waypaper's hotkeys:\n\nhjkl - Navigation (←↓↑→)\ng - Scroll to top\n"
MSG_HELP += "G - Scroll to bottom\nr - Recache images"
MSG_HELP += "\ns - Include/exclude images in subfolders\n? - Help\nq - Exit\n\n"
MSG_HELP += MSG_INFO

ERR_CACHE = "Error deleting cache"
ERR_BACKEND = "Looks like none of the wallpaper backends is installed in the system.\n"
ERR_BACKEND += "Use your package manager to install at least one of these backends:\n"
ERR_BACKEND += "\n- swaybg (for Wayland)\n- swww (for Wayland)\n- feh (for Xorg)\n- wallutils (for Xorg & Wayland)"
ERR_WALL = "Error changing wallpaper: "
ERR_NOTSUP = "The backend is not supported:"
