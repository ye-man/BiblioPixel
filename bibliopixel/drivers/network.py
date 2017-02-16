import socket, sys, time, os

from . driver_base import DriverBase
from .. import log, util
from .. return_codes import RETURN_CODES


class CMDTYPE:
    SETUP_DATA = 1  # reserved for future use
    PIXEL_DATA = 2
    BRIGHTNESS = 3


class DriverNetwork(DriverBase):
    """Driver for communicating with another device on the network."""

    def __init__(self, num=0, width=0, height=0, host="localhost", port=3142):
        super(DriverNetwork, self).__init__(num, width, height)

        self._host = host
        self._port = port

    def _connect(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self._host, self._port))
            return s
        except socket.gaierror:
            error = "Unable to connect to or resolve host: {}".format(
                self._host)
            log.error(error)
            raise IOError(error)

    def _compute_packet(self):
        count = self.bufByteCount()
        self._packet = util.generate_header(CMDTYPE.PIXEL_DATA, count)
        indexes = range(self._pos, self._pos + self.numLEDs)
        self._packet.extend(int(c) for i in indexes for c in self._colors[i])

    # Push new data to strand
    def _send_packet(self):
        try:
            s = self._connect()
            s.sendall(self._packet)

            resp = ord(s.recv(1))

            s.close()

            if resp != RETURN_CODES.SUCCESS:
                log.warning("Bytecount mismatch! %s", resp)

        except Exception as e:
            log.exception(e)
            error = "Problem communicating with network receiver!"
            log.error(error)
            raise IOError(error)

    def set_device_brightness(self, brightness):
        packet = util.generate_header(CMDTYPE.BRIGHTNESS, 1)
        packet.append(self._brightness)
        s = self._connect()
        s.sendall(packet)
        resp = ord(s.recv(1))
        return resp == RETURN_CODES.SUCCESS


MANIFEST = [
    {
        "id": "network",
        "class": DriverNetwork,
        "type": "driver",
        "display": "Network",
        "desc": "Sends pixel data over the network to a reciever.",
        "params": [{
                "id": "num",
                "label": "# Pixels",
                "type": "int",
                "default": 0,
                "min": 0,
                "help": "Total pixels in display. May use Width AND Height instead."
        }, {
            "id": "width",
            "label": "Width",
            "type": "int",
            "default": 0,
            "min": 0,
            "help": "Width of display. Set if using a matrix."
        }, {
            "id": "height",
            "label": "Height",
            "type": "int",
            "default": 0,
            "min": 0,
            "help": "Height of display. Set if using a matrix."
        }, {
            "id": "host",
            "label": "Pixel Size",
            "type": "str",
            "default": "localhost",
            "help": "Receiver host to connect to."
        }, {
            "id": "port",
            "label": "Port",
            "type": "int",
            "default": 3142,
            "help": "Port to connect to."
        }]
    }
]
