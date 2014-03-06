import unittest
import os
import datetime

import mock

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

FULL_METADATA = '''
Title: The Title
Date: 1/2/2014
Something: Non standard metadata

The Body
'''.lstrip()

class TestParseMarkdownFile(unittest.TestCase):
    def test_parse_markdown(self):
        m = mock.mock_open(read_data=FULL_METADATA)
        with mock.patch('concorde.open', m, create=True), \
             mock.patch('concorde.os.path.getmtime') as getmtime:
            context = concorde.parse_markdown_file('a-folder/a-markdown-file.md', output_extension='.html')
            self.assertEqual('The Title', context['title'])
            self.assertIn('The Body', context['html'])
            self.assertEqual('a-markdown-file', context['slug'])
            self.assertEqual('a-folder/a-markdown-file.md', context['source'])
            self.assertEqual('a-folder/a-markdown-file.html', context['link'])
            self.assertEqual(datetime.datetime(2014,1,2), context['date'])
            self.assertEqual(['Non standard metadata'], context['something'])

    def test_no_metadata(self):
        m = mock.mock_open(read_data='No metadata')
        with mock.patch('concorde.open', m, create=True), \
             mock.patch('concorde.os.path.getmtime') as getmtime:
            getmtime.return_value = datetime.datetime(2014,3,1,12,0,0)
            context = concorde.parse_markdown_file('a-folder/a-markdown-file.md')
            self.assertTrue(getmtime.called)
            self.assertEqual('A Markdown File', context['title'])
            self.assertIn('No metadata', context['html'])
            self.assertEqual(datetime.datetime(2014,3,1,12,0,0), context['date'])

class TestUtilities(unittest.TestCase):
    def test_write(self):
        mock_open = mock.mock_open()
        with mock.patch('concorde.open', mock_open, create=True):
            concorde.write('stuff', 'a-file')
            mock_open.assert_called_once_with('a-file', 'w')

    def test_file_relpath(self):
        file_1 = 'a/b/c'
        file_2 = 'a/e'
        path = concorde.file_relpath(file_1, file_2)
        self.assertEqual('b/c', path)

class TestRendering(unittest.TestCase):
    def test_render(self):
        pass

    def test_render_articles(self):
        with mock.patch('concorde.parse_markdown_file') as parse_markdown_file, \
             mock.patch('concorde.render') as render, \
             mock.patch('concorde.write') as write:
            parse_markdown_file.side_effect = [
                {
                    'title': 'Title 1',
                    'html': '<p>html 1</p>',
                    'slug': 'slug-1',
                    'link': 'slug-1.ext',
                    'source': 'slug-1.md'
                }
            ]
            render.side_effect = ['rendered-1']
            concorde.render_articles(['file-1'], 'template', '.ext')
            parse_markdown_file.assert_called_with('file-1', '.ext')
            write.assert_called_with('rendered-1', 'slug-1.ext')

