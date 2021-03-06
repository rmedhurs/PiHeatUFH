#!/usr/bin/env python

import sqlite3
import sys
import cgi
import cgitb


# global variables
speriod=(15*60)-1
dbname='/var/www/templog2.db'



# print the HTTP header
def printHTTPheader():
    print "Content-type: text/html\n\n"



# print the HTML head section
# arguments are the page title and the table for the chart
def printHTMLHead(title, table):
    print "<head>"
    print "    <title>"
    print title
    print "    </title>"
    
    print_graph_script(table)

    print "</head>"


# get data from the database
# if an interval is passed, 
# return a list of records from the database
def get_data(interval):

    conn=sqlite3.connect(dbname,detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    curs=conn.cursor()

    if interval == None:
        curs.execute("SELECT * FROM temps")
    else:

#curs.execute("SELECT (julianday(timestamp)-2440587)*86400000,temp1,temp2,temp3,temp4 FROM temps WHERE timestamp>datetime('now','-%s hours')" % interval)
        curs.execute("SELECT timestamp as \"[timestamp]\",temp1,temp2,temp3,temp4 FROM temps WHERE timestamp>datetime('now','-%s hours')" % interval)
#        curs.execute("SELECT * FROM temps WHERE timestamp>datetime('2013-09-19 21:30:02','-%s hours') AND timestamp<=datetime('2013-09-19 21:31:02')" % interval)

    rows=curs.fetchall()

    conn.close()
    #sys.stderr.write (rows)
    return rows


# convert rows from database into a javascript table
def create_table(rows):
    ## If we couldn't get a reading from the sensor the db will have a value None
    ## hack at the moment is to skip this entry completely, ideally we just ignore the bad value.
    chart_table=""
    #rowstr=""
    for row in rows[:-1]:
        badtemp=False
        date_int = int(row[0].strftime("%s"))*1000 # convert date object into seconds since epoch, multiple by 1000 as javascript expects milliseconds
                                                   # we use epoch seconds because python dates have Jan = 1, javascript Jan=0 what a PITA
        date_str = "Date("+str(date_int)+")"       # now format the string to be Date(xxxxxxxxxxx)
        #print(date_str+"<BR>")
        rowstr="['{0}', {1}, {2}, {3}, {4}],\n".format(date_str,str(row[1]),str(row[2]),str(row[3]),str(row[4]))
        if (str(row[1]) == "85" or str(row[1]) == "85" or str(row[3]) == "85" or str(row[4]) == "85"):
            badtemp=True
        if (not ("None" in rowstr)) and  badtemp==False:
            chart_table+=rowstr
        else:
            # One of the values read from the DB is incorrect (85C) so we just skip this entry
            # The google chart will interpolate the values for us
            print("Error in DB entry "+rowstr+"<BR>") # debug

    row=rows[-1]
    #rowstr="['{0}', {1}]\n".format(str(row[0]),str(row[1]))
    #rowstr="['{0}', {1}, {2}, {3}, {4}],\n".format(str(row[0]),str(row[1]),str(row[2]),str(row[3]),str(row[4]))
    #chart_table+=rowstr

    return chart_table


# print the javascript to generate the chart
# pass the table generated from the database info
def print_graph_script(table):

    # google chart snippet
    chart_code="""
    <script type="text/javascript" src="https://www.google.com/jsapi"></script>
    <script type="text/javascript">
      google.load("visualization", "1", {packages:["corechart"]});
      google.setOnLoadCallback(drawChart);
      function drawChart() {
        var data = google.visualization.arrayToDataTable([
          [ {label: 'Time',     id: 'Time',     type: 'datetime'}, <!-- timeofday
            {label: 'Flow',     id: 'Flow',     type: 'number'},
            {label: 'Return',   id: 'Return',   type: 'number'},
            {label: 'Mainfold Flow',   id: 'Manifold Flow',   type: 'number'},
            {label: 'Manifold Return', id: 'Manifold Return', type: 'number'}],
%s]);        

        var options = {
          title: 'Temperature',
          curveType: 'function', 
          series: {
            0: {color: '#ff0000'}, <!-- Set Flow to Red
            1: {color: '#0000ff'}  <!-- Set Return to Blue
          },
          hAxis: {
            format: "HH:mm",
          },
          vAxis: {
            baseline: 25,
            gridlines: {count:8},
            minorGridlines: {count:2},
            minValue: 20
          }
        };

        var chart = new google.visualization.LineChart(document.getElementById('chart_div'));
        chart.draw(data, options);
      }
    </script>"""

    print chart_code % (table)




# print the div that contains the graph
def show_graph():
    print "<h2>Temperature Chart</h2>"
    print '<div id="chart_div" style="width: 900px; height: 500px;"></div>'



# connect to the db and show some stats
# argument option is the number of hours
def show_stats(option):

    conn=sqlite3.connect(dbname)
    curs=conn.cursor()

    if option is None:
        option = str(24)

    curs.execute("SELECT timestamp,max(temp1) FROM temps WHERE timestamp>datetime('now','-%s hour') AND timestamp<=datetime('now')" % option)
    rowmax=curs.fetchone()
    rowstrmax="{0}&nbsp&nbsp&nbsp{1}C".format(str(rowmax[0]),str(rowmax[1]))

    curs.execute("SELECT timestamp,min(temp1) FROM temps WHERE timestamp>datetime('now','-%s hour') AND timestamp<=datetime('now')" % option)
    rowmin=curs.fetchone()
    rowstrmin="{0}&nbsp&nbsp&nbsp{1}C".format(str(rowmin[0]),str(rowmin[1]))

    curs.execute("SELECT avg(temp1) FROM temps WHERE timestamp>datetime('now','-%s hour') AND timestamp<=datetime('now')" % option)
    rowavg=curs.fetchone()


    print "<hr>"


    print "<h2>Minumum temperature&nbsp</h2>"
    print rowstrmin
    print "<h2>Maximum temperature</h2>"
    print rowstrmax
    print "<h2>Average temperature</h2>"
    print "%.3f" % rowavg+"C"

    print "<hr>"

    print "<h2>In the last hour:</h2>"
    print "<table>"
    print "<tr><td><strong>Date/Time</strong></td><td><strong>Temperature</strong></td></tr>"

    rows=curs.execute("SELECT * FROM temps WHERE timestamp>datetime('new','-1 hour') AND timestamp<=datetime('new')")
    #rows=curs.execute("SELECT * FROM temps WHERE timestamp>datetime('2013-09-19 21:30:02','-1 hour') AND timestamp<=datetime('2013-09-19 21:31:02')")
    for row in rows:
        rowstr="<tr><td>{0}&emsp;&emsp;</td><td>{1}C</td></tr>".format(str(row[0]),str(row[1]))
        print rowstr
    print "</table>"

    print "<hr>"

    conn.close()




def print_time_selector(option):

    print """<form action="/cgi-bin/webgui.py" method="POST">
        Show the temperature logs for  
        <select name="timeinterval">"""


    if option is not None:

        if option == "1":
            print "<option value=\"1\" selected=\"selected\">the last hour</option>"
        else:
            print "<option value=\"1\">the last hour</option>"

        if option == "2":
            print "<option value=\"2\" selected=\"selected\">the last 2 hours</option>"
        else:
            print "<option value=\"2\">the last 2 hours</option>"

        if option == "4":
            print "<option value=\"4\" selected=\"selected\">the last 4 hours</option>"
        else:
            print "<option value=\"4\">the last 4 hours</option>"

        if option == "6":
            print "<option value=\"6\" selected=\"selected\">the last 6 hours</option>"
        else:
            print "<option value=\"6\">the last 6 hours</option>"
        if option == "24":
            print "<option value=\"24\" selected=\"selected\">the last 24 hours</option>"
        else:
            print "<option value=\"24\">the last 24 hours</option>"

    else:
        print """<option value="6">the last 6 hours</option>
            <option value="12">the last 12 hours</option>
            <option value="24" selected="selected">the last 24 hours</option>"""

    print """        </select>
        <input type="submit" value="Display">
    </form>"""


# check that the option is valid
# and not an SQL injection
def validate_input(option_str):
    # check that the option string represents a number
    if option_str.isalnum():
        # check that the option is within a specific range
        if int(option_str) > 0 and int(option_str) <= 24:
            return option_str
        else:
            return None
    else: 
        return None


#return the option passed to the script
def get_option():
    form=cgi.FieldStorage()
    if "timeinterval" in form:
        option = form["timeinterval"].value
        return validate_input (option)
    else:
        return None




# main function
# This is where the program starts 
def main():

    cgitb.enable()

    # get options that may have been passed to this script
    option=get_option()

    if option is None:
        option = str(24)

    # get data from the database
    records=get_data(option)

    # print the HTTP header
    printHTTPheader()

    if len(records) != 0:
        # convert the data into a table
        table=create_table(records)
    else:
        print "No data found"
        return

    # start printing the page
    print "<html>"
    # print the head section including the table
    # used by the javascript for the chart
    printHTMLHead("Raspberry Pi Temperature Logger", table)

    # print the page body
    print "<body>"
    print "<h1>Raspberry Pi Temperature Logger</h1>"
    print "<hr>"
    print_time_selector(option)
    show_graph()
    show_stats(option)
    print "</body>"
    print "</html>"

    sys.stdout.flush()

if __name__=="__main__":
    main()




