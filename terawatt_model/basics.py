#!/usr/bin/env python3

from .globals import *

class Power:
    def __init__(self):
        self.chemical = 0
        self.thermal = 0
        self.electrical = 0
        self.solar = 0

class Energy:
    def __init__(self):
        self.chemical = 0
        self.thermal = 0
        self.electrical = 0
        self.solar = 0

class State:
    def __init__(self):
        self.provide = False
        self.consume = False

class Device:
    def __init__(self):
        self.state = State()
        self.energy_now = Energy()
        self.energy_provided = Energy()
        self.energy_consumed = Energy()
        self.energy_max = Energy()
        self.power = Power()  # For diagnosis
        self.power_in_max = Power()
        self.power_out_min = Power()
        self.power_out_max = Power()

    def update(self, power, state=None):
        if state == 'provide':
            self.state.provide = True
            self.state.consume = False
        elif state == 'consume':
            self.state.provide = False
            self.state.consume = True
        elif state == 'both':
            self.state.provide = True
            self.state.consume = True
        elif state == 'off':
            self.state.provide = False
            self.state.consume = False

        self._log_current_power  # Store input power for diagnosis
        return power
    
    def _to_energy(self, power_type):
        return power_type*(timestep/3600)
    
    def _to_power(self, energy_type):
        return energy_type*(3600/timestep)
    
    def _log_current_power(self, power):
        """
        copy.deepcopy whould also work, but the direct implementation is faster
        """
        self.power.electrical = power.electrical
        self.power.thermal = power.thermal
        self.power.chemical = power.chemical
        self.power.solar = power.solar

class Need:
    ''' This class represents the need for power at a given timepoint in the future. '''

    def __init__(self, time, power):
        # Future timepoint in seconds since 01.01.1970
        self.timepoint=time
        # Power needed in W
        self.power=power

class Consumer:
    ''' This class represents an entity which consumes energy at a certain point in 
    the future. This means that random or very short term power consumption will not
    be handled here.'''

    def __init__(self, broker):
        self.need=[]

    def update():
        __updateNeed()
        __tellBroker()

    def __updateNeed(self):
        pass

    def __tellBroker(self):
        broker.update(self.need)

class Producer:
    ''' This class represents an entity which is able to produce energy at a certain
    point in the future. '''

    def __init__(self):
        self.registeredNeeds=[]

    def providePower(self, need):
        remaining_need,available_need=__provideEnergy(need)
        __registerNeed(available_need)
        return remaining_need

    def update(self):
        pass

    def __provideEnergy(self, need):
        pass

    def _registerNeed(self, available_need):
        pass

class Broker:
    ''' The broker receives all energy needs and sends requests to producers. In general,
    this could be parallelized?'''
    def __init__(self):
        pass
