#!/usr/bin/env python3
import cgitb
import cgi
import cx_Oracle
cgitb.enable(format='text')

import folium
from folium import FeatureGroup, LayerControl, Map, Marker
import json
from jinja2 import Environment, FileSystemLoader
from operator import itemgetter

import district_filter as dist
import facilities_filter as fac
import crowdedness_filter as crowd
import streetparking_filter as street
import transport_filter as tran

print("Content-type: text/html\n")

#################################################################

def print_html():
	env = Environment(loader=FileSystemLoader('.'))
	temp = env.get_template('fringe_spatialmap.html')
	inpFol = foliumMap()
	print(temp.render(map=inpFol))

##################################################################

def BuildQuery():

	""" Function to build the SQL query based on user's choices or default """

	districts, chp1 = dist.Filter()
	facilities, chp2 = fac.Filter()
	crowdedness, chp3 = crowd.Filter()
	parking, chp4 = street.Filter()
	#chp4 = 0
	transport, chp5 = tran.Filter()
	#print(fac.Filter())

	join1 = ''
	join2 = ''
	join3 = ''
	join4 = ''

	if 1 in (chp1, chp2, chp3, chp4, chp5):
		where = ' WHERE ' # start a where statement
	else:
		where = ''

	if chp1==1 and any([chp2==1, chp3 ==1, chp4 ==1, chp5 ==1]):
		join1 = ' AND '

	if chp2==1 and any([chp3 ==1, chp4 ==1, chp5 ==1]):
		join2 = ' AND '

	if chp3==1 and any([chp4 ==1, chp5 ==1]):
		join3 = ' AND '

	if chp4==1 and chp5 ==1:
		join4 = ' AND '


	# target data
	select = 'SELECT B."Name", B.ORA_GEOMETRY.SDO_POINT.Y, B.ORA_GEOMETRY.SDO_POINT.X '
	# target table(s)
	tables = 'FROM S1982773.VENUE B'
	sql = select + tables
	filters = where + districts + join1 + facilities + join2 + crowdedness + join3 + parking + join4 + transport

	query = sql + filters
	return query

##################################################################

def foliumMap():
	query = BuildQuery()

	map_queries = folium.Map(
	location=[55.9486,-3.2008],
	tiles='Stamen Terrain',
	zoom_start=14)

	conn = cx_Oracle.connect("S2002365/caroline58@geoslearn")
	c = conn.cursor()
	c.execute(query)

	for row in c:
		folium.Marker(row[1:],popup=row[0]).add_to(map_queries)

	conn.close()

	return map_queries.get_root().render()

##################################################################


if __name__ == '__main__':
	print_html()
