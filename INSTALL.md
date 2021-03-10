# Installation

## Introduction

The server is made using python3.

There is no build needed but a few dependencies to be installed.

## Dependencies

Please first install the following dependencies
- pip3 install numpy
- pip3 install websockets

# Launch the server

Use the wrapping script as follow :

```console
$ launch_srv.sh
```

# Launch a client

Use the wrapping script as follow :

```console
$ launch_client_example.sh -n <NAME> --addr <SRV_IP> --port <SRV_PORT>
```

You could add "--demo-mode simple" to use a simple stategy, otherwise the client will perform random moves.
