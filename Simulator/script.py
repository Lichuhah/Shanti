import numpy as np
import math
import sys

t_max = 10000

d = 0.05
a = -0.3
b = 0.2
th = 0.45

def h_generator(ttf, d, a, b, th = 0):
    for t in range(ttf, -1, -1):
        h = 1 - d - math.exp(a*t**b)
        if h < th:
            break
        yield t, h

h = h_generator(t_max, d, a, b, th)

import numpy as np
import random
from datetime import date
from scipy.interpolate import interp1d

class VibrationSensorSignalSample:
    CUTOFF = 150

    def __init__(self, W, A, fundamental_from, fundamental_to, t = 0, interval = 1, previous_sample = None, sample_rate = 1024):
        self.interval = interval
        self.sample_rate = sample_rate
        self.W = W
        self.A = A
        self.t = t
        self.base_frequency = fundamental_from
        self.target_base_frequency = fundamental_to
        self.add_noise = True
        self.__previous_sample = previous_sample
        self.__N = sample_rate * interval

    def pcm(self):
        ts = np.linspace(self.t, self.t + self.interval, num = self.__N, endpoint=False)

        x = np.array([0, self.interval]) + self.t
        points = np.array([self.base_frequency, self.target_base_frequency])
        rpm = interp1d(x, points, kind='linear')

        f = rpm(ts)
        f[f < 0] = 0

        fi = np.cumsum(f / self.sample_rate) + (self.__previous_sample.__last_cumsum if self.__previous_sample else 0)

        base = 2 * np.pi * fi
        b = np.array([np.sin(base * w) * a for w, a in zip(self.W, self.A)])
        a = b.sum(axis = 0)

        if self.add_noise:
            a += np.random.normal(0, 0.1, self.__N)

        self.__last_cumsum = fi[-1]
        self.base_frequency = self.target_base_frequency

        a[a > self.CUTOFF] = self.CUTOFF
        a[a < -self.CUTOFF] = -self.CUTOFF

        return np.int16(a / self.CUTOFF * 32767)

class RotationalMachine:
    ambient_temperature = 20 # degrees Celsius
    max_temperature = 120
    ambient_pressure = 101 # kPa

    def __init__(self, name, h1, h2):
        self.W = [1/2, 1, 2, 3, 5, 7, 12, 18]
        self.A = [1, 5, 80, 2/3, 8, 2, 14, 50]
        self.t = 0
        self.name = name
        self.speed = 0
        self.speed_desired = 0
        self.temperature = RotationalMachine.ambient_temperature
        self.pressure = RotationalMachine.ambient_pressure
        self.pressure_factor = 2
        self.__vibration_sample = None
        self.__h1 = h1
        self.__h2 = h2
        self.broken = False
        
    def set_health(self, h1, h2):        
        self.__h1 = h1
        self.__h2 = h2
        self.broken = False

    def set_speed(self, speed):
        self.speed_desired = speed

    def __g(self, v, min_v, max_v, target, rate):
        delta = (target - v) * rate
        return max(min(v + delta, max_v), min_v)
    
    def noise(self, magnitude):
        return random.uniform(-magnitude, magnitude)

    def next_state(self):
        try:
            _, h1 = next(self.__h1)
        except:
            self.broken = True
            raise Exception("F1")
        
        try:
            _, h2 = next(self.__h2)
        except:
            self.broken = True
            raise Exception("F2")
            
        v_from = self.speed / 60        
        self.speed = (self.speed + (2 - h2) * self.speed_desired) / 2
        v_to = self.speed / 60
        
        self.temperature = (2 - h1) * self.__g(self.temperature, self.ambient_temperature, self.max_temperature, self.speed / 10, 0.01 * self.speed / 1000)
        self.pressure = h1 * self.__g(self.pressure, self.ambient_pressure, np.inf, self.speed * self.pressure_factor, 0.3 * self.speed / 1000)        
        self.__vibration_sample = VibrationSensorSignalSample(
            #self.W, self.A, v_from, v_to, t = self.t, previous_sample = self.__vibration_sample)
            self.W, self.A, v_from, v_to, t = self.t)
       
        state = {
            'speed_desired': self.speed_desired,
            'ambient_temperature': self.ambient_temperature + self.noise(0.1),
            'ambient_pressure': self.ambient_pressure + self.noise(0.1),
            'speed': self.speed + self.noise(5),
            'temperature': self.temperature + self.noise(0.1),
            'pressure': self.pressure + self.noise(20),
            'vibration': self.__vibration_sample
        }
        
        self.t += 1

        for key in state:
            value = state[key]
            if isinstance(value, (int, float)):                
                state[key] = round(value, 2)

        return state

