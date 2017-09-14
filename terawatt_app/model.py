#!/usr/bin/env python

import sys
import os

import datetime
import random

sys.path.insert(0, os.path.join('..'))
import terawatt_model

class Model:

    def __init__(self):
        self._update_agent_n()
        self._initialize()
        self.update_external()
        self.increment()


    def _update_agent_n(self):
        self.agent_n = dict(
            # car1_energy = random.randint(0, terawatt_model.Car.energy_max.electrical),
            car1_energy=21900,
            charge_car1_start=random.randint(0, 19),
            charge_car1_time=random.randint(0, 5),
            car1_distance_work=random.randint(40, 80),
            car1_distance_additional=0,
            car1_drive_success=False,
            # car2_energy = random.randint(0, terawatt_model.Car.energy_max.electrical),
            car2_energy=40,
            charge_car2_start=random.randint(0, 19),
            charge_car2_time=random.randint(0, 5),
            car2_distance_work=random.randint(40, 80),
            car2_distance_additional=0,
            car2_drive_success=False,
            # battery_energy = random.randint(0, terawatt_model.Battery.energy_max.electrical),
            battery_energy=35,
            # cogeneration_energy = random.randint(0, 1000),
            cogeneration_energy=10,
        )


    def _initialize(self):
        self.sun = terawatt_model.Sun()
        self.photovoltaic = terawatt_model.Photovoltaic()
        self.car1 = terawatt_model.Car()
        self.car2 = terawatt_model.Car(energy_max_electrical=500) # E-Bike
        self.provider = terawatt_model.Provider()
        self.battery = terawatt_model.Battery()
        self.electrolysis = terawatt_model.Electrolysis()
        self.methanization = terawatt_model.Methanization()
        self.cogeneration = terawatt_model.Cogeneration()

        self.time_current = datetime.datetime(2017, 9, 24, 12, 0, 0, 0)


    def update_external(self):
        self.car1.energy_now.electrical = self.agent_n['car1_energy']
        self.car2.energy_now.electrical = self.agent_n['car2_energy']
        self.battery.battery_current_energy = self.agent_n['battery_energy']
        self.cogeneration.energy_now.chemical = self.agent_n['cogeneration_energy']


    def increment(self):

        dt = terawatt_model.timestep
        self.time_current = self.time_current + datetime.timedelta(0, dt)  # days, seconds
        time = self.time_current

        power = self.sun.update(time=time)
        power = self.photovoltaic.update(power)

        power = self.battery.update(power, state='consume')
        power = self.electrolysis.update(power, state='both', power_requested=self.methanization.get_power_in_max())
        power = self.methanization.update(power, state='both', power_requested=self.methanization.get_power_out_max())
        power = self.cogeneration.update(power, state='consume')

        # Consumers request
        power_requested = terawatt_model.Power()
        if self.agent_n['charge_car1_start'] <= time.hour <= self.agent_n['charge_car1_start'] + self.agent_n['charge_car1_time']:
            # cannot compare against full charge. Due to incremental energies we never reach full charge exactly.
            if self.car1.energy_now.electrical < 0.99 * self.car1.energy_max.electrical:
                power_requested.electrical += self.car1.get_power_in_max().electrical

        if self.agent_n['charge_car2_start'] <= time.hour <= self.agent_n['charge_car2_start'] + self.agent_n['charge_car2_time']:
            if self.car2.energy_now.electrical < 0.99 * self.car2.energy_max.electrical:
                power_requested.electrical += self.car2.get_power_in_max().electrical

        power_requested.chemical += self.cogeneration.power_conversion_electrical_to_chemical(
            power_requested.electrical).chemical
        power = self.cogeneration.update(power, state='provide', power_requested=power_requested)
        power_requested.electrical -= power.electrical
        power = self.battery.update(power, state='provide', power_requested=power_requested)

        # Consumers consume
        if self.agent_n['charge_car1_start'] <= time.hour <= self.agent_n['charge_car1_start'] + self.agent_n['charge_car1_time']:
            power = self.car1.update(power)

        if self.agent_n['charge_car2_start'] <= time.hour <= self.agent_n['charge_car2_start'] + self.agent_n['charge_car2_time']:
            power = self.car2.update(power)

        power = self.provider.update(power)


