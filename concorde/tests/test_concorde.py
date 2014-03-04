import unittest
import os

import concorde

CUR_DIR = os.path.dirname(__file__)
TESTSITE = os.path.join(CUR_DIR, 'testsite')

class TestConcorde(unittest.TestCase):
    def test_get_source_files_none(self):
        files = concorde.get_source_files([TESTSITE])
        self.assertItemsEqual([], files)

    def test_get_source_files_recursive(self):
        files = concorde.get_source_files([os.path.join(TESTSITE, 'site')], recurse=True)
        expected = ['site/page.md', 'site/another-page.markdown', 
                    'site/blog/post-1.md', 'site/blog/post-2.md']
        self.assertItemsEqual([os.path.join(TESTSITE, f) for f in expected], files)
        
    def test_get_source_files_not_recursive(self):
        files = concorde.get_source_files([os.path.join(TESTSITE, 'site')], recurse=False)
        expected = ['site/page.md', 'site/another-page.markdown']
        self.assertItemsEqual([os.path.join(TESTSITE, f) for f in expected], files)

        files = concorde.get_source_files([os.path.join(TESTSITE, 'site/blog')], recurse=False)
        expected = ['site/blog/post-1.md', 'site/blog/post-2.md']
        self.assertItemsEqual([os.path.join(TESTSITE, f) for f in expected], files)

