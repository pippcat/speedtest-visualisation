#!/usr/bin/env python3
#-*- coding: utf-8 -*-

# visualization of speedtest data
# made by pippcat (sendyourspamhere@posteo.de)
# public domain

### import libraries
import pandas as pd # for CSV import
import bokeh.plotting as bp
import numpy as np
import time
from bokeh.io import output_file, curdoc
from bokeh.layouts import column, gridplot
from bokeh.models import HoverTool, DatetimeTickFormatter, ColumnDataSource
from bokeh.models.glyphs import Line
from bokeh.themes import built_in_themes

### common variables
FILENAME = 'data.csv'
SEPERATOR = ';'
INTERVAL = 604800 # in seconds
TITLE = '2n40 Internet bandwidth visualisation'

### common plot preparation function
def preparePlot(name):
	# Create the plot
	plotname = "p_" + name
	plotname = bp.figure(width=500, height=500, x_axis_type="datetime", tools="xpan,xwheel_zoom,reset", active_scroll="xwheel_zoom")
	plotname.sizing_mode='stretch_both'
	# formatting the title
	plotname.title.text_font_size = "30px"
	# Format x-axis as datetime
	plotname.xaxis[0].formatter = DatetimeTickFormatter(days="%d.%m.%Y")
	plotname.title.text_font_size = "20px"
	return plotname

### Data preparation
# import data
logger=pd.read_csv(FILENAME,sep=SEPERATOR,header=1,skipinitialspace=True)
logger.columns=['datetime','ping','bw_dl','st_dl','other_dl','internal_dl','bw_ul','st_ul','other_ul','internal_ul'] # naming the columns
# formatting the date/time in the right way to be displayed correctly
logger['date_time'] = pd.to_datetime(logger.datetime.values, format="%Y-%m-%d %H:%M:%S")
logger7d = logger[-168:] # 24h x last week
# tool tips need special treatment
logger['ToolTipDates'] = logger.date_time.map(lambda x: x.strftime("%d.%m.%Y %H:%M:%S"))
# Create a ColumnDataSource object
mySource = bp.ColumnDataSource(logger)

### Calculations
bw_dl_mean = logger['bw_dl'].mean()
bw_dl_mean7d = logger7d['bw_dl'].mean()
st_dl_mean = logger['st_dl'].mean()
st_dl_mean7d = logger7d['st_dl'].mean()
other_dl_mean = logger['other_dl'].mean()
other_dl_mean7d = logger7d['other_dl'].mean()
mean_x = [logger['date_time'].min(), logger['date_time'].max()]
mean_x7d = [logger7d['date_time'].min(), logger['date_time'].max()]
bw_dl_mean_y = [bw_dl_mean, bw_dl_mean]
bw_dl_mean_y7d = [bw_dl_mean7d, bw_dl_mean7d]
bw_ul_mean = logger['bw_ul'].mean()
bw_ul_mean7d = logger7d['bw_ul'].mean()
bw_ul_mean_y = [bw_ul_mean, bw_ul_mean]
bw_ul_mean_y7d = [bw_ul_mean7d, bw_ul_mean7d]
st_ul_mean = logger['st_ul'].mean()
st_ul_mean7d = logger7d['st_ul'].mean()
other_ul_mean = logger['other_ul'].mean()
other_ul_mean7d = logger7d['other_ul'].mean()
internal_dl_mean = logger['internal_dl'].mean()
internal_ul_mean = logger['internal_ul'].mean()
ping_mean = logger['ping'].mean()
ping_mean7d = logger7d['ping'].mean()
ping_mean_y = [ping_mean, ping_mean]
ping_mean_y7d = [ping_mean7d, ping_mean7d]

### Download plot
p_download = preparePlot("Download")
p_download.title.text = "Download speed"
p_download.yaxis.axis_label = "Download speed in Mb/s"
p_download.vbar(source=mySource,x="date_time",top="bw_dl",bottom="st_dl",width=3600000,fill_color="salmon",line_color="salmon",legend_label="Interface download speed")
p_download.vbar(source=mySource,x="date_time",top="st_dl",bottom="other_dl",width=3600000,fill_color="red",line_color="red",legend_label="Speedtest download speed")
p_download.vbar(source=mySource,x="date_time",top="other_dl",bottom=0,width=3600000,fill_color="darkred",line_color="darkred",legend_label="Other download speed")
p_download.line(mean_x7d, bw_dl_mean_y7d, line_color='darkred', line_width=4, legend_label="last week bandwidth average")
p_download.line(mean_x, bw_dl_mean_y, line_color='white', line_width=4, legend_label="all time bandwidth average")
# interval in seconds / unixtime; bokeh uses milliseconds
p_download.x_range.start = (time.time()-INTERVAL)*1000
p_download.x_range.end = (time.time()+7200)*1000
p_download.legend.location = "top_left"
p_download.legend.background_fill_alpha = 0.7
p_download.legend.label_text_font_size = '10pt'
# add the tool tip
p_download.add_tools( HoverTool(tooltips= [
("date/time","@ToolTipDates"),
("format","selected (last week avg./all time avg)"),
("interface download","@bw_dl{000} (" + str(int(bw_dl_mean7d)).zfill(3) + "/" + str(int(bw_dl_mean)).zfill(3) + ") Mb/s"),
("speedtest download","@st_dl{000} (" + str(int(st_dl_mean7d)).zfill(3) + "/" + str(int(st_dl_mean)).zfill(3) + ") Mb/s"),
("other download","@other_dl{000} (" + str(int(other_dl_mean7d)).zfill(3) + "/" + str(int(other_dl_mean)).zfill(3) + ") Mb/s"),
]))

