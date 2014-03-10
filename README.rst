concorde
========

Simple static site generator built from Markdown and Jinja

Three commands to produce three things::

    concorde pages  renders Markdown files through a template, producing new pages
    concorde index  takes a list of Markdown files that you presumably just rendered
                    with pages, orders them by date, and renders them through a 
                    template to produce an index file
    concorde rss    similar to concorde index, but produces an RSS feed instead

Run ``concorde <command> help`` for more details.

One distinguishing feature of Concorde is that the templates and the rendered
pages do not necessarily have to be HTML. In fact, Concorde was created because
of the need to quickly tack on a static blog generator to a site written in PHP.

Concorde is designed to be easily paired with a Makefile to generate a site.
For example, given a site laid out like so::

    my-example-site
        site
            a-post.md
            another-post.md
        templates
            index.html
            blog-post.html

A Makefile to build the HTML pages, index page, and RSS feed would look like

.. code:: makefile

    posts := $(patsubst %.md,%.html,$(wildcard site/*.md)) 

    .PHONY : all clean

    all: site/index.html site/rss.xml $(posts)

    clean:
        -rm site/index.html
        -rm site/rss.xml
        -rm $(posts)

    site/index.html: $(posts) templates/index.html
        concorde index --template=templates/index.html --output=$@ --output-extension=.html site/

    site/blog/rss.xml : $(posts)
        concorde rss --output=$@ --title="My Example Blog" --url="http://example.com/rss.xml" site/

    $(posts): site/*.md templates/blog-post.html
        concorde pages --template=templates/blog-post.html site/
