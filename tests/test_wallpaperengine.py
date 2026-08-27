import json
import tempfile
import unittest
from pathlib import Path

from waypaper.common import get_image_name
from waypaper.wallpaperengine import (
    get_wallpaperengine_image_name,
    get_wallpaperengine_preview,
    get_wallpaperengine_project,
    get_wallpaperengine_project_dir,
)


class WallpaperEngineMetadataTest(unittest.TestCase):
    def test_project_dir_accepts_directory_or_child_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            preview_path = project_dir / "preview.jpg"

            self.assertEqual(get_wallpaperengine_project_dir(project_dir), project_dir)
            self.assertEqual(get_wallpaperengine_project_dir(preview_path), project_dir)

    def test_project_metadata_normalizes_type_and_title(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            (project_dir / "project.json").write_text(json.dumps({"type": " Video "}), encoding="utf-8")

            project = get_wallpaperengine_project(project_dir / "preview.jpg")

            self.assertEqual(project["type"], "video")
            self.assertEqual(project["title"], project_dir.name)

    def test_image_name_labels_known_project_types(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            (project_dir / "project.json").write_text(json.dumps({"type": "scene", "title": "Neon Driver"}), encoding="utf-8")

            self.assertEqual(get_wallpaperengine_image_name(project_dir / "preview.jpg"), "Neon Driver [scene]")

    def test_image_name_marks_unknown_project_types(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            (project_dir / "project.json").write_text(json.dumps({"type": "preset", "title": "Visualizer"}), encoding="utf-8")

            self.assertEqual(get_wallpaperengine_image_name(project_dir / "preview.jpg"), "Visualizer [preset ?]")

    def test_image_name_falls_back_to_directory_name_on_bad_metadata(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            (project_dir / "project.json").write_text("{", encoding="utf-8")

            self.assertEqual(get_wallpaperengine_image_name(project_dir / "preview.jpg"), project_dir.name)

    def test_preview_search_returns_preview_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            nested_dir = project_dir / "nested"
            nested_dir.mkdir()
            preview_path = nested_dir / "preview.jpg"
            preview_path.touch()
            (nested_dir / "not-preview.jpg").touch()

            self.assertEqual(get_wallpaperengine_preview(project_dir), [str(preview_path)])


class GetImageNameTest(unittest.TestCase):
    """Verify common.get_image_name surfaces WE project.json title [type]."""

    def test_get_image_name_uses_project_json_title_for_workshop_paths(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            base_folder = Path(tmpdir) / "Wallpapers"
            project_dir = base_folder / "431960" / "12345"
            project_dir.mkdir(parents=True)
            preview = project_dir / "preview.jpg"
            preview.touch()
            (project_dir / "project.json").write_text(
                json.dumps({"type": "scene", "title": "Neon Driver"}),
                encoding="utf-8",
            )

            name = get_image_name(str(preview), [base_folder], include_path=False)

            self.assertEqual(name, "Neon Driver [scene]")

    def test_get_image_name_falls_back_to_path_name_when_project_json_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            base_folder = Path(tmpdir) / "Wallpapers"
            project_dir = base_folder / "431960" / "12345"
            project_dir.mkdir(parents=True)
            preview = project_dir / "preview.jpg"
            preview.touch()
            # no project.json in the parent

            name = get_image_name(str(preview), [base_folder], include_path=False)

            self.assertEqual(name, "preview.jpg")

    def test_get_image_name_falls_back_to_path_name_when_project_json_malformed(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            base_folder = Path(tmpdir) / "Wallpapers"
            project_dir = base_folder / "431960" / "12345"
            project_dir.mkdir(parents=True)
            preview = project_dir / "preview.jpg"
            preview.touch()
            (project_dir / "project.json").write_text("{", encoding="utf-8")

            name = get_image_name(str(preview), [base_folder], include_path=False)

            self.assertEqual(name, "preview.jpg")


if __name__ == "__main__":
    unittest.main()