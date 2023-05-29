Display Daily Agenda on an E-Ink Display
========================================

Overview
--------

This is a version of my project <https://github.com/bablokb/pi-e-ink-daily>
written for the Raspberry Pi Pico.

In contrast to that project, the pico is only responsible for updating
the display. All the calendar processing is done on a server. Therefore,
this project has a server part and a client/pico-part. The former is
implemented in plain Python and can run on (almost) any system,
the latter is implemented in CircuitPython.

While this specific project is about the display of the daily agenda,
the core of the client is content agnostic: it fetches data from a
server and then updates the display. After that, it shuts down the
system. Wakeup is manually or triggered by an RTC-alarm.


Server
------

To install the server, run

    git clone https://github.com/bablokb/pico-e-ink-daily.git
    cd pico-e-ink-daily
    sudo tools/install-server

After installation, you have to configure your calendars in
`/etc/py-calendar2json.json`. After that, start the server with

    sudo systemctl start py-calendar2json.service


Client
------

To install the client, copy all files below `client` to your Pico.
Additionally, you have to install at least the following libraries:

  - adafruit_bitmap_font
  - adafruit_bus_device
  - adafruit_display_shapes
  - adafruit_display_text
  - adafruit_requests

Depending on your e-ink display, additional libraries might be necessary.

The client supports different hardware-setups. You have to configure the
hardware you use in the file `config/<board.board_id>.py`. You will find
various examples in the directory `config`, e.g. for Pimoroni's
InkyFrame 5.7" display.


secrets.py
----------

For WLAN-credentials and other settings specific to you environment,
you have to create the file `config/secrets.py`:

    class Settings:
      pass

    secrets = Settings()

    secrets.ssid      = 'my-ssid'
    secrets.password  = 'my-very-secret-password'
    secrets.retry     = 2
    secrets.debugflag = False
    #secrets.channel   = 6       # optional
    #secrets.timeout   = 10      # optional

    secrets.data_url = 'http://my-calendar2json-server-url'
    secrets.time_url = 'http://worldtimeapi.org/api/ip'
