import os
from setuptools import find_packages, setup

## Read in the README file:
with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

## Allow setup.py to be run from any path:
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

## Setup:
setup(name="django-lazydrf",
      version="0.0.1.dev0",
      packages=find_packages(),
      include_package_data=True,
      license="BSD License",
      description="Dirty magic to generate automated DRF endpoints",
      long_description=README,
      url="https://github.com/vst/django-lazydrf",
      author="Vehbi Sinan Tunalioglu",
      author_email="vst@vsthost.com",
      install_requires=[
          "Django>=1.9",
          "django-filter>=0.13.0",
          "djangorestframework>=3.3.3",
      ],
      classifiers=[
          "Environment :: Web Environment",
          "Framework :: Django",
          "Framework :: Django :: 1.9",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: BSD License",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: 3.5",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
      ])
