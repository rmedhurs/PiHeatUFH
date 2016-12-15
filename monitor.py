#!/usr/bin/env python

import sqlite3

import os
import time
import glob
import datetime

# global variables
#speriod=(15*60)-1
speriod=60
dbname='/var/www/templog2.db'
flow_sensor     = '/sys/bus/w1/devices/28-03165563f2ff/w1_slave'
return_sensor   = '/sys/bus/w1/devices/28-0416588291ff/w1_slave'
manifold_flow_sensor = '/sys/bus/w1/devices/28-03165528bcff/w1_slave'
manifold_return_sensor = '/sys/bus/w1/devices/28-0316556dbfff/w1_slave'  
sensor_list = [flow_sensor, return_sensor, manifold_flow_sensor, manifold_return_sensor]
sensor_temperature_list = [1,2,3,4]

# store the temperature in the database
def log_temperature(flow_temp,return_temp,manifold_flow_temp,manifold_return_temp):
    timestamp = datetime.datetime.now()
    #timestamp = int(time.mktime(datetime.datetime.now().timetuple()))
    #print (timestamp)
    #query = "INSERT INTO temps(timestamp,temp1,temp2,temp3,temp4) " \
    #        "VALUES(%s,%s,%s,%s,%s)"
    #args = (datetime.datetime.now(), flow_temp, return_temp, manifold_temp, 0.0)

    conn=sqlite3.connect(dbname)
    curs=conn.cursor()

    curs.execute('''INSERT INTO temps (timestamp, temp1, temp2, temp3, temp4) 
                   VALUES (?,?,?,?,?) ''',(timestamp,flow_temp, return_temp, manifold_flow_temp, manifold_return_temp))

    # commit the changes
    conn.commit()

    conn.close()


# display the contents of the database
def display_data():

    conn=sqlite3.connect(dbname)
    curs=conn.cursor()

    for row in curs.execute("SELECT * FROM temps"):
        print (str(row[0])+"  Flow "+str(row[1])+"	Return "+str(row[2])+"	Manifold Flow "+str(row[3])+"  Manifold Ret "+str(row[4])    )

    conn.close()


def read_sensor(devicefile):
    try:
        fileobj = open(devicefile,'r')
        lines = fileobj.readlines()
        fileobj.close()
        #print (lines)
        return lines
    except:
        return None


# get temerature
# returns None on error, or the temperature as a float
def get_temp(devicefile):

    try:
    #    fileobj = open(devicefile,'r')
    #    lines = fileobj.readlines()
    #    fileobj.close()
    #except:
    #    return None
    #    print ("Reading "+devicefile)
        lines = read_sensor(devicefile)
    # get the status from the end of line 1 
        status = lines[0][-4:-1]

    # is the status is ok, get the temperature from line 2
        if status=="YES":
            tempstr= lines[1][-6:-1]
            #if tempstr=="85000":
                #print ("Error 85000")
                #return 
            tempvalue=float(tempstr)/1000
            #print ("temp is "+str(tempvalue))
            return tempvalue
        else:
            #print ("There was an error.")
            return -1
    except Exception as e:
        #print ("Exception "+e)
        return -1


# main function
# This is where the program starts 
def main():

    # enable kernel modules
    os.system('sudo modprobe w1-gpio')
    os.system('sudo modprobe w1-therm')

    # search for a device file that starts with 28
    #devicelist = glob.glob('/sys/bus/w1/devices/28*')
    #if devicelist=='':
    #    return None
    #else:
        # append /w1slave to the device file
        # w1devicefile = devicelist[0] + '/w1_slave'
    #w1devicefile = '/sys/bus/w1/devices/28-03165563f2ff/w1_slave'

while True:
    #print (sensor_list)
    for index, item in enumerate (sensor_list):
        sensor_name = item
        #print (index, item)
        sensor_readings = [0,0,0,0,0]
        for i in range(5):
            #print (sensor_name)                          ## the 1-wire temp sensors are unreliable so we take 5 readings, sort them than pick the middle one. That should eliminate high values and low ones
            sensor_readings[i]=get_temp(sensor_name)
        sensor_readings = sorted (sensor_readings)     
        #print (sensor_readings,end=" ")
        sensor_temperature_list[index]=sensor_readings[2]
    
    #print (sensor_temperature_list)    
    # get the temperature from the device file
    #flow_temperature = get_temp(flow_sensor)    
    #return_temperature = get_temp(return_sensor)
    #manifold_flow_temperature = get_temp(manifold_flow_sensor)
    #manifold_return_temperature = get_temp(manifold_return_sensor)
    


    #temperature = get_temp(w1devicefile)


    #if temperature != None:
    #    print ("temperature apple="+str(temperature))
    #else:
        # Sometimes reads fail on the first attempt
        # so we need to retry
        # temperature = get_temp(w1devicefile)
    #    print ("temperature banana="+str(temperature))

    # Store the temperature in the database
    log_temperature(sensor_temperature_list[0],sensor_temperature_list[1],sensor_temperature_list[2],sensor_temperature_list[3])

    # display the contents of the database
    #print ("Getting temps from DB")
    #display_data()

    time.sleep(speriod)


if __name__=="__main__":
    main()




