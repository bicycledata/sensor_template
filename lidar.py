#!/usr/bin/env python3

import argparse
import smbus
import time

from BicycleSensor import BicycleSensor, configure

class LidarSensor(BicycleSensor):

  def __init__(self, logger):
  
    self.BUS = 1 # on RPi5, it's bus no.1 - can check with `ls /dev/*i2c*`
    self.ADDRESS = 0x62 # get with `sudo i2cdetect -y 1`
    self.DISTANCE_WRITE_REGISTER = 0x00
    self.DISTANCE_WRITE_VALUE = 0x04
    self.DISTANCE_READ_REGISTER_1 = 0x8f
    self.DISTANCE_READ_REGISTER_2 = 0x10
    
    try:
      self.actual_bus = smbus.SMBus(self.BUS)
    except:
      logging.error("Not able ot instantiate bus number", self.BUS)

  def writeAndWait(self):
    self.actual_bus.write_byte_data(self.ADDRESS, self.DISTANCE_WRITE_REGISTER, self.DISTANCE_WRITE_VALUE);
    time.sleep(0.02)

  def readDistAndWait(self):
    reading = self.actual_bus.read_i2c_block_data(self.ADDRESS, self.DISTANCE_READ_REGISTER_1, 2)
    # time.sleep(0.01)
    return (reading[0] << 8 | reading[1])

  def getDistance(self):
    self.riteAndWait()
    dist = self.readDistAndWait()
    return dist # in cm

  def write_header(self):
    '''Override to write the header to the CSV file.'''
    self.write_to_file("date, time, distance")

  def write_measurement(self):
    '''Override to write measurement data to the CSV file.'''
    try:
      distance = self.getDistance() # in cm
      datestamp, timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f").split(" ")
      data_row = f"{datestamp}, {timestamp}, {distance}"
    except:
      logging.error("Was not able to read and process distance from sensor.")

    self.write_to_file(data_row)


if __name__ == '__main__':

  PARSER = argparse.ArgumentParser(
    description='Lidar Sensor',
    allow_abbrev=False,
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
  )

  PARSER.add_argument('--hash', type=str, required=True, help='[required] hash of the device')
  PARSER.add_argument('--name', type=str, default="VTIGarminLidarLiteV3", help='[required] name of the sensor')
  PARSER.add_argument('--loglevel', type=str, default='DEBUG', help='Set the logging level (e.g., DEBUG, INFO, WARNING)')
  PARSER.add_argument('--measurement-frequency', type=float, default=1.0, help='Frequency of sensor measurements in 1/s')
  PARSER.add_argument('--stdout', action='store_true', help='Enables logging to stdout')
  PARSER.add_argument('--upload-interval', type=float, default=300.0, help='Interval between uploads in seconds')
  ARGS = PARSER.parse_args()

  # Configure logging
  configure(stdout=ARGS.stdout, rotating=True, loglevel=ARGS.loglevel)

  lidar_sensor = LidarSensor(ARGS.name, ARGS.hash, ARGS.measurement_frequency, ARGS.upload_interval)
  lidar_sensor.main()