### Upload plot
p_upload = preparePlot("Upload")
p_upload.title.text = "Upload speed"
p_upload.yaxis.axis_label = "Upload speed in Mb/s"
p_upload.vbar(source=mySource,x="date_time",top="bw_ul",bottom="st_ul",width=3600000,fill_color="lightskyblue",line_color="lightskyblue",legend_label="Interface upload speed")
p_upload.vbar(source=mySource,x="date_time",top="st_ul",bottom="other_ul",width=3600000,fill_color="deepskyblue",line_color="deepskyblue",legend_label="Speedtest upload speed")
p_upload.vbar(source=mySource,x="date_time",top="other_ul",bottom=0,width=3600000,fill_color="dodgerblue",line_color="dodgerblue",legend_label="Other upload speed")
p_upload.line(mean_x7d, bw_ul_mean_y7d, line_color='blue', line_width=4, legend_label="last week bandwidth average")
p_upload.line(mean_x, bw_ul_mean_y, line_color='white', line_width=4, legend_label="all time bandwidth average")
p_upload.x_range = p_download.x_range
p_upload.y_range.end = 60
p_upload.legend.location = "top_left"
p_upload.legend.background_fill_alpha = 0.7
p_upload.legend.label_text_font_size = '10pt'
# add the tool tip
p_upload.add_tools( HoverTool(tooltips= [
("date/time","@ToolTipDates"),
("format","selected (last week avg./all time avg)"),
("interface upload","@bw_ul{00} (" + str(int(bw_ul_mean7d)).zfill(2) + "/" + str(int(bw_ul_mean)).zfill(2) + ") Mb/s"),
("speedtest upload","@st_ul{00} (" + str(int(st_ul_mean7d)).zfill(2) + "/" + str(int(st_ul_mean)).zfill(2) + ") Mb/s"),
("other upload","@other_ul{00} (" + str(int(other_ul_mean7d)).zfill(2) + "/" + str(int(other_ul_mean)).zfill(2) + ") Mb/s")
]))

## Internal LAN plot
p_internal = preparePlot("Internal")
p_internal.title.text = "Internal bandwidth usage"
p_internal.yaxis.axis_label = "Upload/Download speed in Mb/s"
p_internal.line(source=mySource,x="date_time",y="internal_dl",color="red",line_width=5,legend_label="Internal LAN to Server bandwidth usage in Mb/s")
p_internal.line(source=mySource,x="date_time",y="internal_ul",color="blue",line_width=5,legend_label="Internal Server to LAN bandwidth usage in Mb/s")
p_internal.x_range = p_download.x_range
p_internal.legend.location = "top_left"
p_internal.legend.background_fill_alpha = 0.7
p_internal.legend.label_text_font_size = '10pt'
p_internal.add_tools( HoverTool(tooltips= [
("date/time:","@ToolTipDates"),
("internal Server to LAN bandwidth usage:","@internal_ul (avg: " + str(int(internal_ul_mean)) + ") Mb/s"),
("internal LAN to Server bandwidth usage:","@internal_dl (avg: " + str(int(internal_dl_mean)) + ") Mb/s")
]))

### Ping plot
p_ping = preparePlot("Ping")
p_ping.title.text = "Ping"
p_ping.yaxis.axis_label = "Ping in ms"
p_ping.vbar(source=mySource,x="date_time",top="ping",bottom=0,width=3600000,fill_color="lime",line_color="darkgreen",legend_label="Ping in ms")
p_ping.x_range = p_download.x_range
p_ping.y_range.start = 0
p_ping.y_range.end = 200
p_ping.legend.location = "top_left"
p_ping.line(mean_x7d, ping_mean_y7d, line_color='purple', line_width=4, legend_label="last week ping average")
p_ping.line(mean_x, ping_mean_y, line_color='white', line_width=4, legend_label="all time ping average")
p_ping.legend.background_fill_alpha = 0.7
p_ping.legend.label_text_font_size = '10pt'
p_ping.add_tools( HoverTool(tooltips= [
("date/time:","@ToolTipDates"),
("Ping:","@ping{00.0} ms"),
("Last week avg. ping:",str(ping_mean7d).zfill(2) + " ms"),
("All time avg. ping:",str(ping_mean).zfill(2) + " ms")]))

### output to HTML file
bp.output_file("speedtest.html", title=TITLE)
curdoc().theme = 'dark_minimal'
plots=gridplot([[p_download, p_upload],[p_internal, p_ping]], sizing_mode='scale_both', toolbar_location='right')
page = column(plots, sizing_mode='stretch_width')
bp.save(page)
