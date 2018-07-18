#!/usr/bin/env python
#-*- coding: utf-8 -*-

# visualization of speedtest data
# made by Tommy Schönherr (t.schoenherr@hzdr.de)
# public domain

# import libraries
import pandas as pd # for CSV import
import bokeh.plotting as bp
from bokeh.layouts import column, widgetbox
from bokeh.models import LinearAxis, Range1d, HoverTool, DatetimeTickFormatter, ColumnDataSource
from bokeh.models.widgets import DataTable, DateFormatter, TableColumn 
from bokeh.models.markers import X
from datetime import datetime 

FILENAME = 'data.csv'
SEPERATOR = ';'

# import data for diagrams
logger=pd.read_csv(FILENAME,sep=SEPERATOR,header=1,skipinitialspace=True)
logger.columns=['datetime','ping','bw_dl','st_dl','other_dl','internal_dl','bw_ul','st_ul','other_ul','internal_ul'] # naming the columns
# formatting the date/time in the right way to be displayed correctly
logger['date_time'] = pd.to_datetime(logger.datetime.values, format="%Y-%m-%d %H:%M:%S")
# tool tips need special treatment
logger['ToolTipDates'] = logger.date_time.map(lambda x: x.strftime("%d.%m.%Y %H:%M:%S"))

# Create a ColumnDataSource object
mySource = bp.ColumnDataSource(logger)

# Create the Download plot
p_download = bp.figure(title="Internet download speed", width=1000, height=500, x_axis_type="datetime", x_axis_label="date/time", y_axis_label="Download speed in Mb/s")
# formatting the title
p_download.title.text_font_size = "40px"
# Format x-axis as datetime
p_download.xaxis[0].formatter = DatetimeTickFormatter(days="%d.%m.%Y %H:%M:%S")
# draw the lines
p_download.x(source=mySource,x="date_time",y="bw_dl",color="darkred",size=4,legend="Interface download speed")
p_download.line(source=mySource,x="date_time",y="bw_dl",color="darkred",line_width=2,legend="Interface download speed")
p_download.x(source=mySource,x="date_time",y="st_dl",color="red",size=4,legend="Speedtest download speed")
p_download.line(source=mySource,x="date_time",y="st_dl",color="red",line_width=2,legend="Speedtest download speed")
p_download.x(source=mySource,x="date_time",y="other_dl",color="salmon",size=4,legend="Other download speed")
p_download.line(source=mySource,x="date_time",y="other_dl",color="salmon",line_width=2,legend="Other download speed")
# add the legend
p_download.legend.location = "bottom_left"

# Create the Download plot
p_upload = bp.figure(title="Internet upload speed", width=1000, height=500, x_axis_type="datetime", x_axis_label="date/time", y_axis_label="Upload speed in Mb/s")
# formatting the title
p_upload.title.text_font_size = "40px"
# Format x-axis as datetime
p_upload.xaxis[0].formatter = DatetimeTickFormatter(days="%d.%m.%Y %H:%M:%S")
# draw the lines
p_upload.x(source=mySource,x="date_time",y="bw_ul",color="darkblue",size=4,legend="Interface upload speed")
p_upload.line(source=mySource,x="date_time",y="bw_ul",color="darkblue",line_width=2,legend="Interface upload speed")
p_upload.x(source=mySource,x="date_time",y="st_ul",color="blue",size=4,legend="Speedtest upload speed")
p_upload.line(source=mySource,x="date_time",y="st_ul",color="blue",line_width=2,legend="Speedtest upload speed")
p_upload.x(source=mySource,x="date_time",y="other_ul",color="lightblue",size=4,legend="Other upload speed")
p_upload.line(source=mySource,x="date_time",y="other_ul",color="lightblue",line_width=2,legend="Other upload speed")
# add the legend
p_upload.legend.location = "bottom_left"

# Create the Internal LAN plot
p_internal = bp.figure(title="Internal LAN usage", width=1000, height=500, x_axis_type="datetime", x_axis_label="date/time", y_axis_label="Download/Upload speed in Mb/s")
# formatting the title
p_internal.title.text_font_size = "40px"
# Format x-axis as datetime
p_internal.xaxis[0].formatter = DatetimeTickFormatter(days="%d.%m.%Y %H:%M:%S")
# draw the lines
p_internal.x(source=mySource,x="date_time",y="internal_dl",color="red",size=4,legend="Internal LAN to Server bandwidth usage in Mb/s")
p_internal.line(source=mySource,x="date_time",y="internal_dl",color="red",line_width=2,legend="Internal LAN to Server bandwidth usage in Mb/s")
p_internal.x(source=mySource,x="date_time",y="internal_ul",color="blue",size=4,legend="Internal Server to LAN bandwidth usage in Mb/s")
p_internal.line(source=mySource,x="date_time",y="internal_ul",color="blue",line_width=2,legend="Internal Server to LAN bandwidth usage in Mb/s")
# add the legend
# add the legend
p_internal.legend.location = "bottom_left"

p_ping = bp.figure(title="Ping", width=1000, height=500, x_axis_type="datetime", x_axis_label="date/time", y_axis_label="Ping in ms")
# formatting the title
p_ping.title.text_font_size = "40px"
# Format x-axis as datetime
p_ping.xaxis[0].formatter = DatetimeTickFormatter(days="%d.%m.%Y %H:%M:%S")
# draw the line
p_ping.x(source=mySource,x="date_time",y="ping",size=10,color="darkgreen",legend="ping in ms")
p_ping.line(source=mySource,x="date_time",y="ping",line_width=2,color="darkgreen",legend="ping in ms")
# add the legend
p_ping.legend.location = "bottom_left"

# output to line.html
bp.output_file("speedtest.html", title="Internet / LAN bandwidth visualisation") #put output_notebook() for notebook

# show result in browser
bp.save(column(p_download, p_upload, p_internal, p_ping))
