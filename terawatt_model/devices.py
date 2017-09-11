#!/usr/bin/env python3

from .globals import *
from .basics import *
import csv

# battery.py
class Battery(Device):
    """
    Charge time for accumulator = (capacity of accumulator in mAh) / (charging current in mA) * 1.35
    We can use the power directly since the voltage cancels out.
    
    Charging current estimate: Max current ~ Max energy * 0.4
    """
    def __init__(self):
        super().__init__()  # parent init

        self.state.provide = False
        self.state.consume = True

        self.super_cap_current_energy = 0
        self.super_cap_max_energy = 300
        self.battery_current_energy = 0
        self.battery_max_energy = 30000
        self.power_in_max.electrical = self.battery_max_energy * 0.4
        self.power_out_max.electrical = 50000

        self.energy_now.electrical = 0
        self.energy_max.electrical = self.battery_max_energy + self.super_cap_max_energy
    
    def update(self, power, state=None, power_requested=None):
        super().update(power, state)
        
        if self.state.consume:
            power = self._do_consume(power)
        
        if self.state.provide:
            power = self._do_provide(power, power_requested)
        
        self._log_current_power(power)
        return power

    def _do_consume(self, power):
        power_in_max = self.get_power_in_max()
        useable_power = min(power_in_max.electrical, power.electrical)
        additional_energy = self._to_energy(useable_power) / 1.35

        if self.super_cap_current_energy + additional_energy < self.super_cap_max_energy:
            self.super_cap_current_energy += additional_energy
            power.electrical -= useable_power
            self.energy_consumed.electrical += additional_energy
        elif self.battery_current_energy + additional_energy < self.battery_max_energy:
            self.battery_current_energy += additional_energy
            power.electrical -= useable_power
            self.energy_consumed.electrical += additional_energy
        
        self.energy_now.electrical = self.super_cap_current_energy + self.battery_current_energy
        return power

    def _do_provide(self, power, power_requested=None):
        if power_requested == None:
            return power
        
        ere = self._to_energy(power_requested.electrical)
        if self.super_cap_current_energy - ere > 0:
            self.super_cap_current_energy -= ere
            power.electrical += power_requested.electrical
            self.energy_provided.electrical += ere
        elif self.battery_current_energy - ere > 0:
            self.battery_current_energy -= ere
            power.electrical += power_requested.electrical
            self.energy_provided.electrical += ere
        
        self.energy_now.electrical = self.super_cap_current_energy + self.battery_current_energy
        return power

    def get_power_in_max(self):
        """
        The charging is usually reduced above 80% to enhance the livespan of the battery.
        """
        power_max = Power()
        if self.energy_now.electrical < 0.8*self.energy_max.electrical:
            power_max.electrical = self.power_in_max.electrical
            return power_max
        elif 0.8*self.energy_max.electrical <= self.energy_now.electrical <= 1.0*self.energy_max.electrical:
            power_max.electrical = self.power_in_max.electrical * 0.5
            return power_max
        else:
            return power_max
    

