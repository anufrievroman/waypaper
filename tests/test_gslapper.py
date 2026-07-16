import os
import socket
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

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
        with patch.dict(os.environ, {}, clear=True):
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


if __name__ == "__main__":
    unittest.main()
