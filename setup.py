from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='concorde',
      version='0.0',
      description='Static site generator using Markdown and Jinja',
      long_description=readme(),
      classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
        'Environment :: Console'
      ],
      keywords='static generator markdown jinja',
      url='http://github.com/drcraig/concorde',
      author='Dan Craig',
      author_email='drcraig@gmail.com',
      license='MIT',
      packages=['concorde'],
      install_requires=[
          'markdown',
          'jinja2',
          'PyRSS2Gen',
          'python-dateutil'
      ],
      entry_points={
          'console_scripts': ['concorde=concorde:main'],
      },
      include_package_data=True,
      zip_safe=False)
