"""Module that runs the system processes to change the wallpaper"""

import hashlib
import os
import shlex
import socket
import subprocess
import threading
import time
from typing import Optional
from pathlib import Path

from waypaper.common import is_socat_available
from waypaper.config import Config
from waypaper.options import get_monitor_names_with_hyprctl, get_plugged_monitors, \
    LINUX_WALLPAPERENGINE_CLAMP, LINUX_WALLPAPERENGINE_FILL_OPTIONS


GSLAPPER_IPC_TIMEOUT = 2.0
GSLAPPER_STARTUP_TIMEOUT = 3.0
GSLAPPER_POLL_INTERVAL = 0.05
GSLAPPER_VIDEO_CHANGE_ERROR = "cannot update path (use --auto-stop for video changes)"

# ponytail: wallpaper changes are infrequent, so one global lock is enough;
# replace it with per-output locks if real workloads show contention.
_GSLAPPER_LIFECYCLE = threading.Lock()


class GSlapperIPCError(RuntimeError):
    """An error returned by gSlapper's IPC protocol."""


def _gslapper_runtime_dir() -> Path:
    runtime_dir = os.environ.get("XDG_RUNTIME_DIR")
    if not runtime_dir:
        raise RuntimeError("XDG_RUNTIME_DIR is not set")
    path = Path(runtime_dir) / "waypaper"
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    return path


def gslapper_socket_path(monitor: str) -> Path:
    # ponytail: 64 hash bits keep Unix socket names short; use the full digest
    # if an output-name collision ever appears in practice.
    digest = hashlib.sha256(monitor.encode("utf-8")).hexdigest()[:16]
    return _gslapper_runtime_dir() / f"gslapper-{digest}.sock"


def _gslapper_ipc(socket_path: Path, command: str) -> str:
    if "\n" in command or "\r" in command:
        raise ValueError("gSlapper IPC commands cannot contain newlines")

    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
        connection.settimeout(GSLAPPER_IPC_TIMEOUT)
        connection.connect(str(socket_path))
        connection.sendall(f"{command}\n".encode("utf-8"))
        with connection.makefile("r", encoding="utf-8", newline="\n") as response_file:
            response = response_file.readline().rstrip("\r\n")

    if not response:
        raise GSlapperIPCError("gSlapper returned an empty IPC response")
    if response.startswith("ERROR:"):
        raise GSlapperIPCError(response.removeprefix("ERROR:").strip())
    return response


def _gslapper_query(socket_path: Path) -> tuple[str, str, Path]:
    fields = _gslapper_ipc(socket_path, "query").split(" ", 3)
    if (
        len(fields) != 4
        or fields[0] != "STATUS:"
        or fields[1] not in {"playing", "paused"}
        or fields[2] not in {"image", "video"}
        or not fields[3]
    ):
        raise GSlapperIPCError("gSlapper returned an invalid status response")
    return fields[1], fields[2], Path(fields[3])


def _gslapper_managed_sockets() -> list[Path]:
    return sorted(_gslapper_runtime_dir().glob("gslapper-*.sock"))


def _gslapper_outputs(monitor: str) -> list[str]:
    if monitor != "All":
        return [monitor]
    outputs = [name for name in get_plugged_monitors() if name]
    if not outputs:
        raise RuntimeError("Could not detect any outputs for gSlapper")
    return outputs


def _gslapper_media_path(image_path: Path) -> str:
    path = str(image_path)
    if "\n" in path or "\r" in path:
        raise ValueError("gSlapper media paths cannot contain newlines")
    path.encode("utf-8")
    return path


def _gslapper_command(
        socket_path: Path,
        image_path: Path,
        cf: Config,
        monitor: str) -> list[str]:
    fill_options = {
        "fill": "fill",
        "stretch": "stretch",
        "fit": "panscan=1.0",
        "center": "original",
        # ponytail: gSlapper has no tile mode; use its native token if added.
        "tile": "fill",
    }
    options = ["loop", fill_options[cf.fill_option.lower()]]
    if not cf.mpvpaper_sound:
        options.append("no-audio")
    if cf.mpvpaper_options.strip():
        options.append(cf.mpvpaper_options.strip())

    return [
        "gslapper",
        "--fork",
        "--ipc-socket",
        str(socket_path),
        "-o",
        " ".join(options),
        monitor,
        _gslapper_media_path(image_path),
    ]


