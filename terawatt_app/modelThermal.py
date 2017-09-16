#!/usr/bin/env python

import sys
import os

import datetime

sys.path.insert(0, os.path.join('..'))
import terawatt_model

class ModelThermal:

    def __init__(self, radiator_power_out_requested = 750, room_power_out = 250):
        self.radiator_power_out_requested = radiator_power_out_requested
        self.room_power_out = room_power_out

        self._initialize()
        self.increment()

    def _initialize(self):
        self.radiator = terawatt_model.Radiator()
        self.room = terawatt_model.Room(power_out_thermal=self.room_power_out)
        self.provider = terawatt_model.Provider()
        self.threshold_counter = 0
        self.notification_sent = False

        self.energy_now_thermal_init = self.room.energy_now.thermal

        self.time_current = datetime.datetime(2017, 9, 17, 12, 0, 0, 0)

    def check_threshold(self, threshold=75):
            if self.provider.power.thermal > threshold:
                self.threshold_counter += 1

    def increment(self):

        dt = terawatt_model.timestep
        self.time_current = self.time_current + datetime.timedelta(0, dt)  # days, seconds
        time = self.time_current

        power = terawatt_model.Power()
        power_requested = terawatt_model.Power()

        controll_loop = (self.room.energy_max.thermal - self.room.energy_now.thermal) / (self.room.energy_max.thermal - self.energy_now_thermal_init)
        power_requested.thermal += self.radiator_power_out_requested * controll_loop

        power = self.radiator.update(power, state='provide', power_requested=power_requested)
        power = self.room.update(power, state='consume')

        power = self.provider.update(power_requested, state='consume')

        self.check_threshold()



if __name__ == '__main__':
    from plotly.offline import plot
    import plotly.graph_objs as go

    mt = ModelThermal(room_power_out=10)
    y1 = []
    y2 = []
    for i in range(600):
        mt.increment()
        y1.append(mt.room.energy_now.thermal)
        y2.append(mt.provider.power.thermal)

    # Create a trace
    data = []
    data.append(go.Scatter(
        x=range(len(y1)),
        y=y1,
        yaxis='y2',
        name='Window closed',
        legendgroup='Window closed',
    ))
    data.append(go.Scatter(
        x=range(len(y2)),
        y=y2,
        name='Window closed',
        legendgroup = 'Window closed',
    ))

    mt = ModelThermal(room_power_out=100)
    y1 = []
    y2 = []
    for i in range(600):
        mt.increment()
        y1.append(mt.room.energy_now.thermal)
        y2.append(mt.provider.power.thermal)

    # Create a trace
    data.append(go.Scatter(
        x=range(len(y1)),
        y=y1,
        yaxis='y2',
        name='Window open',
        legendgroup='Window open',
    ))
    data.append(go.Scatter(
        x=range(len(y2)),
        y=y2,
        name='Window open',
        legendgroup='Window open',
    ))

    layout = go.Layout(
        xaxis=go.XAxis(title='Time [s]'),
        yaxis=go.YAxis(title='W'),
        yaxis2=go.YAxis(
            title='Wh',
            # titlefont={color:'rgb(148, 103, 189)'},
            # tickfont={color:'rgb(148, 103, 189)'},
            overlaying='y',
            side='right'
        )
    )
    fig = go.Figure(data=data, layout=layout)

    plot(fig, filename='room_all')
