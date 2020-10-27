import setuptools

from distutils.core import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="indiredis",
    version="0.0.1",
    author="Bernard Czenkusz",
    author_email="bernie@skipole.co.uk",
    description="An INDI web client with redis storage",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bernie-skipole/indi",
    packages=['indiredis', 'indiredis.indiwsgi', 'indiredis.indiwsgi.webcode'],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Topic :: Scientific/Engineering :: Astronomy",
        "Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator"
    ],
)
