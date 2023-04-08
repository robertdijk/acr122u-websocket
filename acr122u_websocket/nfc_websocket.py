import logging
from typing import List

from flask import Flask, render_template
from flask_socketio import SocketIO, emit

from .reader_helpers import CardReaderConnector, CardReaderPoller
from .my_reader import ReaderContainer

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

card_reader_container = ReaderContainer()

card_reader_connector = CardReaderConnector(card_reader_container)
card_reader_connector.daemon = True
card_reader_connector.start()


def emit_uuid(uuid: List[int]):
    socketio.emit('card_scanned', {'uuid': uuid})


card_reader_poller = CardReaderPoller(card_reader_container, emit_uuid)
card_reader_poller.daemon = True
card_reader_poller.start()


@app.route('/test')
def test_page():
    return render_template('test.html')


@socketio.on('connect')
def connect(auth):
    app.logger.info("Client connected")


@socketio.on('disconnect')
def disconnect():
    app.logger.info("Client disconnected")


@socketio.on('polling')
def polling(start_stop):
    if card_reader_container.reader is None:
        emit('polling', 'no card reader connected')
        return

    if start_stop == 'start':
        card_reader_poller.start_polling()
        emit('polling', 'polling started')
    elif start_stop == 'stop':
        card_reader_poller.stop_polling()
        emit('polling', 'polling stopped')
    else:
        emit('polling', 'not a valid message')


@socketio.on('status_indicator')
def set_status_indicator(status):
    if card_reader_container.reader is None:
        emit('status indicator', 'no card reader connected')
        return

    if status == "confirm":
        with card_reader_container.lock:
            card_reader_container.reader.confirm_beep()
        emit('status indicator', 'confirm status set')
    elif status == "error":
        with card_reader_container.lock:
            card_reader_container.reader.error_beep()
        emit('status indicator', 'error status set')
    else:
        emit('polling', 'not a valid status')


if __name__ == '__main__':
    socketio.run(app)
