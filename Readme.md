Speedtest-visualization
=======================

Description
-----------

Those small python scripts are made to visualize the internal and external traffic of a server. It also does a speedtest, therefore the maximum internet bandwidth is displayed as well.

Prerequisities
--------------

- `python3` including `bokeh`, `pandas`, `queue` and `speedtest-cli`

Usage
-----

- Run script via `python3 bandwidthlogger.py`
- Or install a cronjob for speedtest-cli, e.g. `12 */1 * * * /usr/bin/python3 /path/to/script/bandwidthlogger.py >> /dev/null`
- Display speedtest.html in Browser

