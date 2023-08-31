from waypaper.app import App
from waypaper.changer import change_wallpaper
from waypaper.config import cf
from waypaper.common import get_random_file
from waypaper.arguments import args


__version__ = "1.8.1"


def run():
    """Read user arguments and either run GUI app or just reset the wallpaper"""

    # Pick random wallpaper:
    if args.random:
        cf.wallpaper = get_random_file(cf.image_folder, cf.include_subfolders)

    # Set the wallpaper and quit:
    if args.restore:
        if cf.wallpaper is not None:
            change_wallpaper(cf.wallpaper, cf.fill_option, cf.color, cf.backend)
        exit()

    # Print the version and quit:
    if args.version:
        print(f"waypaper v.{__version__}")
        exit()

    # Start GUI:
    app = App()
    app.run()


if __name__ == "__main__":
    run()
