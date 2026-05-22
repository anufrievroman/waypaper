import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from waypaper.wallpaperengine import (
    get_wallpaperengine_image_name,
    get_wallpaperengine_project,
    resolve_linux_wallpaperengine_assets_dir,
    resolve_linux_wallpaperengine_binary,
)


class WallpaperEngineTests(unittest.TestCase):
    def test_project_metadata_is_normalized_from_preview_path(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_dir = Path(tmp_dir) / "123"
            project_dir.mkdir()
            preview_path = project_dir / "preview.jpg"
            preview_path.write_text("preview", encoding="utf-8")
            (project_dir / "project.json").write_text('{"type": " Scene ", "title": "Test Scene"}', encoding="utf-8")

            metadata = get_wallpaperengine_project(preview_path)
            image_name = get_wallpaperengine_image_name(preview_path)

        self.assertEqual(metadata["type"], "scene")
        self.assertEqual(metadata["title"], "Test Scene")
        self.assertEqual(image_name, "Test Scene")

    def test_project_metadata_falls_back_to_directory_name(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_dir = Path(tmp_dir) / "fallback-title"
            project_dir.mkdir()
            (project_dir / "project.json").write_text("{}", encoding="utf-8")

            metadata = get_wallpaperengine_project(project_dir)

        self.assertEqual(metadata["type"], "unknown")
        self.assertEqual(metadata["title"], "fallback-title")

    def test_resolve_binary_prefers_configured_path(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            binary_path = Path(tmp_dir) / "linux-wallpaperengine"
            config = SimpleNamespace(linux_wallpaperengine_binary=str(binary_path))

            self.assertEqual(resolve_linux_wallpaperengine_binary(config), str(binary_path))

    def test_resolve_binary_defaults_to_command_name(self):
        config = SimpleNamespace(linux_wallpaperengine_binary="")

        self.assertEqual(resolve_linux_wallpaperengine_binary(config), "linux-wallpaperengine")

    def test_resolve_assets_returns_configured_directory(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            assets_dir = Path(tmp_dir) / "assets"
            assets_dir.mkdir()
            config = SimpleNamespace(linux_wallpaperengine_assets_dir=str(assets_dir))

            self.assertEqual(resolve_linux_wallpaperengine_assets_dir(config), assets_dir)

    def test_resolve_assets_returns_none_without_configured_directory(self):
        config = SimpleNamespace(linux_wallpaperengine_assets_dir="")

        self.assertIsNone(resolve_linux_wallpaperengine_assets_dir(config))


if __name__ == "__main__":
    unittest.main()
