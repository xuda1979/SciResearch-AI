import unittest
import tempfile
import shutil
import re
from pathlib import Path

from packages.sciresearch_paper.project_fs import ProjectFS
from packages.sciresearch_paper.paper_writer import PaperWriter, DEFAULT_TEX

class TestPaperWriter(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.projects_dir = Path(self.test_dir)
        self.project_name = "test_project"
        self.fs = ProjectFS(self.project_name, projects_dir=self.projects_dir)
        self.writer = PaperWriter(self.fs)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_initial_draft_creation(self):
        self.assertTrue(self.writer.draft_path.exists())
        content = self.writer.draft_path.read_text(encoding="utf-8")
        self.assertEqual(content, DEFAULT_TEX)

    def test_autosave(self):
        new_content = "This is the new content for the draft."
        snap_path = self.writer.autosave(new_content)

        # Check draft content
        draft_content = self.writer.draft_path.read_text(encoding="utf-8")
        self.assertEqual(draft_content, new_content)

        # Check checkpoint file
        self.assertTrue(snap_path.exists())
        self.assertEqual(snap_path.parent, self.fs.rev_dir)

        # Check checkpoint content
        snap_content = snap_path.read_text(encoding="utf-8")
        self.assertEqual(snap_content, new_content)

        # Check checkpoint naming
        match = re.match(r"draft-\d{8}-\d{6}-\d{3}\.tex", snap_path.name)
        self.assertIsNotNone(match)

if __name__ == "__main__":
    unittest.main()
