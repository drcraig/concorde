import unittest
import os

import concorde

CUR_DIR = os.path.dirname(__file__)
TESTSITE = os.path.join(CUR_DIR, 'testsite')

class TestGetSources(unittest.TestCase):
    def test_none(self):
        files = concorde.get_source_files([TESTSITE])
        self.assertItemsEqual([], files)

    def test_recursive(self):
        files = concorde.get_source_files([os.path.join(TESTSITE, 'site')], recurse=True)
        expected = ['site/page.md', 'site/another-page.markdown', 
                    'site/blog/post-1.md', 'site/blog/post-2.md']
        self.assertItemsEqual([os.path.join(TESTSITE, f) for f in expected], files)
        
    def test_not_recursive(self):
        files = concorde.get_source_files([os.path.join(TESTSITE, 'site')], recurse=False)
        expected = ['site/page.md', 'site/another-page.markdown']
        self.assertItemsEqual([os.path.join(TESTSITE, f) for f in expected], files)

        files = concorde.get_source_files([os.path.join(TESTSITE, 'site/blog')], recurse=False)
        expected = ['site/blog/post-1.md', 'site/blog/post-2.md']
        self.assertItemsEqual([os.path.join(TESTSITE, f) for f in expected], files)

    def test_mix_dirs_files(self):
        sources = ['site/page.md', 'site/blog']
        files = concorde.get_source_files([os.path.join(TESTSITE, f) for f in sources],
                                          recurse=True)
        expected = ['site/page.md',
                    'site/blog/post-1.md', 'site/blog/post-2.md']
        self.assertItemsEqual([os.path.join(TESTSITE, f) for f in expected], files)

