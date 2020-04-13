#!/usr/bin/env python3

import cx_Oracle
import cgi
import cgitb
cgitb.enable(format='text')
from jinja2 import Environment, FileSystemLoader
from operator import itemgetter

form = cgi.FieldStorage()

print("Content-type: text/html\n")

##################################################################

'''ORACLE QUERY FORM FUNCTION'''

def venue_hub_Distance():

	''' Calculates distance from venue to transport hub'''

	venue_raw = 0
	transport_raw = 0
	venue_raw = form.getvalue('venue')
	transport_raw = form.getvalue('transport') #accesses the user input value for transport hub
	venue = str(venue_raw)
	transport = str(transport_raw)

	conn = cx_Oracle.connect("S2002365/caroline58@geoslearn")
	c = conn.cursor()
	if venue_raw == None or transport_raw == None:
		query1_result = 'Please select a venue and transport hub.'        #this returns a message alerting the user if any of the form fields are left blank
	elif venue == '0' or transport == '0':
		query1_result = 'Please select a venue and transport hub.'
	else:
		c.execute(f"SELECT SDO_GEOM.SDO_DISTANCE(A.ORA_GEOMETRY, B.ORA_GEOMETRY, 0.005) AS DISTANCE FROM S1982773.TRANSPORTHUBS A, S1982773.VENUE B WHERE A.OGR_FID = {transport} AND B.OGR_FID = {venue}")
		query1_result = ''
		for i in c:
			query1_result += str(i)[1:7]
			query1_result += 'm'
	return query1_result     #returns the desired query result, which is then sent back immediately (using Jinja2 template) to populate the HTML page

##################################################################

def venue_hub_NN():

	''' Finds nearest transport hub to each venue '''

	venue_raw = 0
	venue_raw = form.getvalue('venue') #accesses the user input value for venue
	venue = str(venue_raw)

	conn = cx_Oracle.connect("S2002365/caroline58@geoslearn")
	c = conn.cursor()
	if venue_raw == None:
		nn_output = 'Please select a venue and transport hub.'        #this returns a message alerting the user if any of the form fields are left blank
	elif venue == '0':
		nn_output = 'Please select a venue and transport hub.'
	else:
		c.execute(f'''SELECT B."Name",A."Name", SDO_NN_DISTANCE(1) DIS FROM S1982773.TRANSPORTHUBS A, S1982773.VENUE B WHERE B.OGR_FID = {venue} AND SDO_NN(A.ORA_GEOMETRY, B.ORA_GEOMETRY,'SDO_NUM_RES = 1' ,1)= 'TRUE' ''')
		nn_result = []
		for i in c:
			nn_result.append(str(i))
		nn_string = str(nn_result[0])
		nn_list = nn_string.split(",")
		nn_venue = nn_list[0][2:-1]
		nn_hub = nn_list[1][2:-1]
		nn_dist = nn_list[2][:6]
		nn_output = nn_hub + ' is the nearest transport hub to ' + nn_venue + '. Distance: ' + nn_dist + 'm'
	return nn_output     #returns the desired query result, which is then sent back immediately (using Jinja2 template) to populate the HTML page

##################################################################

def tour_transport_Distance():

	'''Calculates distance between transport hubs and walking tour start and end'''

	tour_raw = 0
	transport_raw = 0
	tour_raw = form.getvalue('tour') #accesses the user input value of walking tour
	transport_raw = form.getvalue('transport') #accesses the user input value for transport hub
	tour = str(tour_raw)
	transport = str(transport_raw)

	conn = cx_Oracle.connect("S2002365/caroline58@geoslearn")
	c = conn.cursor()
	if tour_raw == None or transport_raw == None:
		start_dist = 'Please select a walking tour and transport hub.'
		end_dist = ''       #this returns a message alerting the user if any of the form fields are left blank
	elif tour == '0' or transport == '0':
		start_dist = 'Please select a walking tour and transport hub.'
		end_dist = ''
	else:
		c.execute(f"SELECT SDO_GEOM.SDO_DISTANCE(A.ORA_GEOMETRY,sdo_geometry(3001, 8192, sdo_point_type(T.X ,T.Y, null), null, null),0.01,'unit=m') AS DISTANCE FROM S1982773.TRANSPORTHUBS A, S1982773.WALKINGTOUR B,TABLE(SDO_UTIL.GETVERTICES(B.ORA_GEOMETRY)) T WHERE (T.id = '1' OR T.id = '3') AND (A.OGR_FID = {transport} AND B.OGR_FID = {tour})")
		searchresult = []
		for i in c:
			searchresult.append(str(i)[1:7])
		start_dist = 'Distance to Start of Tour: ' + str(searchresult[0]) + 'm'
		end_dist = 'Distance from End of Tour: ' + str(searchresult[1]) + 'm'
	return start_dist, end_dist

##################################################################

def tourLengthForm():
	tour_raw = 0
	tour_raw = form.getvalue('tour')
	tour = str(tour_raw)

	conn = cx_Oracle.connect("S2002365/caroline58@geoslearn")
	c = conn.cursor()
	if tour_raw == None:
		tour_length = 'Please select a walking tour.'        #this returns a message alerting the user if any of the form fields are left blank
	elif tour == '0':
		tour_length = 'Please select a walking tour.'
	else:
		c.execute(f"SELECT B.OGR_FID,SDO_GEOM.SDO_LENGTH(B.ORA_GEOMETRY,0.05,'unit=m') AS WALKINGTOUR_LENGTH FROM s1982773.WALKINGTOUR B WHERE B.OGR_FID = {tour}")

		tour_length = ''
		for i in c:
			tour_length = str(i)[1:7]
			tour_length += 'm'
	return tour_length

##################################################################

'''JINJA2 - to connect function outputs to HTML'''

#render the template
def print_html():

    ''' this function renders the template using the Jinja2 templating language, defining placeholders to send the results of the python functions to generate dynamic content in the main_page.html page '''

    env = Environment(loader=FileSystemLoader('.')) #defines the environment (folder) where to find our template ('.' specifies that the template.html file is in the same folder as the .py file)
    temp = env.get_template('fringe_distance.html') #specifies the name of the template
    inpVHdist = venue_hub_Distance()
    inpVHnn = venue_hub_NN()
    start, end = tour_transport_Distance()
    inpStart = start
    inpEnd = end
    inpLength = tourLengthForm()
    print(temp.render(vh_dist= inpVHdist, vh_nn = inpVHnn, tt_start = inpStart, tt_end = inpEnd, tour_length = inpLength))#, fields_label = inpFields_label, finds_label = inpFind_label, field_string = inpField_string, find_string = inpFind_string)) #prints the rendered HTML template

##################################################################

if __name__ == '__main__':
	print_html()