# photovoltaic.py
class Photovoltaic(Device):
    """
    Panel size and efficiency are tuned to match 10kW peak for maximum solar power.
    """
    def __init__(self):
        super().__init__()  # parent init
        self.panel_size = 40  # square meters
        self.efficiency = 0.2  # efficiency of solar power to electrical power conversion

        self.state.provide = True
        self.state.consume = False

        self._real_data={}
        self._load_real_data()

    def _load_real_data(self):
        with open('analysis/pv_wirk_analysed.csv') as csvfile:
            dialect = csv.Sniffer().sniff(csvfile.read(1024))
            csvfile.seek(0)
            reader = csv.reader(csvfile, dialect)
            next(reader, None)
            for row in reader:
                self._real_data[datetime.datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S")]=float(row[2])

    def update(self, power, time=None, state=None):
        super().update(power, state)

        if self.state.provide:
            if time!=None and time in self._real_data and self._real_data[time]!=None:
                power = self._do_provide_timed(power, time)
            else:
                power = self._do_provide(power)
        
        self._log_current_power(power)
        return power

    def _do_provide_timed(self, power, time):
        power.electrical = self._real_data[time]

        energy = self._to_energy(power.electrical)
        self.energy_now.electrical = energy
        self.energy_provided.electrical += energy
        return power

    def _do_provide(self, power):
        power.electrical = self.efficiency * self.panel_size * power.solar

        energy = self._to_energy(power.electrical)
        self.energy_now.electrical = energy
        self.energy_provided.electrical += energy
        return power


# sun.py

#import numpy as np  # Don't use since we want to use pypy
import pysolar
import datetime

class Sun(Device):
    """
    Maximum power is an estimate.
    """
    def __init__(self, latitude_deg=53.551086, longitude_deg=9.993682):
        super().__init__()  # parent init
        self.maximum_power = 1000  # Watt per square meter
        
        self.state.provide = True
        self.state.consume = False
        
        self.latitude_deg = latitude_deg  # positive in the northern hemisphere
        self.longitude_deg = longitude_deg  # negative reckoning west from prime meridian in Greenwich, England

#    def gaussian(self, x, mu, sig):
#        return np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.)))

    def sun_model(self, d=datetime.datetime.now()):
        altitude_deg = pysolar.solar.get_altitude(self.latitude_deg, self.longitude_deg, d)
        azimuth_deg = pysolar.solar.get_azimuth(self.latitude_deg, self.longitude_deg, d)

        if altitude_deg > 0:
            return pysolar.radiation.get_radiation_direct(d, altitude_deg)
        else:
            return 0
    
    def update(self, time=datetime.datetime.now(), state=None):

        if self.state.provide:
            power = self._do_provide(time)
        
        self._log_current_power(power)
        return power
    
    def _do_provide(self, time):
        # Model according to summer days in Germany
        power = Power()
        #power.solar = np.floor(1000 * self.gaussian(hour_of_day, 12, 2))  # output in Watt per square meter
        power.solar = self.sun_model(time)
        
        energy = self._to_energy(power.solar)
        self.energy_now.solar = energy
        self.energy_provided.solar += energy
        return power


# provider.py
class Provider(Device):
    """
    Provider is a source and sink.
    As sink it just takes all surplus power and we can monitor the money created.
    """

    def __init__(self):
        super().__init__()  # parent init
        self.power_electrical_max = 3 * 230 * 64  # (three phases) * Volt * Ampere

        self.state.provide = True
        self.state.consume = True

    def update(self, power, state=None):
        super().update(power, state)

        if self.state.consume:
            power = self._do_consume(power)

        if self.state.provide:
            power = self._do_provide(power)

        self._log_current_power(power)
        return power

    def _do_consume(self, power, consume_thermal=False, consume_chemical=False):
        self.energy_consumed.electrical += self._to_energy(power.electrical)
        power.electrical = 0
        if consume_thermal:
            self.energy_consumed.thermal += self._to_energy(power.thermal)
            power.thermal = 0
        if consume_chemical:
            self.energy_consumed.chemical += self._to_energy(power.chemical)
            power.chemical = 0
        
        return power

    def _do_provide(self, power):
        if power.electrical < self.power_electrical_max:
            power_diff = self.power_electrical_max - power.electrical
            self.energy_provided.electrical += self._to_energy(power_diff)
        power.electrical = self.power_electrical_max
        
        self.energy_now.electrical = self._to_energy(self.power_electrical_max)
        return power


# car.py
class Car(Device):
    """
    An electric car as consumer for the power produced.
    """

    def __init__(self, power_in_max_electrical=7400, energy_max_electrical=22000, fuel_usage_100_km=17000):
        super().__init__()  # parent init
        self.energy_now.electrical = 0
        self.energy_max.electrical = energy_max_electrical
        self.power_in_max.electrical = power_in_max_electrical
        self.fuel_usage_100_km = fuel_usage_100_km

        self.state.provide = False
        self.state.consume = True

    def update(self, power, state=None):
        super().update(power, state)

        if self.state.consume:
            power = self._do_consume(power)
        
        return power
    
    def _do_consume(self, power):
        power_in_max = self.get_power_in_max()
        useable_power = min(power_in_max.electrical, power.electrical)
        additional_energy = self._to_energy(useable_power) / 1.35
        if self.energy_now.electrical + additional_energy < self.energy_max.electrical:
            self.energy_now.electrical += additional_energy
            power.electrical -= useable_power
        
        return power

    def get_power_in_max(self):
        """
        The charging is usually reduced above 80% to enhance the livespan of the battery.
        """
        power_max = Power()
        if self.energy_now.electrical < 0.8*self.energy_max.electrical:
            power_max.electrical = self.power_in_max.electrical
            return power_max
        elif 0.8*self.energy_max.electrical <= self.energy_now.electrical <= 1.0*self.energy_max.electrical:
            power_max.electrical = self.power_in_max.electrical * 0.5
            return power_max
        else:
            return power_max

    def drive(self, distance):
        """
        Drive the specified amount of kilometers and discharge the battery accordingly 
        return True if possible
        otherwise leave battery uncharged and return False.
        """
        energy_required_electrical = self.fuel_usage_100_km / 100 * distance
        if self.energy_now.electrical >= energy_required_electrical:
            self.energy_now.electrical -= energy_required_electrical
            return True
        else:
            return False


# electrolysis.py
class Electrolysis(Device):
    """
    System that converts electrical energy to chemical energy.
    http://www.itm-power.com/product/hpac
    """

    def __init__(self):
        super().__init__()  # parent init
        self.energy_now.electrical = 0

        self.decompositional_voltage = 1.229
        self.efficiency = 0.9  # 90% efficiency, as told by "energy campus team"
        self.power_in_max.electrical = 10000
        
        self.state.provide = True
        self.state.consume = False
        
        self._calc_energy_production()

    def _calc_energy_production(self):
        """
        Calculate the energy produced at a timestep when the device is running at normal power.
        
        The device produces hydrogen at 15 bar -> transform pressure to normal pressure using Boyle-Mariotte.
        Boyle-Mariotte
          p1/p2 = V2/V1
          => V_atmo = p_prod / p_atmo * V_prod
          
        hydrogen (atmospheric pressure): 3 Wh/l
        """
        production_minute = 40  # liter
        production_timestep = production_minute / 60 * timestep  # liter
        pressure_prod = 15  # bar
        pressure_atmo = 1  # bar
        
        self._energy_production = ( pressure_prod / pressure_atmo ) * production_timestep * hydrogen_energy_density_atmo

    def update(self, power, state=None, power_requested=None):
        super().update(power, state)

        if self.state.consume:
            power = self._do_consume(power)

        if self.state.provide:
            power = self._do_provide(power, power_requested)

        return power

    def _do_consume(self, power):
        current_electrical = power.electrical / self.decompositional_voltage

        # According to Farady the weight of the electrolytical created substance
        # is proportional to the charge that flows
        # I could not find a minimum working power except the required decompositional voltage.
        # So I assume that 1A should be enough to run the electrolysis.
        
        if current_electrical >= 1:
            useable_power = min(self.power_in_max.electrical, power.electrical)
            additional_energy = self._to_energy(useable_power) * self.efficiency
            power.electrical -= useable_power
            self.energy_now.chemical += additional_energy
            self.energy_provided.chemical += additional_energy
            self.energy_consumed.electrical += self._to_energy(useable_power)
        return power

    def _do_provide(self, power, power_requested=None):
        if power_requested == None:
            return power
        
        er = self._to_energy(power_requested.chemical)
        if self.energy_now.chemical >= er:
            self.energy_now.chemical -= er
            self.energy_consumed.chemical += er
            power.chemical = power_requested.chemical
        return power


# methanisation.py
class Methanization(Device):
    """
    Model for MT BioMethan GmbH device.
    efficiency: methane of gas min. 80 Vol.-%
    """

    def __init__(self):
        super().__init__()  # parent init
        self.energy_now.electrical = 0
        self.efficiency = 0.8
        self.energy_methanization = self._to_energy((800/self.efficiency)*hydrogen_energy_density_atmo)

        self.state.provide = True
        self.state.consume = True

    def update(self, power, state=None, power_requested=None):
        super().update(power, state)

        if self.state.consume:
            power = self._do_consume(power)

        if self.state.provide:
            power = self._do_provide(power, power_requested)

        return power

    def _do_consume(self, power):
        power_required = self._to_power(self.energy_methanization)
        if power.chemical >= power_required:
            power.chemical -= power_required
            self.energy_now.chemical += self.energy_methanization * self.efficiency  # only 80% efficiency
            self.energy_consumed.chemical += self.energy_methanization
        return power

    def _do_provide(self, power, power_requested=None):
        if power_requested == None:
            return power
        
        erc = self._to_energy(power_requested.chemical)
        
        if self.energy_now.chemical >= erc:
            power.chemical = power_requested.chemical
            self.energy_now.chemical -= erc
            self.energy_provided.chemical += erc
        
        return power

    def get_power_in_max(self):
        """
        The charging is usually reduced above 80% to enhance the livespan of the battery.
        """
        power_max = Power()
        power_max.chemical = self._to_power(self.energy_methanization)
        return power_max
    
    def get_power_out_max(self):
        power_max = Power()
        power_max.chemical = self._to_power(self.energy_methanization * self.efficiency)
        return power_max

# cogeneration.py
class Cogeneration(Device):
    """
    Model for cogeneration plant.
    For now the thermal part is neglected.
    """

    def __init__(self):
        super().__init__()  # parent init
        
        self.chemical_to_electrical_efficiency = 0.315
        self.power_out_min.electrical = 5000
        self.power_out_max.electrical = 16000
        self.energy_min_chemical_startup = 5000
        self.energy_min_chemical_sustain = 100
        self.is_running = False
        
        self.state.provide = True
        self.state.consume = True
        
    def update(self, power, state=None, power_requested=None):
        super().update(power, state)

        if self.state.consume:
            power = self._do_consume(power)
        
        if self.state.provide:
            power = self._do_provide(power, power_requested)

        self._log_current_power(power)
        return power

    def _do_consume(self, power):
        self.energy_now.chemical += self._to_energy(power.chemical)
        self.energy_consumed.chemical += self._to_energy(power.chemical)
        power.chemical = 0
        return power

    def _do_provide(self, power, power_requested=None):
        if power_requested == None:
            return power

        # Storage too empty to start cogeneration
        if self.energy_now.chemical < self.energy_min_chemical_startup and not self.is_running:
            return power
        
        # Storage too empty to continue cogeneration
        if self.energy_now.chemical < self.energy_min_chemical_sustain and self.is_running:
            self.is_running = False
            return power
        
        if self.power_out_min.electrical < power_requested.electrical < self.power_out_max.electrical:
            self.is_running = True
            prc = self.power_conversion_electrical_to_chemical(power_requested.electrical)

            power.electrical += power_requested.electrical
            self.energy_now.chemical -= self._to_energy(prc.chemical)
            self.energy_provided.electrical -= self._to_energy(power_requested.electrical)
        elif power_requested.electrical > self.power_out_max.electrical:
            self.is_running = True
            prc = self.power_conversion_electrical_to_chemical(self.power_out_max.electrical)

            power.electrical += self.power_out_max.electrical
            self.energy_now.chemical -= self._to_energy(prc.chemical)
            self.energy_provided.electrical -= self._to_energy(self.power_out_max.electrical)

        return power

    def power_conversion_electrical_to_chemical(self, power_electrical):
        power = Power()
        if power_electrical < self.power_out_min.electrical:
            pass  # Cogeneration doesn't work here
        elif self.power_out_min.electrical < power_electrical < self.power_out_max.electrical:
            power.chemical = power_electrical / self.chemical_to_electrical_efficiency
        else:
            power.chemical = self.power_out_max.electrical / self.chemical_to_electrical_efficiency
        return power
        
        
        
