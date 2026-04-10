"""
This is a daemon that randomly changes wallpaper every specified number of minutes.
THIS IS WORK IN PROGRESS AND NOT USED IN THE PROGRAM YET.
"""

import time
import os
import argparse

def main():
    parser = argparse.ArgumentParser(description="Randomly changes wallpaper every specified number of seconds.")
    parser.add_argument("interval", type=int, help="Time interval in seconds until next wallpaper change.")
    args = parser.parse_args()

    try:
        while True:
            os.system("waypaper --random")
            print(f"Command to change wallpaper executed. Waiting {args.interval} seconds.")
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("Program interrupted. Exiting.")

if __name__ == "__main__":
    main()
