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

# import data for diagrams
logger=pd.read_csv('speedtest.csv',sep=',',header=0,skipinitialspace=True,usecols=[3,4,6,7])
logger.columns=['datetime','ping','download','upload'] # naming the columns
logger['download'] = logger['download'].apply(lambda x: x/1000000)
logger['upload'] = logger['upload'].apply(lambda x: x/1000000)
# formatting the date/time in the right way to be displayed correctly
logger['date_time'] = pd.to_datetime(logger.datetime.values, format="%Y-%m-%dT%H:%M:%S")
# tool tips need special treatment
logger['ToolTipDates'] = logger.date_time.map(lambda x: x.strftime("%d.%m.%Y %H:%M:%S"))

# Create a ColumnDataSource object
mySource = bp.ColumnDataSource(logger)

# Create the Upload / Download plot
p_speed = bp.figure(title="Upload/Download speed", width=1000, height=500, x_axis_type="datetime", x_axis_label="date/time", y_axis_label="Upload/Download speed in MB/s")
# formatting the title
p_speed.title.text_font_size = "40px"
# Format x-axis as datetime
p_speed.xaxis[0].formatter = DatetimeTickFormatter(days="%d.%m.%Y %H:%M:%S")
# draw the lines
p_speed.x(source=mySource,x="date_time",y="download",line_width=2,color="red",legend="download speed")
p_speed.x(source=mySource,x="date_time",y="upload",line_width=2,color="blue",legend="upload speed")
# add the legend
p_speed.legend.location = "bottom_left"

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
bp.show(column(p_speed, p_ping))
