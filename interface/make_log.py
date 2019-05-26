
import csv
import math as m

filename = "fake_log.csv"

timestep = 180 # seconds
duration = 48 # hours

startTime = 1558275432 # random startdate in may 2019

baseCo2 = 600
co2d = 200
baseTvoc = 10
tvocd = 5
baseT = 25
Td = 5
baseHum = 50
humd = 20
baseLux = 40
luxd = 20

steps = int(duration*60*60/timestep)

f = open(filename, 'w')
writer = csv.writer(f)


for i in range(0, steps):
    row = []
    x = i*2*m.pi/steps
    time = startTime + i*timestep
    co2 = round(baseCo2 + co2d*m.cos(x), 2)
    tvoc = round(baseTvoc + tvocd*m.sin(x), 2)
    temp = round(baseT + Td*m.cos(x)*m.sin(x), 2)
    hum = round(baseHum + humd*m.cos(2*x), 2)
    lux = round(baseLux + luxd*m.sin(2*x), 2)

    row.append(time)
    row.append(temp)
    row.append(hum)
    row.append(co2)
    row.append(tvoc)
    row.append(temp)
    row.append(hum)
    row.append(lux)

    writer.writerow(row)

f.close()
