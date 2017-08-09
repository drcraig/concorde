# coding: utf-8
from __future__ import with_statement

import os
import codecs
from operator import itemgetter
from datetime import datetime
from urlparse import urljoin

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

from markdown import Markdown
import dateutil.parser
from jinja2 import Environment, FileSystemLoader
import PyRSS2Gen

def get_source_files(paths, extensions=['.md', '.markdown'], recurse=False):
    files = []
    for path in paths:
        if os.path.isfile(path):
            files.append(path)
        for root, dirs, filenames in os.walk(path):
            files.extend([os.path.join(root, filename) for filename in filenames])
            if not recurse:
                break
    return [f for f in files if os.path.splitext(f)[1] in extensions]

def parse_markdown_file(md_file, output_extension=''):
    md = Markdown(extensions=['extra', 'meta', 'nl2br', 'sane_lists'])
    html = md.convert(codecs.open(md_file, 'r', 'utf-8').read())
    slug, _ = os.path.splitext(os.path.basename(md_file))

    if not hasattr(md, 'Meta'):
        md.Meta = {}

    data = {}
    data.update(md.Meta)

    date = datetime.fromtimestamp(os.path.getmtime(md_file))
    if md.Meta.get('date'):
        date = dateutil.parser.parse(md.Meta.get('date')[0])
    data.update({
        'title': md.Meta.get('title', [''])[0] or slug.replace('-', ' ').replace('_', ' ').title(),
        'date': date,
        'html': html,
        'slug': slug,
        'source': md_file,
        'link': os.path.splitext(md_file)[0] + output_extension
    })
    return data

def render(context, template):
    env = Environment(loader=FileSystemLoader(os.path.dirname(template)),
                      trim_blocks=True, lstrip_blocks=True)
    return env.get_template(os.path.basename(template)).render(context)

def write(content, filename):
    with codecs.open(filename, 'w', 'utf-8') as f:
        f.write(content)

def render_articles(md_files, template, output_extension=''):
    for md_file in md_files:
        context = parse_markdown_file(md_file, output_extension)
        content = render(context, template)
        write(content, context['link'])

def file_relpath(file1, file2):
    return os.path.join(os.path.relpath(os.path.dirname(file1), os.path.dirname(file2)),
                        os.path.basename(file1))

def render_to_index(md_files, template, indexfile, output_extension):
    articles = [parse_markdown_file(md_file, output_extension) for md_file in md_files]
    articles.sort(key=itemgetter('date'), reverse=True)
    for article in articles:
        article['url'] = file_relpath(article['link'], indexfile)
    content = render({'articles': articles}, template)
    write(content, indexfile)

def generate_feed(md_files, output_extension, feedfile, feed_url, title='', description=''):
    articles = [parse_markdown_file(md_file, output_extension) for md_file in md_files]
    articles.sort(key=itemgetter('date'), reverse=True)
    for article in articles:
        relative_path = file_relpath(article['link'], feedfile)
        article['url'] = urljoin(feed_url, relative_path)

    rss = PyRSS2Gen.RSS2(
        title=title,
        link=feed_url,
        description=description,
        lastBuildDate=datetime.now(),
        items = [
            PyRSS2Gen.RSSItem(
                title=article['title'],
                link=article['url'],
                description=article['html'],
                guid=PyRSS2Gen.Guid(article['url']),
                pubDate=article['date']
            ) for article in articles
         ]
    )
    with open(feedfile, 'w') as f:
        rss.write_xml(f)
