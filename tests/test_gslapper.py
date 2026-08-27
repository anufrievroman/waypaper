import os
import socket
import tempfile
import threading
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, call, patch

from waypaper import changer


class GSlapperIPCTests(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp_dir.cleanup)
        runtime_patch = patch.dict(
            os.environ, {"XDG_RUNTIME_DIR": self.tmp_dir.name}
        )
        runtime_patch.start()
        self.addCleanup(runtime_patch.stop)

    def test_socket_paths_are_owned_and_output_specific(self):
        first = changer.gslapper_socket_path("DP-1")
        second = changer.gslapper_socket_path("HDMI-A-1")

        self.assertEqual(first.parent, Path(self.tmp_dir.name) / "waypaper")
        self.assertNotEqual(first, second)
        self.assertEqual(first.suffix, ".sock")
        self.assertLess(len(str(first).encode()), 108)

    def test_missing_runtime_directory_is_reported(self):
        with patch.dict(os.environ, {"XDG_RUNTIME_DIR": ""}):
            with self.assertRaisesRegex(RuntimeError, "XDG_RUNTIME_DIR"):
                changer.gslapper_socket_path("DP-1")

    def serve_once(self, socket_path: Path, response: bytes):
        ready = threading.Event()
        received = []

        def server():
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as listener:
                listener.bind(str(socket_path))
                listener.listen(1)
                listener.settimeout(1)
                ready.set()
                connection, _ = listener.accept()
                with connection:
                    received.append(connection.recv(4096))
                    connection.sendall(response)

        thread = threading.Thread(target=server, daemon=True)
        thread.start()
        self.assertTrue(ready.wait(1))
        return received, thread

    def test_ipc_sends_one_line_and_reads_one_response(self):
        socket_path = Path(self.tmp_dir.name) / "ipc.sock"
        received, thread = self.serve_once(socket_path, b"OK\n")

        self.assertEqual(changer._gslapper_ipc(socket_path, "pause"), "OK")
        thread.join(1)
        self.assertEqual(received, [b"pause\n"])

    def test_ipc_raises_protocol_error(self):
        socket_path = Path(self.tmp_dir.name) / "ipc.sock"
        _, thread = self.serve_once(socket_path, b"ERROR: no pipeline\n")

        with self.assertRaisesRegex(changer.GSlapperIPCError, "no pipeline"):
            changer._gslapper_ipc(socket_path, "query")
        thread.join(1)

    def test_query_parses_state_and_preserves_spaces(self):
        socket_path = Path(self.tmp_dir.name) / "ipc.sock"
        _, thread = self.serve_once(
            socket_path,
            b"STATUS: paused video /wallpapers/space name.mp4\n",
        )

        self.assertEqual(
            changer._gslapper_query(socket_path),
            ("paused", "video", Path("/wallpapers/space name.mp4")),
        )
        thread.join(1)

    def test_ipc_rejects_newlines(self):
        with self.assertRaisesRegex(ValueError, "newlines"):
            changer._gslapper_ipc(
                Path("/tmp/not-used.sock"), "change bad\npath"
            )

    def make_config(self, **changes):
        values = {
            "fill_option": "fill",
            "mpvpaper_sound": False,
            "mpvpaper_options": "",
        }
        values.update(changes)
        return SimpleNamespace(**values)

    def test_launch_command_uses_current_gslapper_options(self):
        command = changer._gslapper_command(
            Path("/tmp/ipc.sock"),
            Path("/wallpapers/a b.mp4"),
            self.make_config(mpvpaper_options="queue-size=4"),
            "DP-1",
        )

        self.assertEqual(
            command,
            [
                "gslapper",
                "--fork",
                "--ipc-socket",
                "/tmp/ipc.sock",
                "-o",
                "loop fill no-audio queue-size=4",
                "DP-1",
                "/wallpapers/a b.mp4",
            ],
        )

    def test_launch_command_rejects_newlines_in_media_path(self):
        with self.assertRaisesRegex(ValueError, "newlines"):
            changer._gslapper_command(
                Path("/tmp/ipc.sock"),
                Path("/wallpapers/bad\nname.jpg"),
                self.make_config(),
                "DP-1",
            )

    def test_change_reuses_live_target(self):
        target = changer.gslapper_socket_path("DP-1")
        target.touch()
        with patch(
            "waypaper.changer._gslapper_ipc", return_value="OK"
        ) as ipc, patch("waypaper.changer._launch_gslapper") as launch:
            changer.change_with_gslapper(
                Path("/wallpapers/new.jpg"), self.make_config(), "DP-1"
            )

        ipc.assert_called_once_with(target, "change /wallpapers/new.jpg")
        launch.assert_not_called()

    def test_all_creates_independent_instances_for_later_output_changes(self):
        monitors = [SimpleNamespace(name="DP-1"), SimpleNamespace(name="DP-3")]

        def launch(socket_path, image_path, cf, monitor):
            socket_path.touch()

        cf = self.make_config()
        with patch(
            "waypaper.changer.screeninfo.get_monitors", return_value=monitors
        ), patch(
            "waypaper.changer._launch_gslapper", side_effect=launch
        ) as launch_gslapper, patch(
            "waypaper.changer._gslapper_ipc", return_value="OK"
        ) as ipc:
            changer.change_with_gslapper(
                Path("/wallpapers/all.jpg"), cf, "All"
            )
            changer.change_with_gslapper(
                Path("/wallpapers/dp-1.jpg"), cf, "DP-1"
            )

        self.assertEqual(
            launch_gslapper.call_args_list,
            [
                call(
                    changer.gslapper_socket_path("DP-1"),
                    Path("/wallpapers/all.jpg"),
                    cf,
                    "DP-1",
                ),
                call(
                    changer.gslapper_socket_path("DP-3"),
                    Path("/wallpapers/all.jpg"),
                    cf,
                    "DP-3",
                ),
            ],
        )
        ipc.assert_called_once_with(
            changer.gslapper_socket_path("DP-1"),
            "change /wallpapers/dp-1.jpg",
        )
        self.assertFalse(changer.gslapper_socket_path("All").exists())

    def test_video_change_error_restarts_only_the_target(self):
        target = changer.gslapper_socket_path("DP-1")
        target.touch()
        error = changer.GSlapperIPCError(
            "cannot update path (use --auto-stop for video changes)"
        )
        with patch(
            "waypaper.changer._gslapper_ipc", side_effect=error
        ), patch("waypaper.changer._stop_gslapper_at") as stop, patch(
            "waypaper.changer._launch_gslapper"
        ) as launch:
            cf = self.make_config()
            image = Path("/wallpapers/new.mp4")
            changer.change_with_gslapper(image, cf, "DP-1")

        stop.assert_called_once_with(target)
        launch.assert_called_once_with(target, image, cf, "DP-1")

    def test_unrelated_protocol_error_does_not_restart(self):
        target = changer.gslapper_socket_path("DP-1")
        target.touch()
        with patch(
            "waypaper.changer._gslapper_ipc",
            side_effect=changer.GSlapperIPCError("file not accessible"),
        ), patch("waypaper.changer._launch_gslapper") as launch:
            with self.assertRaisesRegex(
                changer.GSlapperIPCError, "file not accessible"
            ):
                changer.change_with_gslapper(
                    Path("/wallpapers/missing.jpg"),
                    self.make_config(),
                    "DP-1",
                )

        launch.assert_not_called()

    def test_stale_target_is_removed_before_launch(self):
        target = changer.gslapper_socket_path("DP-1")
        target.touch()
        with patch(
            "waypaper.changer._gslapper_ipc",
            side_effect=ConnectionRefusedError,
        ), patch("waypaper.changer._launch_gslapper") as launch:
            cf = self.make_config()
            image = Path("/wallpapers/new.jpg")
            changer.change_with_gslapper(image, cf, "DP-1")

        self.assertFalse(target.exists())
        launch.assert_called_once_with(target, image, cf, "DP-1")

    def test_pause_toggles_from_reported_state(self):
        target = changer.gslapper_socket_path("DP-1")
        with patch(
            "waypaper.changer._gslapper_query",
            return_value=("paused", "video", Path("/wallpapers/a.mp4")),
        ), patch("waypaper.changer._gslapper_ipc", return_value="OK") as ipc:
            changer.toggle_gslapper_pause("DP-1")

        ipc.assert_called_once_with(target, "resume")

    def test_pause_all_skips_targets_already_in_the_desired_state(self):
        # gSlapper nests pause commands: pausing an already-paused instance
        # requires two resumes before it plays again, so convergence must not
        # send pause to a target that is already paused.
        monitors = [SimpleNamespace(name="DP-1"), SimpleNamespace(name="DP-3")]
        targets = [changer.gslapper_socket_path(m.name) for m in monitors]
        for target in targets:
            target.touch()

        with patch(
            "waypaper.changer.screeninfo.get_monitors", return_value=monitors
        ), patch(
            "waypaper.changer._gslapper_query",
            side_effect=[
                ("playing", "video", Path("/wallpapers/a.mp4")),
                ("paused", "video", Path("/wallpapers/b.mp4")),
            ],
        ), patch(
            "waypaper.changer._gslapper_ipc", return_value="OK"
        ) as ipc:
            changer.toggle_gslapper_pause("All")

        self.assertEqual(ipc.call_args_list, [call(targets[0], "pause")])

    def test_resume_all_resumes_every_paused_output(self):
        monitors = [SimpleNamespace(name="DP-1"), SimpleNamespace(name="DP-3")]
        targets = [changer.gslapper_socket_path(m.name) for m in monitors]
        for target in targets:
            target.touch()

        with patch(
            "waypaper.changer.screeninfo.get_monitors", return_value=monitors
        ), patch(
            "waypaper.changer._gslapper_query",
            side_effect=[
                ("paused", "video", Path("/wallpapers/a.mp4")),
                ("paused", "video", Path("/wallpapers/b.mp4")),
            ],
        ), patch(
            "waypaper.changer._gslapper_ipc", return_value="OK"
        ) as ipc:
            changer.toggle_gslapper_pause("All")

        self.assertCountEqual(
            ipc.call_args_list,
            [call(target, "resume") for target in targets],
        )

    def test_stop_all_only_visits_managed_sockets(self):
        first = changer.gslapper_socket_path("DP-1")
        second = changer.gslapper_socket_path("HDMI-A-1")
        first.touch()
        second.touch()
        with patch("waypaper.changer._stop_gslapper_at") as stop:
            changer.stop_all_gslappers()

        self.assertCountEqual(stop.call_args_list, [call(first), call(second)])

    def test_sound_restart_does_nothing_without_a_managed_target(self):
        with patch("waypaper.changer._launch_gslapper") as launch:
            changer.restart_gslapper(
                Path("/wallpapers/a.mp4"), self.make_config(), "DP-1"
            )

        launch.assert_not_called()

    def test_sound_restart_all_restarts_each_managed_output(self):
        monitors = [SimpleNamespace(name="DP-1"), SimpleNamespace(name="DP-3")]
        targets = [changer.gslapper_socket_path(m.name) for m in monitors]
        for target in targets:
            target.touch()

        cf = self.make_config()
        image = Path("/wallpapers/a.mp4")
        with patch(
            "waypaper.changer.screeninfo.get_monitors", return_value=monitors
        ), patch(
            "waypaper.changer._stop_gslapper_at"
        ) as stop, patch(
            "waypaper.changer._launch_gslapper"
        ) as launch:
            changer.restart_gslapper(image, cf, "All")

        self.assertCountEqual(
            stop.call_args_list,
            [call(target) for target in targets],
        )
        self.assertCountEqual(
            launch.call_args_list,
            [
                call(target, image, cf, monitor.name)
                for target, monitor in zip(targets, monitors)
            ],
        )

    def test_launch_waits_until_ipc_is_ready(self):
        process = MagicMock()
        process.poll.return_value = None
        socket_path = changer.gslapper_socket_path("DP-1")
        cf = self.make_config()
        image = Path("/wallpapers/a.jpg")
        with patch(
            "waypaper.changer.subprocess.Popen", return_value=process
        ) as popen, patch(
            "waypaper.changer._gslapper_query",
            return_value=("playing", "image", image),
        ):
            changer._launch_gslapper(socket_path, image, cf, "DP-1")

        popen.assert_called_once_with(
            changer._gslapper_command(socket_path, image, cf, "DP-1"),
            stdin=changer.subprocess.DEVNULL,
            stdout=changer.subprocess.DEVNULL,
            stderr=changer.subprocess.DEVNULL,
            start_new_session=True,
        )

    def test_launch_reports_immediate_process_failure(self):
        process = MagicMock()
        process.poll.return_value = 7
        with patch(
            "waypaper.changer.subprocess.Popen", return_value=process
        ), self.assertRaisesRegex(RuntimeError, "code 7"):
            changer._launch_gslapper(
                changer.gslapper_socket_path("DP-1"),
                Path("/wallpapers/a.jpg"),
                self.make_config(),
                "DP-1",
            )

    def test_stop_all_attempts_every_managed_socket_before_reporting(self):
        first = changer.gslapper_socket_path("DP-1")
        second = changer.gslapper_socket_path("HDMI-A-1")
        first.touch()
        second.touch()
        with patch(
            "waypaper.changer._stop_gslapper_at",
            side_effect=[RuntimeError("stuck"), None],
        ) as stop, self.assertRaisesRegex(RuntimeError, "stuck"):
            changer.stop_all_gslappers()

        self.assertCountEqual(stop.call_args_list, [call(first), call(second)])

    def test_stop_waits_for_the_server_to_release_its_socket(self):
        socket_path = changer.gslapper_socket_path("DP-1")
        ready = threading.Event()
        received = []

        def server():
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as listener:
                listener.bind(str(socket_path))
                listener.listen(1)
                ready.set()
                connection, _ = listener.accept()
                with connection:
                    received.append(connection.recv(4096))
                    connection.sendall(b"OK\n")
            socket_path.unlink()

        thread = threading.Thread(target=server, daemon=True)
        thread.start()
        self.assertTrue(ready.wait(1))

        changer._stop_gslapper_at(socket_path)

        thread.join(1)
        self.assertEqual(received, [b"stop\n"])
        self.assertFalse(socket_path.exists())

    def test_background_action_errors_notify(self):
        action = MagicMock(side_effect=RuntimeError("socket timed out"))
        with patch("waypaper.changer.notify_waypaper_issue") as notify, patch(
            "builtins.print"
        ):
            changer.run_gslapper_action(action, "DP-1")

        notify.assert_called_once_with(
            "Waypaper gSlapper failed", "socket timed out"
        )

    def test_wallpaper_change_error_notifies_and_skips_post_command(self):
        cf = SimpleNamespace(
            backend="gslapper",
            post_command="echo should-not-run",
            use_post_command=True,
            fill_option="fill",
            color="#ffffff",
        )
        with patch(
            "waypaper.changer.change_with_gslapper",
            side_effect=RuntimeError("gSlapper failed"),
        ), patch("waypaper.changer.notify_waypaper_issue") as notify, patch(
            "waypaper.changer.subprocess.Popen"
        ) as popen, patch("builtins.print"):
            changer.change_wallpaper(Path("/wallpapers/a.jpg"), cf, "DP-1")

        notify.assert_called_once_with(
            "Waypaper gSlapper failed", "gSlapper failed"
        )
        popen.assert_not_called()


