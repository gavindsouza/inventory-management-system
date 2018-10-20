# imports - standard imports
from setuptools import setup, find_packages

# imports - module imports
from inventory.__attr__ import __name__, __version__, __description__, __url__, __author__, __email__, __license__

setup(name=__name__,
      version=__version__,
      description=__description__,
      url=__url__,
      author=__author__,
      author_email=__email__,
      license=__license__,
      packages=find_packages(),
      zip_safe=False)
