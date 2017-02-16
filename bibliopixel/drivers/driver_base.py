from .. import gamma as _gamma
from .. import data_maker
import threading, time


class ChannelOrder:
    RGB = 0, 1, 2
    RBG = 0, 2, 1
    GRB = 1, 0, 2
    GBR = 1, 2, 0
    BRG = 2, 0, 1
    BGR = 2, 1, 0

    ORDERS = RGB, RBG, GRB, GBR, BRG, BGR


class DriverBase(object):
    """Base driver class to build other drivers from."""

    # If set_device_brightness is not empty, it's a method that allows you
    # to directly set the brightness for the device.
    #
    # If it is empty, then the brightness is used as a scale factor in rendering
    # the pixels.
    set_device_brightness = None

    def __init__(self, num=0, width=0, height=0, c_order=ChannelOrder.RGB,
                 gamma=None, maker=data_maker.MAKER):
        if num == 0:
            num = width * height
            if num == 0:
                raise ValueError("Either num, or width and height are needed!")

        self.numLEDs = num
        gamma = gamma or _gamma.DEFAULT
        self.gamma = gamma

        self.c_order = c_order
        self.perm = ChannelOrder.ORDERS.index(c_order)

        self.layout = None

        self.width = width
        self.height = height
        self._buf = maker.make_packet(self.bufByteCount())

        self._thread = None
        self.lastUpdate = 0

        self._render_td = maker.renderer(
            gamma=gamma.gamma,
            offset=gamma.offset,
            permutation=self.perm,
            min=gamma.lower_bound,
            max=255)

        self.brightness_lock = threading.Lock()
        self._brightness = 255
        self.set_brightness(255)

    def set_layout(self, layout):
        pass

    def set_colors(self, colors, pos):
        self._colors = colors
        self._pos = pos

    def cleanup(self):
        pass

    def bufByteCount(self):
        return 3 * self.numLEDs

    def sync(self):
        pass

    def _compute_packet(self):
        """Compute the packet from the colors and position.

        Eventually, this will run on the compute thread.
        """
        pass

    def _send_packet(self):
        """Send the packet to the driver.

        Eventually, this will run on an I/O thread.
        """
        pass

    def update_colors(self):
        if self._thread:
            start = time.time() * 1000.0

        with self.brightness_lock:
            # Swap in a new brightness.
            brightness, self._waiting_brightness = (
                self._waiting_brightness, None)

        if brightness is not None:
            self._brightness = brightness
            if self.set_device_brightness:
                self.set_device_brightness(brightness)

        self._compute_packet()
        self._send_packet()

        if self._thread:
            self.lastUpdate = (time.time() * 1000.0) - start

    def set_brightness(self, brightness):
        with self.brightness_lock:
            self._waiting_brightness = brightness

    def _render_py(self, colors, pos, length, output, level):
        fix, (r, g, b) = self.gamma.get, (int(level) * i for i in self.c_order)
        for i in range(length):
            c = tuple(int(x) for x in colors[i + pos])
            output[i * 3:(i + 1) * 3] = fix(c[r]), fix(c[g]), fix(c[b])
        return output

    def _render(self):
        render = self._render_td or self._render_py
        if self.set_device_brightness:
            level = 1.0
        else:
            level = self._brightness / 255.0
        self._buf = render(
            self._colors, self._pos, self.numLEDs, self._buf, level)
