import argparse
import os
import fnmatch
from operator import itemgetter
from datetime import datetime
from urlparse import urljoin

from markdown import Markdown
import dateutil.parser
from jinja2 import Environment, FileSystemLoader
import PyRSS2Gen

def get_files(paths, extensions=['.md', '.markdown'], recurse=False):
    files = []
    for path in paths:
        if os.path.isfile(path):
            files.append(path)
        for root, dirs, filenames in os.walk(path):
            files.extend([os.path.join(root, filename) for filename in filenames])
            if not recurse:
                break
    for extention in extensions:
        files = fnmatch.filter(files, '*'+extention)
    return files

def parse_markdown_file(md_file):
    md = Markdown(extensions=['extra', 'meta', 'nl2br', 'sane_lists'])
    html = md.convert(open(md_file).read())
    slug, _ = os.path.splitext(os.path.basename(md_file))

    if not hasattr(md, 'Meta'):
        md.Meta = {}

    data = {}
    data.update(md.Meta)
    data.update({
        'title': md.Meta.get('title', [''])[0] or slug.replace('-', ' ').replace('_', ' ').title(),
        'date': dateutil.parser.parse(md.Meta.get('date', [''])[0]) or os.path.getmtime(source),
        'html': html,
        'slug': slug,
        'source': md_file,
        'link': os.path.splitext(md_file)[0]
    })
    return data

def render_to_file(context, template, outfile):
    env = Environment(loader=FileSystemLoader(os.path.dirname(template)),
                      trim_blocks=True, lstrip_blocks=True)
    output = env.get_template(os.path.basename(template)).render(context)
    with open(outfile, 'w') as f:
        f.write(output.encode('utf-8'))

def contexts_and_destinations(md_files, output_extentsion):
    for md_file in md_files:
        context = parse_markdown_file(md_file)
        outfile = os.path.splitext(md_file)[0] + output_extentsion
        context['url'] = outfile
        yield context, outfile

def render_articles(md_files, template, output_extension=''):
    for context, outfile in contexts_and_destinations(md_files, output_extension or os.path.splitext(template)[1]):
        render_to_file(context, template, outfile)

def file_relpath(file1, file2):
    return os.path.join(os.path.relpath(os.path.dirname(file1), os.path.dirname(file2)),
                        os.path.basename(file1))

def render_to_index(md_files, template, indexfile, output_extension):
    articles = [context for context, _ in contexts_and_destinations(md_files, output_extension)]
    articles.sort(key=itemgetter('date'), reverse=True)
    for article in articles:
        article['url'] = file_relpath(article['url'], indexfile)
    render_to_file({'articles': articles}, template, indexfile)

def generate_feed(md_files, output_extension, feedfile, feed_url, title='', description=''):
    articles = [context for context, _ in contexts_and_destinations(md_files, output_extension)]
    articles.sort(key=itemgetter('date'), reverse=True)
    for article in articles:
        relative_path = file_relpath(article['url'], feedfile)
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

def main():
    base_parser = argparse.ArgumentParser(add_help=False)
    base_parser.add_argument('-t', '--template', default='', help='Template file to use when rendering')
    base_parser.add_argument('-r', '--recurse', action='store_true', default=False, 
                             help='Recurse through a directory')
    base_parser.add_argument('--output-extension', help='File extension of the rendered output files')
    base_parser.add_argument('paths', metavar='path', nargs="+", help='Markdown file or directory of Markdown files')

    parser = argparse.ArgumentParser(description="Static site generator")
    subparsers = parser.add_subparsers(help='subcommand help', dest='subparser_name')

    pages_parser = subparsers.add_parser('pages', help='Render Markdown files to pages', parents=[base_parser])

    index_parser = subparsers.add_parser('index', help='Create an index file', parents=[base_parser])
    index_parser.add_argument('-o', '--output', required=True, help='Write index to file')

    rss_parser = subparsers.add_parser('rss', help='Create an RSS feed', parents=[base_parser])
    rss_parser.add_argument('-o', '--output', required=True, help='Write feed to file')
    rss_parser.add_argument('--title', default='', help='Title of the RSS feed')
    rss_parser.add_argument('--description', default='', help='Description of the RSS feed')
    rss_parser.add_argument('--url', default='', help='URL of the RSS feed')

    args = parser.parse_args()

    markdown_files = get_files(args.paths, extensions=['.md', '.markdown'],
                               recurse=args.recurse)
    output_extension = args.output_extension or os.path.splitext(args.template)[1]

    if args.subparser_name == 'index':
        render_to_index(markdown_files, args.template, args.output, output_extension)
        return
    if args.subparser_name == 'pages':
        render_articles(markdown_files, args.template, output_extension)
        return
    if args.subparser_name == 'rss':
        generate_feed(markdown_files, output_extension, args.output, args.url,
                      title=args.title, description=args.description)
        return

if __name__ == "__main__":
    main()
