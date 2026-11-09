import unittest
from scripts.package import build
class PackageTests(unittest.TestCase):
 def test_reproducible_valid_archive(self):
  first=build();second=build()
  self.assertEqual(first["sha256"],second["sha256"])
