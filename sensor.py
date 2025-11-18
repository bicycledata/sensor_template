import time
from multiprocessing.connection import Connection
from random import randint

from bicycleinit.BicycleSensor import BicycleSensor


def main(bicycleinit : Connection, name : str, args : dict):
  sensor = BicycleSensor(bicycleinit, name, args)
  sensor.write_header(['random'])
  for _ in range(6):
    sensor.write_measurement([randint(1, 6)])
    time.sleep(10)
  sensor.shutdown()

if __name__ == "__main__":
  main(None, "sensor_template", {})
