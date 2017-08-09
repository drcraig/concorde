import os.path
import argparse

from . import get_source_files, render_articles, render_to_index, generate_feed

def main(test_args=None):
    base_parser = argparse.ArgumentParser(add_help=False)
    base_parser.add_argument('-t', '--template', default='', help='Template file to use when rendering')
    base_parser.add_argument('--output-extension', default=None,
                             help='File extension of the rendered output files, if different '
                                  'from the template file extension')
    base_parser.add_argument('-r', '--recurse', action='store_true', default=False, 
                             help='Recurse through a directory')
    base_parser.add_argument('paths', metavar='path', nargs="+", help='Markdown file(s) or director(y,ies) of Markdown files')

    parser = argparse.ArgumentParser(description="Static site generator")
    subparsers = parser.add_subparsers(dest='subparser_name')

    pages_parser = subparsers.add_parser('pages', help='Render Markdown files to pages', parents=[base_parser])

    index_parser = subparsers.add_parser('index', help='Create an index file', parents=[base_parser])
    index_parser.add_argument('-o', '--output', required=True, help='Write index to file')

    rss_parser = subparsers.add_parser('rss', help='Create an RSS feed', parents=[base_parser])
    rss_parser.add_argument('-o', '--output', required=True, help='Write feed to file')
    rss_parser.add_argument('--title', default='', help='Title of the RSS feed')
    rss_parser.add_argument('--description', default='', help='Description of the RSS feed')
    rss_parser.add_argument('--url', default='', help='URL of the RSS feed')

    args = parser.parse_args(test_args) if test_args else parser.parse_args()

    markdown_files = get_source_files(args.paths, recurse=args.recurse)

    output_extension = os.path.splitext(args.template)[1] if args.output_extension is None \
                       else args.output_extension
    if args.subparser_name == 'pages':
        render_articles(markdown_files, args.template, output_extension)
        return
    if args.subparser_name == 'index':
        render_to_index(markdown_files, args.template, args.output, output_extension)
        return
    if args.subparser_name == 'rss':
        generate_feed(markdown_files, output_extension, args.output, args.url,
                      title=args.title, description=args.description)
        return
