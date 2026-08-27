import json
import tempfile
import unittest
from pathlib import Path

from waypaper.wallpaperengine import (
    get_wallpaperengine_entry_path,
    get_wallpaperengine_project,
    get_wallpaperengine_project_dir,
)


class WallpaperEngineHelpersTest(unittest.TestCase):
    def test_project_dir_accepts_project_directory_or_child_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            child_path = project_dir / "preview.jpg"

            self.assertEqual(get_wallpaperengine_project_dir(project_dir), project_dir)
            self.assertEqual(get_wallpaperengine_project_dir(child_path), project_dir)

    def test_project_metadata_normalizes_type_and_title(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            (project_dir / "project.json").write_text(json.dumps({"type": " Video "}))

            project = get_wallpaperengine_project(project_dir)

            self.assertEqual(project["type"], "video")
            self.assertEqual(project["title"], project_dir.name)

    def test_project_metadata_falls_back_to_directory_name_on_missing_title(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            (project_dir / "project.json").write_text(json.dumps({"type": "scene"}))

            project = get_wallpaperengine_project(project_dir)

            self.assertEqual(project["type"], "scene")
            self.assertEqual(project["title"], project_dir.name)

    def test_project_metadata_marks_unknown_type(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            (project_dir / "project.json").write_text(json.dumps({"type": "preset", "title": "Visualizer"}))

            project = get_wallpaperengine_project(project_dir)

            self.assertEqual(project["type"], "preset")
            self.assertEqual(project["title"], "Visualizer")

    def test_entry_path_returns_existing_project_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            entry_path = project_dir / "wallpaper.mp4"
            entry_path.touch()
            (project_dir / "project.json").write_text(json.dumps({"type": "video", "file": entry_path.name}))

            self.assertEqual(get_wallpaperengine_entry_path(project_dir / "preview.jpg"), entry_path)

    def test_entry_path_returns_none_when_file_field_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            (project_dir / "project.json").write_text(json.dumps({"type": "scene"}))

            self.assertIsNone(get_wallpaperengine_entry_path(project_dir / "preview.jpg"))


if __name__ == "__main__":
    unittest.main()