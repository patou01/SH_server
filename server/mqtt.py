"""
Basically listens to all subtopics from topic which is passed as script parameter. (ie topic/#)

Topics are expected something like
bedroom/temperature
bedroom/humidity
bedroom/co2

The data is then stored in a folder called data. Inside this folder we create a "bedroom" folder under which
each set of data is stored as .csv.

In the future, this will be improved to use something like a database.

"""
import os
from pathlib import Path

import paho.mqtt.client as mqtt
import time
import csv
import random
import logging
import argparse


logging.basicConfig(level=logging.INFO)
counter = 0
DATA_FOLDER = Path("./data")


def temp_callback(client, userdata, message):
    global counter
    counter = counter + 1
    msg = str(message.payload.decode("utf-8"))
    time_received = time.time()
    time_str = time.asctime(time.localtime(time_received))
    split_topic = message.topic.split("/")

    logging.debug(f"message info: topic {message.topic}, qos: {message.qos}, retain: {message.retain}")
    logging.info(f" {counter}, Received message '{msg}' at {time_str} for {split_topic[-1]}")

    room_path = DATA_FOLDER / split_topic[0]
    if not room_path.exists():
        os.makedirs(room_path)

    filename = room_path / f"{split_topic[-1]}.csv"
    mode = 'a'
    if not os.path.exists(filename):
        mode = 'w'

    with open(filename, mode) as f:
        writer = csv.writer(f)
        writer.writerow([time_received, float(msg)])


def on_connect(client, userdata, flags, rc):
    if rc==0:
        print("connected OK Returned code=",rc)
    else:
        print("Bad connection Returned code=",rc)


def main(topic):
    random.seed()
    client_name = "poney"
    name_int = random.getrandbits(16)
    name_int_str = str(name_int)
    client_name += name_int_str
    broker_address = "192.168.0.171"
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_name)

    if not DATA_FOLDER.exists():
        os.makedirs(DATA_FOLDER)

    client.on_message = temp_callback
    client.on_connect = on_connect
    client.connect(broker_address)

    client.subscribe(f"{topic}/#")

    logging.info("broker address " + broker_address + " , name: " + client_name)
    client.loop_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic")
    args = parser.parse_args()
    main(args.topic)
