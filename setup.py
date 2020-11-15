import setuptools

from distutils.core import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="indiredis",
    version="0.0.9",
    author="Bernard Czenkusz",
    author_email="bernie@skipole.co.uk",
    description="INDI client storing instrument data to redis, and on receiving data published to redis, sending on to indiserver. If the package is run, it provides instrument control via a web service. If imported, it provides tools to read/write to redis, and hence indiserver, for use by your own GUI or WEB applications.",
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
