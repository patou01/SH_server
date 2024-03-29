# SH_server

The goal of this repo is to store the server side of the "Smart home" concept. Essentially it offers two parts, one to 
log data, and one to display it.

## Server

The server logs the data. Essentially, it just listens to MQTT and stores the data in an accessible way. For now it's just
.csv to make it easy. 

### todo:
- store in a database
- run as service/daemon

## Interface

This connects to the data source and enables a simple display of the data. 

### todo:
- enable viewing as a map, based on sensor location
- Make the general interface better for plotting:
  - zooms on the plots
  - keep plots aligned on same time
  - make a big "add" button with which to add more data to plot (or less)
  - Add a way to select from/until (currently it sucks)
  - performance with changing time is bad
