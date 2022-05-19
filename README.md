# Behave and `async` Transports

## Introduction

The Python Behave framework provides behaviour-driven development (BDD).
The 1.2.6 version adds support for `asyncio`.

The example here demonstrates Behave `async_step` with
`asyncio.DatagramProtocol`.
The server code is from the Python language docs.  The client protocol
factory class is also based on the example code from the docs.

If you aren't familiar with Python coroutines and transports, using
Behave becomes quite a puzzle.  This project demonstrates a solution
to running a client in the background and performing tests in the
foreground.

## Using the Sample

The server code is from
[the asyncio UDP echo server example](https://docs.python.org/3/library/asyncio-protocol.html#udp-echo-server).
Follow the link, and copy and run the code for the server portion.

You will need Behave and Hamcrest:

    python3 -m venv ab_env
    source ab_env/bin/activate
    python3 -m pip install behave PyHamcrest wheel

Start the server in a different shell, and then run Behave.  That's it!

## License

This code is released under the GPL 3.0 license.
