import shlex
import unittest
from pathlib import Path

from waypaper.changer import format_post_command


class PostCommandTests(unittest.TestCase):
    def test_format_post_command_quotes_dynamic_tokens(self):
        image_path = Path("/tmp/wallpapers/bg; unexpected command.png")
        monitor = "HDMI-A-1; unexpected command"
        fill_option = "fill && unexpected command"
        color = "#112233; unexpected command"

        command = format_post_command(
            "notify-send $wallpaper $monitor $fill $color && echo done",
            image_path,
            monitor,
            fill_option,
            color,
        )

        self.assertEqual(
            command,
            "notify-send "
            f"{shlex.quote(str(image_path))} "
            f"{shlex.quote(monitor)} "
            f"{shlex.quote(fill_option)} "
            f"{shlex.quote(color)} "
            "&& echo done",
        )

    def test_format_post_command_handles_apostrophes_in_paths(self):
        command = format_post_command(
            "printf %s $wallpaper",
            Path("/tmp/Don't Look Down.jpg"),
            "All",
            "fill",
            "#000000",
        )

        self.assertIn("'\"'\"'", command)
        self.assertTrue(command.startswith("printf %s "))


if __name__ == "__main__":
    unittest.main()
