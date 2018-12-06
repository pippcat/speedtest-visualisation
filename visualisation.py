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
from bokeh.models.glyphs import Line
from bokeh.models.markers import X
from datetime import datetime
import numpy as np
import time

FILENAME = 'data.csv'
SEPERATOR = ';'
INTERVAL = 604800

def preparePlot(name):
	# Create the plot
	plotname = "p_" + name
	plotname = bp.figure(title="Internet "+name+" speed", width=1000, height=500, x_axis_type="datetime", x_axis_label="date/time", y_axis_label="Download speed in Mb/s")
	# formatting the title
	plotname.title.text_font_size = "40px"
	# Format x-axis as datetime
	plotname.xaxis[0].formatter = DatetimeTickFormatter(days="%d.%m.%Y %H:%M:%S")
	# add the legend
	plotname.legend.location = "top_left"
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

### Create the Download plot
p_download = preparePlot("Download")
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
p_download.y_range.start = 0
p_download.y_range.end = 200

#regression = np.polyfit(logger['date_time'].astype('int')*1000, logger['bw_dl'], 1)
#r_x, r_y = zip(*((logger['date_time'], i*regression[0] + regression[1]) for i in range(len(logger))))
#p_download.line(r_x, r_y, color="black")

### Create the Upload plot
p_upload = preparePlot("Upload")
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
p_upload.y_range = p_download.y_range

### Create the Internal LAN plot
p_internal = preparePlot("Internal")
# calculating average values
internal_dl_mean = logger['internal_dl'].mean()
internal_ul_mean = logger['internal_ul'].mean()
# add tool tip
p_internal.add_tools( HoverTool(tooltips= [
	("date/time:","@ToolTipDates"),
	("internal Server to LAN bandwidth usage:","@internal_ul (avg: " + str(int(internal_ul_mean)) + ") Mb/s"),
	("internal LAN to Server bandwidth usage:","@internal_dl (avg: " + str(int(internal_dl_mean)) + ") Mb/s")
]))
# draw the lines
#p_internal.vbar(source=mySource,x="date_time",y="internal_dl",color="red",size=5,legend="Internal LAN to Server bandwidth usage in Mb/s")
#p_internal.vbar(source=mySource,x="date_time",y="internal_ul",color="blue",size=5,legend="Internal Server to LAN bandwidth usage in Mb/s")
p_internal.line(source=mySource,x="date_time",y="internal_dl",color="red",line_width=2,legend="Internal LAN to Server bandwidth usage in Mb/s")
p_internal.line(source=mySource,x="date_time",y="internal_ul",color="blue",line_width=2,legend="Internal Server to LAN bandwidth usage in Mb/s")
p_internal.x_range = p_download.x_range
p_internal.y_range = p_download.y_range

### Create the ping plot
p_ping = preparePlot("Ping")
# calculate average ping
ping_mean = logger['ping'].mean()
# draw the line
p_ping.vbar(source=mySource,x="date_time",top="ping",bottom=0,width=3600000,fill_color="darkgreen",line_color="darkgreen",legend="Ping in ms")
p_ping.add_tools( HoverTool(tooltips= [("date/time:","@ToolTipDates"),("Ping:","@ping ms"),("Avg. ping:",str(ping_mean) + " ms")]))
p_ping.x_range = p_download.x_range
p_ping.y_range = p_download.y_range

### output to line.html
bp.output_file("speedtest.html", title="Internet / LAN bandwidth visualisation") #put output_notebook() for notebook
# show result in browser
bp.save(column(p_download, p_upload, p_internal, p_ping))
