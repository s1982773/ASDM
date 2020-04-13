#!/usr/bin/env python3
import cgitb
import cgi
cgitb.enable(format='text')

from folium import FeatureGroup, LayerControl, Map, Marker
import json
from jinja2 import Environment, FileSystemLoader

#################################################################

def print_html():
	env = Environment(loader=FileSystemLoader('.'))
	temp = env.get_template('fringe_about.html')
	print(temp.render())

if __name__ == '__main__':
	print_html()
