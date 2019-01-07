#!/usr/bin/env python
#-*- coding: utf-8 -*-

# visualization of speedtest data
# made by pippcat (sendyourspamhere@posteo.de)
# public domain

### import libraries
import pandas as pd # for CSV import
import bokeh.plotting as bp
from bokeh.layouts import column, widgetbox
from bokeh.models import LinearAxis, Range1d, HoverTool, DatetimeTickFormatter, ColumnDataSource, Range
from bokeh.models.widgets import DataTable, DateFormatter, TableColumn, Div
from bokeh.models.glyphs import Line
from bokeh.models.markers import X
from datetime import datetime
import numpy as np
import time

### common variables
FILENAME = 'data.csv'
SEPERATOR = ';'
INTERVAL = 604800 # in seconds
TITLE = '2n40 Internet bandwidth visualisation'

### common plot preparation function
def preparePlot(name):
	# Create the plot
	plotname = "p_" + name
	plotname = bp.figure(width=3000, height=500, x_axis_type="datetime", x_axis_label="date/time", tools="xpan,xwheel_zoom,reset", active_scroll="xwheel_zoom")
	plotname.sizing_mode='scale_width'
	# formatting the title
	plotname.title.text_font_size = "30px"
	# Format x-axis as datetime
	plotname.xaxis[0].formatter = DatetimeTickFormatter(days="%d.%m.%Y %H:%M:%S")
	return plotname

### Data preparation
# import data for diagrams
logger=pd.read_csv(FILENAME,sep=SEPERATOR,header=1,skipinitialspace=True)
logger.columns=['datetime','ping','bw_dl','st_dl','other_dl','internal_dl','bw_ul','st_ul','other_ul','internal_ul'] # naming the columns
# formatting the date/time in the right way to be displayed correctly
logger['date_time'] = pd.to_datetime(logger.datetime.values, format="%Y-%m-%d %H:%M:%S")
# tool tips need special treatment
logger['ToolTipDates'] = logger.date_time.map(lambda x: x.strftime("%d.%m.%Y %H:%M:%S"))
# Create a ColumnDataSource object
mySource = bp.ColumnDataSource(logger)

### Header and Footer
header = Div(text='''<h1 style="text-align:center;font-size:40px;">'''+TITLE+'''</h1>''')
footer = Div(text='''<p style="text-align:right;font-size:12px;font-style:italic;">Sourcecode can be found on <a href="https://www.github.com/pippcat/speedtest-visualisation" target="_blank">GitHub</a></p>''')

### Create the Download plot
p_download = preparePlot("Download")
p_download.title.text = "Download speed"
p_download.yaxis.axis_label = "Download speed in Mb/s"
# calculating average values
bw_dl_mean = logger['bw_dl'].mean()
st_dl_mean = logger['st_dl'].mean()
other_dl_mean = logger['other_dl'].mean()
p_download.vbar(source=mySource,x="date_time",top="bw_dl",bottom="st_dl",width=3600000,fill_color="darkred",line_color="darkred",legend="Interface download speed")
p_download.vbar(source=mySource,x="date_time",top="st_dl",bottom="other_dl",width=3600000,fill_color="red",line_color="red",legend="Speedtest download speed")
p_download.vbar(source=mySource,x="date_time",top="other_dl",bottom=0,width=3600000,fill_color="salmon",line_color="salmon",legend="Other download speed")
# add the tool tip
p_download.add_tools( HoverTool(tooltips= [
("date/time:","@ToolTipDates"),
	("interface download:","@bw_dl (avg: " + str(int(bw_dl_mean)) + ") Mbit/s"),
	("speedtest download:","@st_dl (avg: " + str(int(st_dl_mean)) + ") Mb/s"),
	("other download:","@other_dl (avg: " + str(int(other_dl_mean)) + ") Mb/s")
]))
# interval in seconds / unixtime; bokeh uses milliseconds
p_download.x_range.start = (time.time()-INTERVAL)*1000
p_download.x_range.end = time.time()*1000+7200
p_download.legend.location = "top_left"

### Create the Upload plot
p_upload = preparePlot("Upload")
p_upload.title.text = "Upload speed"
p_upload.yaxis.axis_label = "Upload speed in Mb/s"
# calculating average values
bw_ul_mean = logger['bw_ul'].mean()
st_ul_mean = logger['st_ul'].mean()
other_ul_mean = logger['other_ul'].mean()
p_upload.vbar(source=mySource,x="date_time",top="bw_ul",bottom="st_ul",width=3600000,fill_color="darkblue",line_color="darkblue",legend="Interface upload speed")
p_upload.vbar(source=mySource,x="date_time",top="st_ul",bottom="other_ul",width=3600000,fill_color="blue",line_color="blue",legend="Speedtest upload speed")
p_upload.vbar(source=mySource,x="date_time",top="other_ul",bottom=0,width=3600000,fill_color="lightblue",line_color="lightblue",legend="Other upload speed")
# add the tool tip
p_upload.add_tools( HoverTool(tooltips= [
	("date/time:","@ToolTipDates"),
	("interface upload:","@bw_ul (avg: " + str(int(bw_ul_mean)) + ") Mb/s"),
    	("speedtest upload:","@st_ul (avg: " + str(int(st_ul_mean)) + ") Mb/s"),
	("other upload:","@other_ul (avg: " + str(int(other_ul_mean)) + ") Mb/s")
]))
p_upload.x_range = p_download.x_range
p_upload.legend.location = "top_left"

## Create the Internal LAN plot
p_internal = preparePlot("Internal")
# calculating average values
internal_dl_mean = logger['internal_dl'].mean()
internal_ul_mean = logger['internal_ul'].mean()

p_internal.add_tools( HoverTool(tooltips= [
	("date/time:","@ToolTipDates"),
	("internal Server to LAN bandwidth usage:","@internal_ul (avg: " + str(int(internal_ul_mean)) + ") Mb/s"),
	("internal LAN to Server bandwidth usage:","@internal_dl (avg: " + str(int(internal_dl_mean)) + ") Mb/s")
]))
p_internal.line(source=mySource,x="date_time",y="internal_dl",color="red",line_width=2,legend="Internal LAN to Server bandwidth usage in Mb/s")
p_internal.line(source=mySource,x="date_time",y="internal_ul",color="blue",line_width=2,legend="Internal Server to LAN bandwidth usage in Mb/s")
p_internal.x_range = p_download.x_range

### Create the ping plot
p_ping = preparePlot("Ping")
p_ping.title.text = "Ping"
p_ping.yaxis.axis_label = "Ping in ms"
# calculate average ping
ping_mean = logger['ping'].mean()
# draw the line
p_ping.vbar(source=mySource,x="date_time",top="ping",bottom=0,width=3600000,fill_color="darkgreen",line_color="darkgreen",legend="Ping in ms")
p_ping.add_tools( HoverTool(tooltips= [("date/time:","@ToolTipDates"),("Ping:","@ping ms"),("Avg. ping:",str(ping_mean) + " ms")]))
p_ping.x_range = p_download.x_range
p_ping.legend.location = "top_left"

### output to HTML file
bp.output_file("speedtest.html", title=TITLE) #put output_notebook() for notebook
page = column(children=[header,p_download, p_upload, p_ping, p_internal, footer], sizing_mode='scale_width')
bp.save(page)
