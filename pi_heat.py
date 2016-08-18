import sys
from sensors import W1ThermSensor

TemperatureSensors = W1ThermSensor()
#scommand = input("Press any key to continue ")
#sensors = TemperatureSensors.get_available_sensors()
for s in TemperatureSensors.get_available_sensors():
    temp = s.get_temperature()
    print (s.id + " " + s.type_name + " " + str(temp) + " " + str(round(temp,1)) + "C")
    print "oh shit"