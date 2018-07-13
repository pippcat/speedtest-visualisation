Speedtest-visualization
=======================

Description
-----------

This is a small python script which generates a visualization of the Internet Up- and Download as well as the ping by using the output of speedtest-cli

Prerequisities
--------------

- speedtest-cli
- python including bokeh and pandas

Usage
-----

- Install a cronjob for speedtest-cli, e.g. "12 */1 * * * /usr/bin/speedtest-cli --csv >> /whatever/speedtest-visualization/speedtest.csv"
- Run script via python speedtest.py
- Display speedtest.html in Browser

