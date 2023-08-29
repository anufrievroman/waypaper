"""English translations of the program interface"""

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

MSG_HELP = "Waypaper's hotkeys:\n\nhjkl - Navigation (←↓↑→)\n"
MSG_HELP += "g - Scroll to top\nG - Scroll to bottom\n"
MSG_HELP += "s - Include/exclude images in subfolders\n? - Help\nq - Exit\n\n"
MSG_HELP += MSG_INFO

ERR_CACHE = "Error deleting cache"
ERR_BACKEND = "Looks like none of the wallpaper backends is installed in the system.\n"
ERR_BACKEND += "Use your package manager to install at least one of these backends:\n\n"
ERR_BACKEND += "- swaybg (for Wayland)\n- swww (for Wayland)\n"
ERR_BACKEND += "- feh (for Xorg)\n- wallutils (for Xorg & Wayland)\n\n"
ERR_BACKEND += MSG_INFO
ERR_WALL = "Error changing wallpaper: "
ERR_NOTSUP = "The backend is not supported:"
