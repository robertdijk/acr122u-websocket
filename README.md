# ACR122U Websocket

[![PyPI - Version](https://img.shields.io/pypi/v/acr122u-websocket)](https://pypi.org/project/acr122u-websocket/)
[![PyPI - License](https://img.shields.io/pypi/l/acr122u-websocket)](https://pypi.org/project/acr122u-websocket/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/acr122u-websocket)](https://pypi.org/project/acr122u-websocket/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/acr122u-websocket)](https://pypi.org/project/acr122u-websocket/)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/acr122u-websocket)](https://pypi.org/project/acr122u-websocket/)

This project enables you to connect an usb ACR122U NFC card scanner to a computer and access it using Socket.IO.

## Features

- Read UUID from nfc cards and send them over Socket.IO.
- Websocket messages to start and stop the polling for cards.
- Websocket messages to give a confirmation or error beep and light signal.
- Automatically reconnect to the reader when interrupted.

## Installation

You can install this package from [PyPI](https://pypi.org/project/acr122u-websocket/).

```shell
pip install acr122u-websocket
```

## Usage

1. Connect the ACR122U reader to the computer
2. Run the app
    ```shell
    python -m acr122u_websocket.app
    ```

## API

You can connect to the webserver using [Socket.IO](https://socket.io).
These are the available events:

<details>
<summary><h3><code>polling</code></h3></summary>

Start or stop the polling.

#### Request

- `start` to start the polling.
- `stop` to stop the polling.

#### Reply

- `no card reader connected` if no card reader is connected.
- `polling started` if the polling has (already) started.
- `polling stopped` if the polling has (already) stopped.
- `invalid message` if the message is neither `start` nor `stop`.

</details>

<details>
<summary><h3><code>status indicator</code></h3></summary>

Set the status indicator.

#### Request

- `confim` to play the confirming status.
- `error` to play the error status.

#### Reply

- `no card reader connected` if no card reader is connected
- `confirm status set` if the confirm beep and light have been show
- `error status set` if the error beep and light have been show
- `invalid message` if the message is neither `confirm` nor `error`

</details>

<details>
<summary><h3><code>card scanned</code></h3></summary>

Broadcasts when a card has been scanned

#### Broadcast

- `{"uuid": [..]}` - An object containing the uuid in the form of a list of integers.

</details>

## Example

See an example webpage at [test.html](acr122u_websocket/templates/test.html).

This page is also served on [`http://localhost:8080/test`](http://localhost:8080/test).