# Simulation parameters
import pandas as pd
from dateutil import parser
from datetime import timedelta
import pyarrow 

seed = 42
date_from = parser.parse("May 30 2017 12:00AM")
date_to = parser.parse("Aug 30 2017 12:00AM")
telemetry_batch_frequency = timedelta(hours = 1)
telemetry_interval = timedelta(seconds = 60)
machine_count = 1
active_machines_per_batch = 1
cycle_length_min = 1
cycle_length_max = 5

import os
data_dir = r"D:\Diploma\dataset\0"

random.seed(seed)

def create_machines(n):
    machines = []
    for i in range(n):
        ttf1 = random.randint(5000, 50000)
        ttf2 = random.randint(5000, 90000)

        h1 = h_generator(ttf1, d, a, b)
        h2 = h_generator(ttf2, d, a, b)

        m = RotationalMachine('M_{0:04d}'.format(i), h1, h2)
        machines.append(m)
    return machines

def sample(machines, m):
    return [machines[i] for i in sorted(random.sample(range(len(machines)), m))]

machines = create_machines(machine_count)

telemetry = []
errors = []

max_count = (date_to - date_from) / telemetry_batch_frequency


for i in range(0, 100):
    data_dir = r"D:\Diploma\dataset"
    data_dir += "\\"+str(i)
    date_from = parser.parse("May 30 2017 12:00AM")
    date_to = parser.parse("Jun 3 2017 12:00AM")
    suffix = 0
    print(data_dir)
    sys.stdout.flush()
    while date_from + telemetry_batch_frequency < date_to:
        s = sample(machines, active_machines_per_batch)
        telemetry.clear()
    
        for m in s:
            if m.broken:
                # repair record
                ttf1 = random.randint(5000, 50000)
                h1 = h_generator(ttf1, d, a, b)
    
                ttf2 = random.randint(5000, 90000)
                h2 = h_generator(ttf2, d, a, b)
                m.set_health(h1, h2)
    
                errors.append({
                    'timestamp': date_from,
                    'machineID': m.name,
                    'level': 'INFO',
                    'code': 'fixed'
                })
    
                continue
    
            l = random.randint(cycle_length_min, cycle_length_max)
            offset = random.randint(0, 60-l)
            m.set_speed(1000)
            duration = l * 60
            cooldown_point = duration - 20
            for i in range(duration):
                if i == cooldown_point:
                    m.set_speed(0)
    
                ts = date_from + timedelta(seconds=offset * 60 + i)
                try:
                    state = m.next_state()
                    state['timestamp'] = ts
                    state['machineID'] = m.name
                    telemetry.append(state)
                    if not state['speed']:
                        break
                except Exception as e:
                    errors.append({
                        'timestamp': ts,
                        'machineID': m.name,
                        'level': 'CRITICAL',
                        'code': str(e)
                    })
                    break
    
        if telemetry:
            telemetry_df = pd.DataFrame(telemetry).drop('vibration', axis = 1)
            telemetry_df.index = telemetry_df['timestamp']
            del telemetry_df['timestamp']
            # suffix = date_from.strftime("%Y%m%d-%H%M%S")
            # INT96 timestamp are deprecated, but default INT64 timestamps are supported only since Spark 2.3.0
            if not os.path.exists(data_dir):
                os.mkdir(data_dir)
            telemetry_df.to_csv(data_dir+'\\' + str(suffix) + '.csv', sep='\t', encoding='utf-8')
            suffix += 1
            del telemetry_df
    
        date_from += telemetry_batch_frequency
    
    if errors:
        logs_df = pd.DataFrame(errors)
        sequence_count = len(logs_df[logs_df.level == 'CRITICAL'])
        logs_df.index = logs_df['timestamp']
        logs_df.to_csv(data_dir+'/errors.csv', sep='\t', encoding='utf-8')
        del logs_df['timestamp']
    else:
        print('WARNING: Simulation produced no run-to-failure sequences.')