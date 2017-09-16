#!/usr/bin/env python

import sys
import os

import datetime
import random

sys.path.insert(0, os.path.join('..'))
import terawatt_model

class ModelElectrical:

    def __init__(self):
        self._update_agent_n()
        self._initialize()
        self.update_external()
        self.increment()


    def _update_agent_n(self):
        self.agent_n = dict(
            # car1_energy = random.randint(0, terawatt_model.Car.energy_max.electrical),
            work=[9, 17],
            distance=22,

            car1_energy=8000,
            charge_car1_prio=2,

            car2_energy=40,
            charge_car2_prio=1,

            battery_energy=35,

            cogeneration_energy=10,
        )


    def _initialize(self):
        self.sun = terawatt_model.Sun()
        self.photovoltaic = terawatt_model.Photovoltaic()
        self.car1 = terawatt_model.Car()
        self.car2 = terawatt_model.Car(energy_max_electrical=500, fuel_usage_100_km=250) # E-Bike
        self.provider = terawatt_model.Provider()
        self.battery = terawatt_model.Battery()
        self.electrolysis = terawatt_model.Electrolysis()
        self.methanization = terawatt_model.Methanization()
        self.cogeneration = terawatt_model.Cogeneration()

        self.car1_work = False
        self.car2_work = False

        self.time_current = datetime.datetime(2017, 9, 16, 7, 29, 59, 0)


    def update_external(self):
        self.car1.energy_now.electrical = self.agent_n['car1_energy']
        self.car2.energy_now.electrical = self.agent_n['car2_energy']
        self.battery.battery_current_energy = self.agent_n['battery_energy']
        self.cogeneration.energy_now.chemical = self.agent_n['cogeneration_energy']


    def increment(self):

        dt = terawatt_model.timestep
        self.time_current = self.time_current + datetime.timedelta(0, dt)  # days, seconds
        time = self.time_current

        # Drive to work
        success_car1 = False
        success_car2 = False

        # Roll dice to see if bicycle or car will be used
        car1_or_car2 = random.randint(0,1)

        if car1_or_car2 == 0:
            if (time.hour == self.agent_n['work'][0]) and (time.second == 0) and (time.minute == 0 ):
                success_car2 = self.car2.drive(self.agent_n['distance'])
                if success_car2:
                    self.car2_work = True
                if not success_car2:
                    success_car1 = self.car1.drive(self.agent_n['distance'])
                    if success_car1:
                        self.car1_work = True
        else:
            if (time.hour == self.agent_n['work'][0]) and (time.second == 0) and (time.minute == 0 ):
                success_car1 = self.car1.drive(self.agent_n['distance'])
                if success_car1:
                    self.car1_work = True
                if not success_car1:
                    success_car2 = self.car2.drive(self.agent_n['distance'])
                    if success_car2:
                        self.car2_work = True

        if (time.hour == self.agent_n['work'][1]) and (time.second == 0) and (time.minute == 0):
            self.car1_work = False
        if (time.hour == self.agent_n['work'][1]) and (time.second == 0) and (time.minute == 0):
            self.car2_work = False

        power = self.sun.update(time=time)
        power = self.photovoltaic.update(power)

        # Consumers request
        power_requested = terawatt_model.Power()
        if self.agent_n['charge_car1_prio'] <= self.agent_n['charge_car2_prio']:
            # cannot compare against full charge. Due to incremental energies we never reach full charge exactly.

            if not self.car1_work:
                if self.car1.energy_now.electrical < 0.99 * self.car1.energy_max.electrical:
                    power_requested.electrical += self.car1.get_power_in_max().electrical

            if not self.car2_work:
                if self.car2.energy_now.electrical < 0.99 * self.car2.energy_max.electrical:
                    power_requested.electrical += self.car2.get_power_in_max().electrical
        else:
            # cannot compare against full charge. Due to incremental energies we never reach full charge exactly.
            if not self.car2_work:
                if self.car2.energy_now.electrical < 0.99 * self.car2.energy_max.electrical:
                    power_requested.electrical += self.car2.get_power_in_max().electrical

            if not self.car1_work:
                if self.car1.energy_now.electrical < 0.99 * self.car1.energy_max.electrical:
                    power_requested.electrical += self.car1.get_power_in_max().electrical

        power = self.battery.update(power, state='provide', power_requested=power_requested)

        # Consumers consume
        if self.agent_n['charge_car1_prio'] <= self.agent_n['charge_car2_prio']:
            if not self.car1_work:
                power = self.car1.update(power)
            if not self.car2_work:
                power = self.car2.update(power)
        else:
            if not self.car2_work:
                power = self.car2.update(power)
            if not self.car1_work:
                power = self.car1.update(power)

        power = self.battery.update(power, state='consume')

        power = self.provider.update(power)


