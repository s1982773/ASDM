#!/usr/bin/env python3
import cgitb
import cgi
import cx_Oracle
cgitb.enable(format='text')
import numpy as np

import folium
from folium import FeatureGroup, LayerControl, Map, Marker
import json
from jinja2 import Environment, FileSystemLoader

#################################################################

def print_html():
	env = Environment(loader=FileSystemLoader('.'))
	temp = env.get_template('fringe_map.html')
	inpFol = foliumMap()
	inpVenueshow=venue_show()
	print(temp.render(map=inpFol,venueList=inpVenueshow))

##################################################################

def foliumMap():
	map_l = folium.Map(
	location=[55.9486,-3.2008],
	tiles='Stamen Terrain',
	zoom_start=14)

	venues_layer = FeatureGroup(name='Venues')
	transport_layer = FeatureGroup(name='Transport Hubs')
	walking_layer = FeatureGroup(name='Walking Tours')
	districts_layer = FeatureGroup(name='Districts')
	crowdedness_layer = FeatureGroup(name='Crowdedness Zones')
	parking_layer = FeatureGroup(name='Street Parking Zones')

	v = plotVenue()
	for i in v:
         folium.Marker(i[3:],popup=folium.Popup('Name: ' + str(i[0])+ '<br>'+ 'Show : '+str(i[1])+'<br>'+'Genre: '+str(i[2]),max_width=450)).add_to(venues_layer)

	t = plotTransport()
	for i in t:
		folium.Marker(i[2:],popup=folium.Popup('Name: ' + str(i[0])+ '<br>'+ 'Type: ' + str(i[1]),max_width=450), icon=folium.Icon(color='red')).add_to(transport_layer)

	w = plotWalkingTours()
	for i in w:
		walkingtours = json.load(i[4])
		gj = folium.GeoJson(walkingtours, style_function=lambda feature: {'color':'Red'})
		gj.add_child(folium.Popup('Walking Tour: ' +str(i[0])+'<br>'+ 'Show 1: ' + str(i[1])+'<br>'+'Show 2: '+ str(i[2])+ '<br>'+'Show 3: '+ str(i[3]),max_width=450))
		gj.add_to(walking_layer)

	d = plotDistricts()
	for i in d:
		districts = json.load(i[1])
		gj = folium.GeoJson(districts, style_function=lambda feature: {'fillColor':'Yellow'})
		gj.add_child(folium.Popup(str(i[0]),max_width=450))
		gj.add_to(districts_layer)

	c = plotCrowdedness()
	for i in c:
		crowdedness = json.load(i[1])
		#folium.GeoJson(crowdedness, style_function=lambda feature: {'fillColor':'Red'})
		gj = folium.GeoJson(crowdedness, style_function=lambda feature: {'fillColor':'Red'})
		gj.add_child(folium.Popup('Crowdedness Zone ' +str(i[0]),max_width=450))
		gj.add_to(crowdedness_layer)

	p = plotParkingZone()
	for i in p:
		crowdedness = json.load(i[4])
		gj = folium.GeoJson(crowdedness, style_function=lambda feature: {'fillColor':'Green'})
		gj.add_child(folium.Popup('Parking Zone: ' + str(i[0])+'<br>'+'Start time: '+ str(i[1])+ '<br>'+ 'End time: '+ str(i[2])+ '<br>'+'Disabled only: '+ str(i[3]),max_width=450))
		gj.add_to(parking_layer)

	venues_layer.add_to(map_l)
	transport_layer.add_to(map_l)
	walking_layer.add_to(map_l)
	districts_layer.add_to(map_l)
	crowdedness_layer.add_to(map_l)
	parking_layer.add_to(map_l)
	LayerControl().add_to(map_l)
	return map_l.get_root().render()

#################################################################

def plotVenue():
	conn = cx_Oracle.connect("S2002365/caroline58@geoslearn")
	c = conn.cursor()
	c.execute('select A."Name",B."NAME",B."GENRE", A.ORA_GEOMETRY.SDO_POINT.Y, A.ORA_GEOMETRY.SDO_POINT.X from S1982773.VENUE A, S1982773.SHOW B WHERE A."Venue_ID" = B."VENUE_ID" ')
	return c
