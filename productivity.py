#! /usr/bin/python
# -*- coding: utf-8 -*-

# Alan's productivity vs temperature

import os
import sys
import datetime
import collections
import plotly.express as px
import plotly.graph_objects as go

if len(sys.argv) < 3:
	print(sys.argv[0] + " git_author git_project_1 git_project_2 ...")
	sys.exit(-1)

git_author = sys.argv[1]
git_projects = sys.argv[2:]

data = collections.OrderedDict()

# Read temperature data
#  This was hard to get.
#  I attempted to request the data from openweathermap, but it would have required paying for additional API access
#  I ended up requesting historical data from https://www.ncdc.noaa.gov/cdo-web/ and having to manually type it in from the PDF
#  And then manually requesting the rest of the data from wunderground
# TODO: Request all historical weather data from some service for all git commit data
year = 2019
for month, line in enumerate(open("kspf_weather.ssv", "r").read().splitlines()):
	temps = line.split()
	for day, temp in enumerate(temps):
		date = datetime.date(year = year, month = month + 1, day = day + 1)
		temp = int(temp)

		data[date] = { 'code': 0, 'temp': temp }

# Scrape git projects
#  Maybe I worked on more, these are the 3 I have been touching mostly
for project in git_projects:
	path = os.path.abspath(project)
	os.chdir(path)
	output = os.popen('git log  --date=raw --oneline --author="' + git_author + '" --pretty="@%ad"  --stat   |grep -v \| |  tr "\n" " "  |  tr "@" "\n"').read()
	for line in output.splitlines():
		chunks = line.split()
		if len(chunks) > 5:
			date = datetime.datetime.fromtimestamp(int(chunks[0])).date()
			code = int(chunks[5])

			if date in data:
				sum_code = min(data[date]['code'] + code, 100)

				data[date]['code'] = sum_code

# Remove weekends
#  Dont want those dips showing up
for date in data.keys():
	if date.weekday() >= 5:
		data.pop(date)

# Make the vectors
date_data = data.keys()
code_data = [x['code'] for x in data.values()]
temp_data = [x['temp'] for x in data.values()]

# Plot the data
fig = go.Figure()
fig.add_trace(go.Scatter(x=date_data, y=code_data, fill='tozeroy', name="LOC max 100"))
fig.add_trace(go.Scatter(x=date_data, y=temp_data, name="High °F"))
fig.update_layout(
	title=go.layout.Title(
		text="Alan's Productivity",
	),
	annotations=[
		go.layout.Annotation(
			x = datetime.date(year = 2019, month = 7, day = 22),
			y = 0,
			xref = "x",
			yref = "y",
			text = "Alan relocates",
			showarrow = True,
			arrowhead = 7,
			ax = 0,
			ay = 20
		)
	],
	xaxis=go.layout.XAxis(
		title=go.layout.xaxis.Title(
			text="Date, no weekends",
			font=dict(
				family="Courier New, monospace",
				size=18,
				color="#7f7f7f"
			)
		)
	),
	yaxis=go.layout.YAxis(
		title=go.layout.yaxis.Title(
			text="LOC & °F",
			font=dict(
				family="Courier New, monospace",
				size=18,
				color="#7f7f7f"
			)
		)
	)
)
fig.show()
