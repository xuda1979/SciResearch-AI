import shutil
import tempfile
import unittest
from pathlib import Path

from packages.sciresearch_paper.project_fs import ProjectFS


class TestProjectFS(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.projects_dir = Path(self.test_dir)
        self.project_name = "test_project"
        self.fs = ProjectFS(self.project_name, projects_dir=self.projects_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_project_creation(self):
        self.assertTrue(self.fs.root.exists())
        self.assertEqual(self.fs.root, self.projects_dir / self.project_name)
        self.assertTrue(self.fs.paper_dir.exists())
        self.assertTrue(self.fs.fig_dir.exists())
        self.assertTrue(self.fs.code_dir.exists())
        self.assertTrue(self.fs.data_dir.exists())
        self.assertTrue(self.fs.notes_dir.exists())
        self.assertTrue(self.fs.logs_dir.exists())
        self.assertTrue(self.fs.rev_dir.exists())

    def test_write_and_read_file(self):
        file_path = "notes/test_note.txt"
        content = "This is a test note."
        self.fs.write(file_path, content)

        read_content = self.fs.read(file_path)
        self.assertEqual(content, read_content)

    def test_list_files(self):
        self.fs.write("code/script1.py", "print('hello')")
        self.fs.write("code/script2.py", "print('world')")

        files = self.fs.list_files("code")
        self.assertIn("script1.py", files)
        self.assertIn("script2.py", files)

    def test_read_nonexistent_file(self):
        with self.assertRaises(FileNotFoundError):
            self.fs.read("nonexistent_file.txt")


if __name__ == "__main__":
    unittest.main()