def venue_show():
	conn = cx_Oracle.connect("S2002365/caroline58@geoslearn")
	c = conn.cursor()
	c.execute('select A."Venue_ID",A."Name",B."NAME",B."GENRE" from S1982773.VENUE A, S1982773.SHOW B WHERE A."Venue_ID" = B."VENUE_ID" ')
	li=[]
	for i in c:
		li.append(i)
	conn.close()
	attr=np.asarray(li)
	for i in attr:
		if i[0]=='1':
			i[2]=i[2]+'; India Flamenco - A Gypsy Tale'
			i[3]=i[3]+'; Dance'
		if i[0]=='2':
			i[2]=i[2]+'; Late Bloomer\'s Tale'
			i[3]=i[3]+'; Theatre'
		if i[0]=='3':
			i[2]=i[2]+'; Absolute Improv'
			i[3]=i[3]+'; Comedy'
		if i[0]=='4':
			i[2]=i[2]+'; Confetti and Chaos'
		if i[0]=='5':
			i[2]=i[2]+'; Gone Native'
			i[3]=i[3]+'; Music'
		if i[0]=='6':
			i[2]=i[2]+'; Late Bloomer\'s Tale'
			i[3]=i[3]+'; Cabaret'
		if i[0]=='7':
			i[2]=i[2]+'; Black Dog'
			i[3]=i[3]+'; Theatre'
		if i[0]=='8':
			i[2]=i[2]+'; Bodily Functions and Where to Find Them'
			i[3]=i[3]+'; Spoken Word'
		if i[0]=='9':
			i[2]=i[2]+'; Free Love Plus Guests'
			i[3]=i[3]+'; Music'
		if i[0]=='10':
			i[2]=i[2]+'; Out'
			i[3]=i[3]+'; Dance'
		if i[0]=='11':
			i[2]=i[2]+'; The 30 Year Old Virgo'
			i[3]=i[3]+'; Comedy'
		if i[0]=='12':
			i[2]=i[2]+'; Degrees of Guilt'
			i[3]=i[3]+'; Theatre'
		if i[0]=='13':
			i[2]=i[2]+'; Raven'
			i[3]=i[3]+'; Dance'
		new_attr=attr[0:-13]
		return new_attr

def plotTransport():
	conn = cx_Oracle.connect("S2002365/caroline58@geoslearn")
	c = conn.cursor()
	c.execute('select A."Name",A."Type", A.ORA_GEOMETRY.SDO_POINT.Y, A.ORA_GEOMETRY.SDO_POINT.X from S1982773.TRANSPORTHUBS A')
	return c

def plotDistricts():
	conn = cx_Oracle.connect("S2002365/caroline58@geoslearn")
	c = conn.cursor()
	c.execute('select A."District_N", SDO_UTIL.TO_GEOJSON(A.ORA_GEOMETRY) from S1982773.DISTRICTS A')
	return c

def plotWalkingTours():
	conn = cx_Oracle.connect("S2002365/caroline58@geoslearn")
	c = conn.cursor()
	c.execute('select A."Id",A."Stop_1_Sho",A."Stop_2_Sho",A."Stop_3_Sho", SDO_UTIL.TO_GEOJSON(A.ORA_GEOMETRY) from S1982773.WALKINGTOUR A')
	return c

def plotCrowdedness():
	conn = cx_Oracle.connect("S2002365/caroline58@geoslearn")
	c = conn.cursor()
	c.execute('select A."Id", SDO_UTIL.TO_GEOJSON(A.ORA_GEOMETRY) from S1982773.CROWDEDNESS A')
	return c

def plotParkingZone():
	conn = cx_Oracle.connect("S2002365/caroline58@geoslearn")
	c = conn.cursor()
	c.execute('select A."Id",A."Start_time",A."End_time",A."Disabled_o", SDO_UTIL.TO_GEOJSON(A.ORA_GEOMETRY) from S1982773.PARKINGZONE A')
	return c

if __name__ == '__main__':
	print_html()
