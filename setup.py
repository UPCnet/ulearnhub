import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.txt')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'gummanager.libs',
    'maxclient',
    'maxcarrot',
    'pyramid',
    'pyramid_beaker',
    'pyramid_chameleon',
    'pyramid_debugtoolbar',
    'pyramid_osiris',
    'pyramid_tm',
    'pyramid_zodbconn',
    'pyramid_multiauth',
    'transaction',
    'waitress',
    'max'
]

setup(name='ulearnhub',
      version='1.10.dev0',
      description='ulearnhub',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Pyramid",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
      author='',
      author_email='',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      tests_require=requires,
      extras_require={
          'test': ['webtest', 'mock', 'httpretty']
      },
      test_suite='ulearnhub',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = ulearnhub:main
      [console_scripts]
      initialize_ulearnhub = ulearnhub.scripts:init_devel
      """,
      )
