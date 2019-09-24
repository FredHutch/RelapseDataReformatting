from setuptools import setup

setup(
    name='RelapseDataReformatting',
    version='0.1',
    packages=['scripts',
              'utils',
              'test',
              'classes',
              'classes.event',
              'classes.evaluator',
              'classes.collection'],
    tests_require=['nose'],
    install_requires=['pycap',
                      'pandas',
                      'pandas-profiling',
                      'pyyaml',
                      'sklearn'],
    url='https://github.com/FredHutch/RelapseDataReformatting',
    license='Apache 2.0',
    author='Fred Hutch HDC',
    author_email='',
    description='A reformatting package for the Relapse project, targetting the RETAIN model'
)
