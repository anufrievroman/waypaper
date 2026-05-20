"""Small daemon that periodically triggers `waypaper --random`."""

import argparse
import logging
import subprocess
import sys
import time
from typing import Sequence

from waypaper.config import Config

LOG = logging.getLogger(__name__)


def positive_interval(value: str) -> int:
    interval = int(value)
    if interval <= 0:
        raise argparse.ArgumentTypeError("interval must be a positive integer")
    return interval


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Randomly changes wallpaper every specified number of seconds."
    )
    parser.add_argument(
        "interval",
        nargs="?",
        default=None,
        type=positive_interval,
        help="Time interval in seconds between random wallpaper changes. Defaults to the Waypaper config value.",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def read_config_interval() -> int:
    config = Config()
    config.read()
    config.check_validity()
    return int(config.waypaperd_cycle_length)


def resolve_interval(interval: int | None) -> int:
    if interval is not None:
        return interval
    return read_config_interval()


def build_waypaper_command() -> list[str]:
    return [sys.executable, "-m", "waypaper", "--random"]


def trigger_random_wallpaper(command: Sequence[str] | None = None) -> int:
    result = subprocess.run(
        list(command) if command is not None else build_waypaper_command(),
        check=False,
    )
    if result.returncode == 0:
        LOG.info("Random wallpaper command completed successfully.")
    else:
        LOG.warning("Random wallpaper command exited with status %s.", result.returncode)
    return result.returncode


def main(argv: Sequence[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args = parse_args(argv)
    interval = resolve_interval(args.interval)
    command = build_waypaper_command()

    LOG.info("Starting waypaperd with interval=%s seconds.", interval)
    try:
        while True:
            trigger_random_wallpaper(command)
            LOG.info("Sleeping for %s seconds.", interval)
            time.sleep(interval)
    except KeyboardInterrupt:
        LOG.info("waypaperd interrupted, exiting cleanly.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
