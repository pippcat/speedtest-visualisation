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
logger.columns=['datetime','ping','bw_dl','st_dl','other_dl','bw_ul','st_ul','other_ul'] # naming the columns
# formatting the date/time in the right way to be displayed correctly
logger['date_time'] = pd.to_datetime(logger.datetime.values, format="%Y-%m-%dT%H:%M:%S")
# tool tips need special treatment
logger['ToolTipDates'] = logger.date_time.map(lambda x: x.strftime("%d.%m.%Y %H:%M:%S"))

# Create a ColumnDataSource object
mySource = bp.ColumnDataSource(logger)

# Create the Download plot
p_dlspeed = bp.figure(title="Internet Download speed", width=1000, height=500, x_axis_type="datetime", x_axis_label="date/time", y_axis_label="Download speed in Mb/s")
# formatting the title
p_dlspeed.title.text_font_size = "40px"
# Format x-axis as datetime
p_dlspeed.xaxis[0].formatter = DatetimeTickFormatter(days="%d.%m.%Y %H:%M:%S")
# draw the lines
p_dlspeed.x(source=mySource,x="date_time",y="st_dl",line_width=2,color="red",legend="Speedtest download speed")
p_dlspeed.x(source=mySource,x="date_time",y="bw_dl",line_width=2,color="blue",legend="Interface download speed")
p_dlspeed.x(source=mySource,x="date_time",y="other_dl",line_width=2,color="green",legend="Other download speed")
# add the legend
p_dlspeed.legend.location = "bottom_left"

# Create the Upload plot
p_ulspeed = bp.figure(title="Internet Upload speed", width=1000, height=500, x_axis_type="datetime", x_axis_label="date/time", y_axis_label="Upload speed in Mb/s")
# formatting the title
p_ulspeed.title.text_font_size = "40px"
# Format x-axis as datetime
p_ulspeed.xaxis[0].formatter = DatetimeTickFormatter(days="%d.%m.%Y %H:%M:%S")
# draw the lines
p_ulspeed.x(source=mySource,x="date_time",y="st_ul",line_width=4,color="red",legend="Speedtest upload speed")
p_ulspeed.x(source=mySource,x="date_time",y="bw_ul",line_width=6,color="blue",legend="Interface upload speed")
p_ulspeed.x(source=mySource,x="date_time",y="other_ul",line_width=2,color="green",legend="Other upload speed")
# add the legend
p_ulspeed.legend.location = "bottom_left"

p_ping = bp.figure(title="ping", width=1000, height=500, x_axis_type="datetime", x_axis_label="date/time", y_axis_label="Ping in ms")
# formatting the title
p_ping.title.text_font_size = "40px"
# Format x-axis as datetime
p_ping.xaxis[0].formatter = DatetimeTickFormatter(days="%d.%m.%Y %H:%M:%S")
# draw the line
p_ping.x(source=mySource,x="date_time",y="ping",size=10,color="red",legend="ping in ms")
p_ping.line(source=mySource,x="date_time",y="ping",line_width=2,color="red",legend="ping in ms")
# add the legend
p_ping.legend.location = "bottom_left"

# output to line.html
bp.output_file("speedtest.html", title="Vodafone speedtest") #put output_notebook() for notebook

# show result in browser
bp.show(column(p_dlspeed, p_ulspeed, p_ping))
