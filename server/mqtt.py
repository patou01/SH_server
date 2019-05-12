import paho.mqtt.client as mqtt #import the client
import time
import csv
import calendar
import re
import random



	
def temp_callback(client, userdata, message):
        msg = str(message.payload.decode("utf-8"))
        print("Received a msg \n")
        print("message received " , msg)
        print(msg.split(' , '))
        parsed = re.findall(r"[-+]?\d*\.\d+|\d+", msg)
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


def on_connect(client, userdata, flags, rc):
    if rc==0:
        print("connected OK Returned code=",rc)
    else:
        print("Bad connection Returned code=",rc)


random.seed()
client_name = "poney"
name_int = random.getrandbits(16)
name_int_str = str(name_int)
client_name += name_int_str
broker_address = "192.168.0.112"
client = mqtt.Client(client_name) #create new instance

client.on_message = temp_callback
client.on_connect = on_connect


client.connect(broker_address) #connect to broker

client.subscribe("Patrick")



print("broker address " + broker_address + " , name: " + client_name)
client.loop_forever()





