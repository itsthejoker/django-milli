import os
from setuptools import setup

with open("README.md") as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="django_milli",
    version="0.1.0",
    url='https://github.com/itsthejoker/django-milli',
    include_package_data=True,
    license="Apache 2.0",
    description="An installable app for Milli, the incredibly fast search engine core.",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Joe Kaufeld",
    author_email="opensource@joekaufeld.com",
    packages=["django_milli"],
    install_requires=[
        "django>=3.2",
        "some-pkg @ git+https://git@github.com/AlexAltea/milli-py",
    ],
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.10",
        "Topic :: Database :: Database Engines/Servers",
    ],
)
