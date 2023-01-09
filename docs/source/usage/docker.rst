Docker Setup
============

These notes describe how containers were set up to test this package. The notes are intended as a personal reminder to myself.

With docker installed on a host PC, a redis container, an indiserver container and an indiredis container were installed on a docker network, to excercise connectivity between them.

Create a network
^^^^^^^^^^^^^^^^

This creates an internal network with name indi_net::

    docker network create indi_net



redis container
^^^^^^^^^^^^^^^

This creates and runs a container with name redis_server_cont running a redis database, connected to the network indi_net. The image is the standard redis image automatically pulled from the docker hub::

    docker run --name redis_server_cont --network indi_net -d redis


indiserver container
^^^^^^^^^^^^^^^^^^^^

In a directory, create a Dockerfile::


    FROM debian:11-slim

    # install dependencies
    RUN apt-get update && apt-get install -y indi-bin && rm -rf /var/lib/apt/lists/*

    # The app runs on port 7624
    EXPOSE 7624

    # and run the app
    CMD ["indiserver", "indi_simulator_telescope", "indi_simulator_ccd"]



Then build the image::

    docker build -t indiserver_image .

And create and run a container from this image on the network indi_net::

    docker run -d --name indiserver_cont --network indi_net indiserver_image



indiredis container
^^^^^^^^^^^^^^^^^^^

In another directory, create a Dockerfile::


    FROM python:latest

    # install dependencies
    RUN pip install --no-cache-dir indiredis

    # The app runs on port 8000
    EXPOSE 8000

    # and set an entrypoint for the app
    ENTRYPOINT ["python", "-m", "indiredis"]


Then build the image::

    docker build -t indiredis_image .

And create and run a container from this image on the network indi_net::

    docker run -d --name indiredis_cont --network indi_net indiredis_image --host 0.0.0.0 --rhost redis_server_cont --ihost indiserver_cont /blobfolder


The host address of 0.0.0.0 allows the web service to listen on all ports, so a web browser on the host machine can connect to it.

Inspect the network, and get the ip address of the container indiredis_cont:: 

    docker network inspect indi_net

then from the host browser call this ip address on port 8000 to view the indi web client.