def _stop_gslapper_at(socket_path: Path) -> None:
    if not socket_path.exists():
        return
    try:
        _gslapper_ipc(socket_path, "stop")
    except (FileNotFoundError, ConnectionRefusedError):
        socket_path.unlink(missing_ok=True)
        return

    deadline = time.monotonic() + GSLAPPER_STARTUP_TIMEOUT
    while socket_path.exists():
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
                connection.settimeout(GSLAPPER_POLL_INTERVAL)
                connection.connect(str(socket_path))
        except (FileNotFoundError, ConnectionRefusedError):
            socket_path.unlink(missing_ok=True)
            return
        if time.monotonic() >= deadline:
            raise TimeoutError("gSlapper did not release its IPC socket after stop")
        time.sleep(GSLAPPER_POLL_INTERVAL)


def _launch_gslapper(
        socket_path: Path,
        image_path: Path,
        cf: Config,
        monitor: str) -> None:
    process = subprocess.Popen(
        _gslapper_command(socket_path, image_path, cf, monitor),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    deadline = time.monotonic() + GSLAPPER_STARTUP_TIMEOUT
    last_error = None
    # ponytail: fixed short polling keeps startup simple; calibrate the timeout
    # if manual testing finds hardware that needs more than three seconds.
    while time.monotonic() < deadline:
        exit_code = process.poll()
        if exit_code not in (None, 0):
            raise RuntimeError(f"gSlapper exited during startup with code {exit_code}")
        try:
            _gslapper_query(socket_path)
            return
        except (OSError, GSlapperIPCError) as error:
            last_error = error
            time.sleep(GSLAPPER_POLL_INTERVAL)
    raise TimeoutError(f"gSlapper IPC socket did not become ready: {last_error}")


def format_post_command(
        post_command: str,
        image_path: Path,
        monitor: str,
        fill_option: str,
        color: str) -> str:
    """Replace post_command tokens while treating dynamic values as shell literals."""
    replacements = {
        "$wallpaper": shlex.quote(str(image_path)),
        "$monitor": shlex.quote(monitor),
        "$fill": shlex.quote(fill_option),
        "$color": shlex.quote(color),
    }

    for token, value in replacements.items():
        post_command = post_command.replace(token, value)

    return post_command


def find_process_pid(command: str) -> Optional[int]:
    """Find the PID of the first process matching the command fragments.

    Uses 'pgrep -f' to match against the full command line in /proc.

    Returns the lowest matching PID as an int, or None if no match is found
    or if the subprocess encounters an error.
    """
    try:
        result = subprocess.run(
            ["pgrep", "-f", command],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        return None

    if result.returncode != 0:
        return None

    for line in result.stdout.splitlines():
        stripped = line.strip()
        if stripped:
            try:
                return int(stripped)
            except ValueError:
                # Malformed PID line — skip and try next.
                continue
    return None


def seek_and_destroy(process: str, monitor: str = "All"):
    """Find if a backend is already running somewhere and kill it"""

    # Kill all process instances if we want to set for all monitors:
    if monitor == "All":
        try:
            subprocess.check_output(["pgrep", "-f", f"{process}"], encoding='utf-8')
            subprocess.Popen(["killall", f"{process}"])
            time.sleep(0.1)
            print(f"Killed all previous instances of {process}")
        except subprocess.CalledProcessError:
            pass

    # Kill swww-daemon or awww-daemon if both are running at the same time, only works on all monitors
    elif process == "swww-daemon":
        try:
            subprocess.Popen(["swww kill"])
        except subprocess.CalledProcessError:
            pass
    elif process == "awww-daemon":
        try:
            subprocess.Popen(["awww kill"])
        except subprocess.CalledProcessError:
            pass

    # Otherwise, find PID of the process for certain monitor and kill it:
    else:
        if process == "mpvpaper":
            pid = find_process_pid(f"mpvpaper -f socket-{monitor}")
        elif process == "swaybg":
            pid = find_process_pid(f"swaybg -o {monitor}")
        elif process == "linux-wallpaperengine":
            pid = find_process_pid(f"linux-wallpaperengine --screen-root {monitor}")
        else:
            return
        if pid is None:
            # No previous process for this monitor — nothing to kill.
            return
        try:
            subprocess.run(['kill', '-9', str(pid)], check=True)
            print(f"Detected {process} on {monitor} and killed it")
        except Exception as e:
            pass


def notify_waypaper_issue(summary: str, body: str) -> None:
    """Show a desktop notification when a wallpaper backend fails."""
    try:
        subprocess.Popen(
            ["notify-send", summary, body],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except OSError:
        pass


def run_gslapper_action(action, *args) -> None:
    """Run a gSlapper UI action and report failures."""
    try:
        action(*args)
    except Exception as error:
        print(f"gSlapper action failed: {error}")
        notify_waypaper_issue("Waypaper gSlapper failed", str(error))


def change_with_swaybg(image_path: Path, cf: Config, monitor: str):
    """Change wallpaper with swaybg backend"""

    # Check pid of current swaybg process:
    if monitor == "All":
        pid = find_process_pid(f"swaybg")
    else:
        pid = find_process_pid(f"swaybg -o {monitor}")

    # Launch a new swaybg process:
    fill = cf.fill_option.lower()
    command = ["swaybg"]
    if monitor != "All":
        command.extend(["-o", monitor])
    command.extend(["-i", str(image_path)])
    command.extend(["-m", fill, "-c", cf.color])
    subprocess.Popen(command)

    # Kill previous swaybg process once new wallpaper is set:
    if pid:
        time.sleep(0.2)
        subprocess.run(['kill', '-9', str(pid)], check=True)


def change_with_mpvpaper(image_path: Path, cf: Config, monitor: str):
    """Change wallpaper with mpvpaper backend"""

    fill_types = {
            "fill": "panscan=1.0",
            "fit": "panscan=0.0",
            "center": "",
            "stretch": "--keepaspect=no",
            "tile": "",
            }
    fill = fill_types[cf.fill_option.lower()]

    # If mpvpaper is already active on given monitor, try to call that process in that socket:
    try:
        subprocess.check_output(["pgrep", "-f", f"socket-{monitor}"], encoding='utf-8')
        time.sleep(0.2)
        print(f"Detected running mpvpaper on {monitor}, now trying to call mpvpaper socket")
        if not is_socat_available():
            return
        subprocess.Popen(f"echo 'loadfile \"{image_path}\"' | socat - /tmp/mpv-socket-{monitor}", shell=True)

    # If mpvpaper is not running, create a new process in a new socket:
    except subprocess.CalledProcessError:
        print("Detected no running mpvpaper, starting new mpvpaper process")
        command = ["mpvpaper", "--fork"]
        if cf.mpvpaper_sound:
            command.extend(["-o", f"input-ipc-server=/tmp/mpv-socket-{monitor} {cf.mpvpaper_options} loop {fill} --background-color='{cf.color}'"])
        else:
            command.extend(["-o", f"input-ipc-server=/tmp/mpv-socket-{monitor} {cf.mpvpaper_options} loop {fill} --mute=yes --background-color='{cf.color}'"])

        # Specify the monitor:
        if monitor == "All":
            command.extend('*')
        else:
            command.extend([monitor])

        command.extend([image_path])

        print(f"{command=}")
        subprocess.Popen(command)


def change_with_gslapper(image_path: Path, cf: Config, monitor: str):
    """Change a Waypaper-managed gSlapper instance through IPC."""
    with _GSLAPPER_LIFECYCLE:
        outputs = _gslapper_outputs(monitor)
        targets = [(output, gslapper_socket_path(output)) for output in outputs]
        if monitor == "All":
            wanted = {target for _, target in targets}
            for stale in _gslapper_managed_sockets():
                if stale not in wanted:
                    _stop_gslapper_at(stale)

        for output, target in targets:
            if target.exists():
                try:
                    _gslapper_ipc(
                        target, f"change {_gslapper_media_path(image_path)}"
                    )
                    continue
                except (FileNotFoundError, ConnectionRefusedError):
                    target.unlink(missing_ok=True)
                except GSlapperIPCError as error:
                    if GSLAPPER_VIDEO_CHANGE_ERROR not in str(error):
                        raise
                    _stop_gslapper_at(target)

            _launch_gslapper(target, image_path, cf, output)


def restart_gslapper(image_path: Path, cf: Config, monitor: str) -> None:
    """Restart the selected managed instance to apply launch-only options."""
    with _GSLAPPER_LIFECYCLE:
        for output in _gslapper_outputs(monitor):
            target = gslapper_socket_path(output)
            if target.exists():
                _stop_gslapper_at(target)
                _launch_gslapper(target, image_path, cf, output)


def toggle_gslapper_pause(monitor: str) -> None:
    """Toggle playback on the selected managed instance."""
    with _GSLAPPER_LIFECYCLE:
        targets = [
            gslapper_socket_path(output) for output in _gslapper_outputs(monitor)
        ]
        if monitor == "All":
            targets = [target for target in targets if target.exists()]
        if not targets:
            raise RuntimeError("No Waypaper-managed gSlapper instances are running")
        states = [_gslapper_query(target)[0] for target in targets]
        command = "pause" if "playing" in states else "resume"
        # gSlapper nests pause commands: a paused instance that receives
        # another pause needs two resumes before it plays again, so only
        # command the targets that are not already in the desired state.
        desired = "paused" if command == "pause" else "playing"
        for target, state in zip(targets, states):
            if state != desired:
                _gslapper_ipc(target, command)


def stop_all_gslappers() -> None:
    """Stop all gSlapper instances owned by Waypaper."""
    with _GSLAPPER_LIFECYCLE:
        failures = []
        for socket_path in _gslapper_managed_sockets():
            try:
                _stop_gslapper_at(socket_path)
            except Exception as error:
                failures.append(f"{socket_path.name}: {error}")
        if failures:
            raise RuntimeError("; ".join(failures))


def change_with_swww(image_path: Path, cf: Config, monitor: str):
    """Change wallpaper with swww backend"""

    # Because swaybg and hyprpaper are known to conflict with swww, kill them:
    seek_and_destroy("swaybg")
    seek_and_destroy("hyprpaper")
    # if both swww and awww  are running they conflict
    seek_and_destroy("awww-daemon")

    fill_types = {
            "fill": "crop",
            "fit": "fit",
            "center": "no",
            "stretch": "crop",
            "tile": "no",
            }
    fill = fill_types[cf.fill_option.lower()]

    # Check if swww-daemon is already running. If not, launch it:
    try:
        subprocess.check_output(["pgrep", "swww-daemon"], encoding='utf-8')
    except subprocess.CalledProcessError:
        subprocess.Popen(["swww-daemon"])
        print("Launched swww-daemon")

    # Get rid of this in future when swww updates everywhere:
    version_p = subprocess.run(["swww", "-V"], capture_output=True, text=True)
    swww_version = [int(x) for x in version_p.stdout.strip().split("-")[0].split(" ")[1].split(".")]

    command = ["swww", "img", image_path]
    command.extend(["--resize", fill])
    if swww_version >= [0, 11, 0]:
        command.extend(["--fill-color", cf.color.lstrip("#")])
    else:
        command.extend(["--fill-color", cf.color])
    command.extend(["--filter", cf.swww_filter])
    command.extend(["--transition-type", cf.swww_transition_type])
    command.extend(["--transition-step", str(cf.swww_transition_step)])
    command.extend(["--transition-angle", str(cf.swww_transition_angle)])
    command.extend(["--transition-duration", str(cf.swww_transition_duration)])
    command.extend(["--transition-fps", str(cf.swww_transition_fps)])
    if monitor != "All":
        command.extend(["--outputs", monitor])
    subprocess.run(command)

def change_with_awww(image_path: Path, cf: Config, monitor: str):
    """Change wallpaper with awww backend"""

    # Because swaybg and hyprpaper are known to conflict with swww, kill them:
    seek_and_destroy("swaybg")
    seek_and_destroy("hyprpaper")
    # if both swww and awww are running they conflict
    seek_and_destroy("swww-daemon")

    fill_types = {
            "fill": "crop",
            "fit": "fit",
            "center": "no",
            "stretch": "crop",
            "tile": "no",
            }
    fill = fill_types[cf.fill_option.lower()]

    # Check if swww-daemon is already running. If not, launch it:
    try:
        subprocess.check_output(["pgrep", "awww-daemon"], encoding='utf-8')
    except subprocess.CalledProcessError:
        subprocess.Popen(["awww-daemon"])
        print("Launched awww-daemon")

    # Get rid of this in future when swww updates everywhere:
    version_p = subprocess.run(["awww", "-V"], capture_output=True, text=True)
    awww_version = [int(x) for x in version_p.stdout.strip().split("-")[0].split(" ")[1].split(".")]

    command = ["awww", "img", image_path]
    command.extend(["--resize", fill])
    if awww_version >= [0, 11, 0]:
        command.extend(["--fill-color", cf.color.lstrip("#")])
    else:
        command.extend(["--fill-color", cf.color])
    command.extend(["--filter", cf.swww_filter])
    command.extend(["--transition-type", cf.swww_transition_type])
    command.extend(["--transition-step", str(cf.swww_transition_step)])
    command.extend(["--transition-angle", str(cf.swww_transition_angle)])
    command.extend(["--transition-duration", str(cf.swww_transition_duration)])
    command.extend(["--transition-fps", str(cf.swww_transition_fps)])
    if monitor != "All":
        command.extend(["--outputs", monitor])
    subprocess.run(command)

def change_with_feh(image_path: Path, cf: Config, monitor: str):
    """Change wallpaper with feh backend"""

    fill_types = {
            "fill": "--bg-fill",
            "fit": "--bg-max",
            "center": "--bg-center",
            "stretch": "--bg-scale",
            "tile": "--bg-tile",
            }
    fill = fill_types[cf.fill_option.lower()]
    command = ["feh", fill, "--image-bg", cf.color]
    command.extend([str(image_path)])
    subprocess.Popen(command)

def change_with_xwallpaper(image_path: Path, cf: Config, monitor: str):
    """Change wallpaper with xwallpaper backend"""

    fill_types = {
            "fill": "--zoom",
            "fit": "--maximize",
            "center": "--center",
            "stretch": "--stretch",
            "tile": "--tile",
            }
    fill = fill_types[cf.fill_option.lower()]
    # Since xwallpaper doesn't accept 'All', but 'all'
    if monitor == "All":
        monitor = "all"
    command = ["xwallpaper", "--output", monitor, fill]
    command.extend([str(image_path)])
    subprocess.Popen(command)

def change_with_wallutils(image_path: Path, cf: Config, monitor: str):
    """Change wallpaper with wallutils backend"""
    fill_types = {
            "fill": "scale",
            "fit": "scale",
            "center": "center",
            "stretch": "stretch",
            "tile": "tile",
            }
    fill = fill_types[cf.fill_option.lower()]
    subprocess.Popen(["setwallpaper", "--mode", fill, image_path])


def change_with_finder(image_path: Path, cf: Config, monitor: str):
    """Change wallpaper on macOS"""
    script = f'tell application "System Events" to set picture of every desktop to "{image_path}"'
    subprocess.Popen(["osascript", "-e", script])


def change_with_hyprpaper(image_path: Path, cf: Config, monitor: str):
    """Change wallpaper with hyprpaper backend"""

    # Check if hyprpaper is already running, otherwise start it, and preload the wallpaper:
    try:
        subprocess.check_output(["pgrep", "hyprpaper"], encoding='utf-8')
    except subprocess.CalledProcessError:
        subprocess.Popen(["hyprpaper"])
        time.sleep(1)
    preload_command = ["hyprctl", "hyprpaper", "preload", image_path]

    # Decide which monitors are affected:
    if monitor == "All":
        monitors = get_monitor_names_with_hyprctl()
    else:
        monitors: list = [monitor]

    # Change the wallpaper one by one for each affected monitor:
    for m in monitors:
        wallpaper_command = ["hyprctl", "hyprpaper", "wallpaper", f"{m},{image_path}"]
        unload_command = ["hyprctl", "hyprpaper", "unload", "all"]
        result: str = ""
        retry_counter: int = 0

        # Since sometimes hyprpaper fails to change the wallpaper, we try until success:
        while result != "ok" and retry_counter < 10:
            try:
                subprocess.check_output(unload_command, encoding="utf-8").strip()
                subprocess.check_output(preload_command, encoding="utf-8").strip()
            except Exception:
                pass
                # Preloading images with Hyprpaper is currently unavailable due to https://github.com/hyprwm/hyprpaper/pull/288
                # It has not yet been determined if this will be reimplemented - https://github.com/hyprwm/hyprpaper/issues/292
            try:
                wpresult = subprocess.run(
                    wallpaper_command,
                    encoding="utf-8",
                    capture_output=True,
                    text=True,
                    check=True
                )
                if wpresult.returncode == 0 or wpresult.stdout.strip() == "ok":
                    result = "ok"
                time.sleep(0.1)
            except Exception:
                retry_counter += 1

def change_with_linux_wallpaperengine(image_path: Path, cf: Config, monitor: str):
    seek_and_destroy("linux-wallpaperengine", monitor)

    if cf.fill_option.lower() in LINUX_WALLPAPERENGINE_FILL_OPTIONS:
        fill = cf.fill_option.lower()
    else:
        fill = LINUX_WALLPAPERENGINE_FILL_OPTIONS[3]

    command = ["linux-wallpaperengine"]

    if monitor == "All":
        for monitor in get_plugged_monitors():
            if monitor is not None:
                command.extend(["--screen-root", monitor])
    else:
        command.extend(["--screen-root", monitor])

    if cf.linux_wallpaperengine_silent:
        command.append("--silent")
    if cf.linux_wallpaperengine_noautomute:
        command.append("--noautomute")
    if cf.linux_wallpaperengine_no_audio_processing:
        command.append("--no-audio-processing")
    if cf.linux_wallpaperengine_no_fullscreen_pause:
        command.append("--no-fullscreen-pause")
    if cf.linux_wallpaperengine_fullscreen_pause_only_active:
        command.append("--fullscreen-pause-only-active")
    if cf.linux_wallpaperengine_disable_particles:
        command.append("--disable-particles")
    if cf.linux_wallpaperengine_disable_mouse:
        command.append("--disable-mouse")
    if cf.linux_wallpaperengine_disable_parallax:
        command.append("--disable-parallax")
    if cf.linux_wallpaperengine_clamp != LINUX_WALLPAPERENGINE_CLAMP[0]:
        command.extend(["--clamp", cf.linux_wallpaperengine_clamp])

    command.extend(["--volume", str(cf.linux_wallpaperengine_volume)])
    command.extend(["--fps", str(cf.linux_wallpaperengine_fps)])
    command.extend(["--scaling", fill])

    command.append(str(image_path.parent))
    print(f"{command=}")
    process = subprocess.Popen(
        command,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    time.sleep(0.5)
    exit_code = process.poll()
    if exit_code is not None:
        message = f"linux-wallpaperengine exited immediately with code {exit_code}."
        print(message)
        notify_waypaper_issue("Waypaper launch failed", message)

def change_wallpaper(image_path: Path, cf: Config, monitor: str):
    """Run system commands to change the wallpaper depending on the backend"""

    print(f"Selected file: {image_path}")

    try:
        if cf.backend == "swaybg":
            change_with_swaybg(image_path, cf, monitor)
        if cf.backend == "mpvpaper":
            change_with_mpvpaper(image_path, cf, monitor)
        if cf.backend == "swww":
            change_with_swww(image_path, cf, monitor)
        if cf.backend == "awww":
            change_with_awww(image_path, cf, monitor)
        if cf.backend == "feh":
            change_with_feh(image_path, cf, monitor)
        if cf.backend == "xwallpaper":
            change_with_xwallpaper(image_path, cf, monitor)
        if cf.backend == "wallutils":
            change_with_wallutils(image_path, cf, monitor)
        if cf.backend == "hyprpaper":
            change_with_hyprpaper(image_path, cf, monitor)
        if cf.backend == "gslapper":
            change_with_gslapper(image_path, cf, monitor)
        if cf.backend == "macos":
            change_with_finder(image_path, cf, monitor)
        if cf.backend == "linux-wallpaperengine":
            change_with_linux_wallpaperengine(image_path, cf, monitor)
        if cf.backend != "none":
            filename = Path(image_path).resolve().name
            print(f"Sent {cf.backend} command to set {filename} on {monitor} display\n")

        # Run a post command:
        if cf.post_command and cf.use_post_command:
            post_command = format_post_command(
                cf.post_command,
                image_path,
                monitor,
                cf.fill_option,
                cf.color,
            )
            subprocess.Popen(post_command, shell=True)
            print(f'Executed "{post_command}" post-command\n')

    except Exception as e:
        print(f"Error occured while changing wallpaper: \n{e}")
        if cf.backend == "gslapper":
            notify_waypaper_issue("Waypaper gSlapper failed", str(e))
