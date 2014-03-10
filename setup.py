from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='concorde',
      version='0.1',
      description='Static site generator using Markdown and Jinja',
      long_description=readme(),
      classifiers=[
        'Development Status :: 3 - Alpha',
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
          'console_scripts': ['concorde=concorde.command_line:main'],
      },
      setup_requires=['nose>=1.0'],
      test_suite='nose.collector',
      tests_require=['nose', 'mock', 'coverage'],
      include_package_data=True,
      zip_safe=False)
