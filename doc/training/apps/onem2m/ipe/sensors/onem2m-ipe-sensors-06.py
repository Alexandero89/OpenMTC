# notes:

# - added create sensor container to function create_sensor_structure()
# - add sensor to _recognized_sensors
# - build data set with value and metadata
# - printing out the new data set


from random import random

from openmtc_app.onem2m import XAE
from openmtc_onem2m.model import Container


class TestIPE(XAE):
    remove_registration = True

    # sensors to create
    sensors = [
        'Temp-1',
        'Temp-2',
        'Humi-1',
        'Humi-2'
    ]

    # settings for random sensor data generation
    threshold = 0.2
    temp_range = 25
    temp_offset = 10
    humi_range = 50
    humi_offset = 30

    def _on_register(self):

        # init variables
        self._recognized_sensors = {}

        # init base structure
        label = 'devices'
        container = Container(resourceName=label)
        self._devices_container = self.create_container(None,
                                                        container,
                                                        labels=[label],
                                                        max_nr_of_instances=0)

        # trigger periodically new data generation
        self.run_forever(1, self.get_random_data)

        # log message
        self.logger.debug('registered')

    def get_random_data(self):

        # at random time intervals
        if random() > self.threshold:

            # select a random sensor
            sensor = self.sensors[int(random() * len(self.sensors))]

            # set parameters depending on sensor type
            if sensor.startswith('Temp'):
                value_range = self.temp_range
                value_offset = self.temp_offset
            else:
                value_range = self.humi_range
                value_offset = self.humi_offset

            # generate random sensor data
            value = int(random() * value_range + value_offset)
            self.handle_sensor_data(sensor, value)

    def handle_sensor_data(self, sensor, value):

        # initialize sensor structure if never done before
        if sensor not in self._recognized_sensors:
            self.create_sensor_structure(sensor)
        self.push_sensor_data(sensor, value)

    def create_sensor_structure(self, sensor):
        print('initializing sensor: %s' % sensor)

        # create sensor container
        device_container = Container(resourceName=sensor)
        device_container = self.create_container(self._devices_container.path,
                                                 device_container,
                                                 labels=['sensor'],
                                                 max_nr_of_instances=0)

        # add sensor to _recognized_sensors
        self._recognized_sensors[sensor] = device_container

    def push_sensor_data(self, sensor, value):

        # build data set with value and metadata
        if sensor.startswith('Temp'):
            data = {
                'value': value,
                'type': 'temperature',
                'unit': 'degreeC'
            }
        else:
            data = {
                'value': value,
                'type': 'humidity',
                'unit': 'percentage'
            }

        # print the new data set
        print('%s: %s' % (sensor, data))


if __name__ == '__main__':
    from openmtc_app.runner import AppRunner as Runner

    host = 'http://localhost:8000'
    app = TestIPE()
    Runner(app).run(host)
