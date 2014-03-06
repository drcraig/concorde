import unittest
import os
import time
import datetime
import argparse

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
            mod_time = datetime.datetime(2014,3,1,12,0,0)
            getmtime.return_value = time.mktime(mod_time.timetuple())
            context = concorde.parse_markdown_file('a-folder/a-markdown-file.md')
            self.assertTrue(getmtime.called)
            self.assertEqual('A Markdown File', context['title'])
            self.assertIn('No metadata', context['html'])
            self.assertEqual(mod_time, context['date'])

    def test_empty(self):
        m = mock.mock_open(read_data='')
        with mock.patch('concorde.open', m, create=True), \
             mock.patch('concorde.os.path.getmtime') as getmtime:
            mod_time = datetime.datetime(2014,3,1,12,0,0)
            getmtime.return_value = time.mktime(mod_time.timetuple())
            context = concorde.parse_markdown_file('a-folder/a-markdown-file.md')
            self.assertTrue(getmtime.called)
            self.assertEqual('A Markdown File', context['title'])
            self.assertIn('', context['html'])
            self.assertEqual(mod_time, context['date'])

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
        with mock.patch('concorde.Environment') as Environment:
            env = mock.Mock()
            Environment.return_value = env
            template = mock.Mock()
            env.get_template.return_value = template
            concorde.render({'the':'context'}, 'folder/the-template')
            env.get_template.assert_called_with('the-template')
            template.render.assert_called_with({'the': 'context'})

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

    def test_render_to_index(self):
        with mock.patch('concorde.parse_markdown_file') as parse_markdown_file, \
             mock.patch('concorde.render') as render, \
             mock.patch('concorde.write') as write:
            article_1 = {
                'link': 'a/b/slug-1.ext',
                'date': datetime.datetime(2014,1,1)
            }
            article_2 = {
                'link': 'a/b/c/slug-2.ext',
                'date': datetime.datetime(2014,2,1)
            }
            parse_markdown_file.side_effect = [article_1, article_2]
            render.return_value = 'rendered'

            concorde.render_to_index(['a/b/slug-1.md', 'a/b/c/slug-2.md'], 'template', 'a/index', '.ext')
            article_1['url'] = 'b/slug-1.ext'
            article_2['url'] = 'b/c/slug-2.ext'

            render.assert_called_once_with({'articles': [article_2, article_1]}, 'template')
            write.assert_called_once_with('rendered', 'a/index')

    def test_generate_feed(self):
        with mock.patch('concorde.parse_markdown_file') as parse_markdown_file, \
             mock.patch('concorde.open', mock.mock_open(), create=True) as mock_open:
            article_1 = {
                'title': 'Title 1',
                'html': 'HTML 1',
                'link': 'a/b/slug-1.ext',
                'date': datetime.datetime(2014,1,1)
            }
            article_2 = {
                'title': 'Title 2',
                'html': 'HTML 2',
                'link': 'a/b/c/slug-2.ext',
                'date': datetime.datetime(2014,2,1)
            }
            parse_markdown_file.side_effect = [article_1, article_2]

            concorde.generate_feed(['a/b/slug-1.md', 'a/b/c/slug-2.md'], '.ext', 'a/feed',
                                    'http://example.com/feed', 'Feed Title', 'Feed Description')
            article_1['url'] = 'b/slug-1.ext'
            article_2['url'] = 'b/c/slug-2.ext'
            mock_open.assert_called_once_with('a/feed', 'w')

class TestCommandLine(unittest.TestCase):
    def setUp(self):
        os.chdir(TESTSITE)

    def test_pages(self):
        concorde.command_line.main(['pages', '-t', 'templates/page-template.html', 'site/blog/'])

    def test_index(self):
        concorde.command_line.main(['index', '-t', 'templates/index-template.html',
                                    '-o', 'site/blog/index.html', 'site/blog/'])

    def test_rss(self):
        concorde.command_line.main(['rss', '--title', 'The Title', '--description', 'The Description',
                                    '--url', 'http://example.com/blog/rss.xml',
                                    '-o', 'site/blog/rss.xml', 'site/blog/'])
