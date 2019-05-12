import paho.mqtt.client as mqtt #import the client
import time
import csv
import calendar
import re
import threading


class mqtt_sh_server:

	def __init__(self, ip):
		self.broker_address = ip
		self.client = mqtt.Client("pi") #create new instance
		self.client.connect(self.broker_address) #connect to broker

		self.client.subscribe("Patrick")
		self.client.on_message = self.temp_callback



		clientloop_thread = threading.Thread(target=self.connect, daemon=True)
		clientloop_thread.start()
		print("Started server with broker address " + self.broker_address)

	def connect(self):
		self.client.loop_forever()
		
	def temp_callback(client, userdata, message):
			msg = str(message.payload.decode("utf-8"))
			print("Received a msg \n")
			print("message received " , msg)
	#        print(msg.split(' , '))
	#        parsed = re.findall(r"[-+]?\d*\.\d+|\d+", msg)
			split_msg = msg.split(' , ')

			print(split_msg)
			print(len(split_msg))
			print("message topic=",message.topic)
			print("message qos=",message.qos)
			print("message retain flag=",message.retain)

			
			filename = "./" + message.topic + ".csv"

			print("file is " + filename)
			row = []
			row.append(time.time())
			n = len(split_msg)
			for i in range(0, n):
					row.append(float(split_msg[i]))

			f = open(filename, 'a')
			writer = csv.writer(f)
			writer.writerow(row)
			print("wrote row ")
			f.close()