class GSlapperUITests(unittest.TestCase):
    def test_gslapper_displays_existing_pause_control(self):
        from waypaper.app import App

        window = SimpleNamespace(
            cf=SimpleNamespace(backend="gslapper"),
            txt=SimpleNamespace(msg_stop="Stop all", tip_mpv_stop="mpv stop"),
            options_box=MagicMock(),
            mpv_stop_button=MagicMock(),
            mpv_pause_button=MagicMock(),
            mpv_sound_toggle=MagicMock(),
        )

        App.mpv_options_display(window)

        window.mpv_stop_button.set_tooltip_text.assert_called_with("Stop all")
        self.assertIn(
            call(window.mpv_pause_button, False, False, 0),
            window.options_box.pack_end.call_args_list,
        )

    def test_gslapper_pause_and_stop_schedule_managed_actions(self):
        from waypaper import app

        window = SimpleNamespace(
            cf=SimpleNamespace(backend="gslapper", selected_monitor="DP-1")
        )
        with patch("waypaper.app.threading.Thread") as thread, patch(
            "waypaper.app.subprocess.Popen"
        ):
            app.App.on_mpv_pause_button_clicked(window, None)
            app.App.on_mpv_stop_button_clicked(window, None)

        self.assertEqual(thread.call_count, 2)
        self.assertIs(
            thread.call_args_list[0].kwargs["target"],
            changer.run_gslapper_action,
        )
        self.assertEqual(
            thread.call_args_list[0].kwargs["args"],
            (changer.toggle_gslapper_pause, "DP-1"),
        )
        self.assertIs(
            thread.call_args_list[1].kwargs["target"],
            changer.run_gslapper_action,
        )
        self.assertEqual(
            thread.call_args_list[1].kwargs["args"],
            (changer.stop_all_gslappers,),
        )

    def test_gslapper_sound_schedules_selected_instance_restart(self):
        from waypaper import app

        toggle = MagicMock()
        toggle.get_active.return_value = True
        config = SimpleNamespace(
            backend="gslapper",
            selected_monitor="DP-1",
            selected_wallpaper=Path("/wallpapers/a.mp4"),
            mpvpaper_sound=False,
        )
        window = SimpleNamespace(cf=config)
        with patch("waypaper.app.threading.Thread") as thread, patch(
            "waypaper.changer.change_with_gslapper"
        ):
            app.App.on_mpv_sound_toggled(window, toggle)

        self.assertTrue(config.mpvpaper_sound)
        self.assertIs(
            thread.call_args.kwargs["target"], changer.run_gslapper_action
        )
        self.assertEqual(
            thread.call_args.kwargs["args"],
            (
                changer.restart_gslapper,
                Path("/wallpapers/a.mp4"),
                config,
                "DP-1",
            ),
        )


if __name__ == "__main__":
    unittest.main()
