import setuptools

from distutils.core import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="indiredis",
    version="0.3.1",
    author="Bernard Czenkusz",
    author_email="bernie@skipole.co.uk",
    description="An INDI web client for general Instrument control. If the package is run, it provides a web service for controlling instruments. If imported, it provides functions which can be adapted to your own web server.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bernie-skipole/indi",
    packages=['indiredis', 'indiredis.webcode'],
    include_package_data=True,
    install_requires=[
          'indi-mr',
          'paho-mqtt',
          'redis',
          'skipole',
          'waitress'
      ],
    keywords='indi client astronomy instrument',
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
