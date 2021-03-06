The Serial Driver
--------------------

The Serial Driver handles LEDs that are attached to the computer with the USB
bus, particularly the `AllPixel <https://maniacallabs.com/products/allpixel/>`_
and
`PiPixel <https://www.tindie.com/products/ManiacalLabs/pipixel-raspberry-pi-led-strip-hat/>`_
hardware controllers, but be adapted to any serial or USB connected LED strips.

If you aren't using serial hardware, you can skip this chapter.

**Example**: The ``driver`` section of a project using Serial communication

.. code-block:: yaml

    driver:
      typename: .serial
      ledtype: LPD8806
      c_order: GRB
      gamma: 2.5
      device_id: 2


Serial Driver Fields
=========================

``ledtype``
  LED protocol type - see below for details

``dev``
  Serial device address/path. If not set, the first serial device
  found will be used

``c_order``
  RGB color order

``gamma``
  the gamma correction for the driver

``spi_speed`` (default ``2``)
  SPI datarate for applicable LED types, in MHz

``restart_timeout`` (default ``3``)
  Seconds to wait between reconfigure reboot and reconnection attempt

``device_id``
  Device ID to connect to.  If not set, connect to the first device ID
  found on the device

``hardwareID`` (default ``'1D50:60AB'``)
   A valid USB VID:PID (vendor id : product id) pair.  The default is the
   VID:PID pair for the AllPixel

``baudrate`` (default ``921600``)
  Baud rate to connect to serial device






Basic Usage
===============





[TODO-API: embed or point to generated documentation for serial/driver.py]

LEDTYPE
^^^^^^^

The Serial Driver needs to have an LEDTYPE set to identify the LED chipset and
hardware.  This must be one of these values: [TODO-API: point to or embed generated
documentation for ledtype.py]

.. bp-code-block:: footer

   shape: [64, 24]
   animation:
     typename: $bpa.matrix.MathFunc
     palette: bold
     func: 15
