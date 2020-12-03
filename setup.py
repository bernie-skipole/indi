import setuptools

from distutils.core import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="indiredis",
    version="0.1.1",
    author="Bernard Czenkusz",
    author_email="bernie@skipole.co.uk",
    description="Client for general Instrument control, converting between the INDI protocol and redis storage. If the package is run, it provides a web service for controlling instruments attached via indiserver. If imported, it provides tools to read/write to redis, and hence the INDI protocol, for use by your own GUI or WEB applications.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bernie-skipole/indi",
    packages=['indiredis', 'indiredis.indiwsgi', 'indiredis.indiwsgi.webcode'],
    include_package_data=True,
    install_requires=[
          'paho-mqtt',
          'redis',
          'skipole',
          'waitress'
      ],
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
