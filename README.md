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
  - adafruit_connection_manager
  - adafruit_display_shapes
  - adafruit_display_text
  - adafruit_requests
  - adafruit_ticks.mpy

Depending on your e-ink display, additional libraries might be necessary.

The client supports different hardware-setups. See the section about
hardware configuration below.


Configuration and Settings
--------------------------

The central configuration file for build and user specific settings is
the file `client/settings.py`. The repository provides two examples:
`client/settings_simple.py` and `client/settings_inky.py`.

These setting-files create three objects:

  - `secrets`: for credentials and other network related settings
  - `hw_config`: for build-specific hardware configuration
  - `app_config`: for application-specific configuration

Copy one of the template files to `client/settings.py` and adapt to
your needs.


Automatic Wakeup
----------------

To enable automatic wakeup (with refresh), you must define a time-table:

    app_config.time_table = [
      ((7,18,1),(0,59,15)),
      ((7,18,1),(0,59,15)),
      ((7,18,1),(0,59,15)),
      ((7,18,1),(0,59,15)),
      ((7,18,1),(0,59,15)),
      (None,None),
      (None,None)
  ]

The table must have one entry (line) for every day starting with Monday.
The format is

    ((h_start,h_end,h_inc),(m_start,m_end,m_inc))

This defines an hourly range from h_start to h_end with and
increment value (e.g. `1` for every hour). Within each hour, you define
at which minutes from m_start to m_end the system wakes up.

Note that all intervals are inclusive. In the example above the system
starts from 07:00 to 18:45 every fifteen minutes on Monday to Friday.

Also note that this is just an example. Updating an ACEP-e-ink every
fifteen minutes is possible, but not recommended.


Hardware Configuration
----------------------

There are two sources for hardware configuration:

  - a board-specific configuration file in `client/hal/`
  - the user/setup specific configuration in `client/settings.py`

"HAL" is an acronym for "hardware abstraction layer" and takes care
of fixed hardware on the board (e.g. led vs. neopixel for blinking). Not
every board needs a hal-file. Without a board-specific hal-file the
system uses a default, which might already be sufficient.

The name of the board-specific hal-file must be the same
as the value returned by `board.board_id` (with '.' replaced by '_').
For new boards, use one of the existing ones as a template.

The user/setup specific configuration has to provide an object
`hw_config`. Use one of the files `client/settings_xxx.py` as a
template.  In the context of this application, only two things are
necessary: a factory method for the display and a factory method for
the keypad. Both are only required if the hal-file of the board does
not already provide them. E.g. the Pimoroni Inky-Frame has a
builtin-display and a set of buttons, so for this specific display the
`hw_config` object can be empty (but it should exist).


Hacking
-------

The main program consists of an instance of `EInkApp`. You pass an
instance of your content-provider to the constructor. The content-provider
is responsible to update and process data. Necessary methods are

  - `update_data()`
  - `process_data()`
  - `handle_exception()`

See file `client/agenda.py` for the implementation of the agenda-application.
