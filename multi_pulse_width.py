from nidaqmx import Task
from nidaqmx.system import System
from nidaqmx.constants import AcquisitionType, TimeUnits, Edge, \
    DataTransferActiveTransferMode, SampleTimingType, READ_ALL_AVAILABLE
from nidaqmx.stream_readers import CounterReader
import time
import click
import numpy as np
import yaml
import threading


class PulseCounter:
    """
    Class to implement a pulse counter
    """
    def __init__(self, channel, channel_name, gate_src, timebase_src,
                 edge=Edge.RISING):
        self._data = None
        self.sample_readies = 0

        self._channel = channel
        self._task = Task('task' + channel_name)
        self._counter = self._task.ci_channels.add_ci_pulse_width_chan(
            channel, channel_name, units=TimeUnits.TICKS, starting_edge=edge)
        self._counter.ci_ctr_timebase_src = timebase_src
        self._counter.ci_pulse_width_term = gate_src
        self._task.in_stream.read_all_avail_samp = True
        self._reader = CounterReader(self._task.in_stream)
        self._thread = None
        self.stop = False

    def __del__(self):
        self._task.close()

    def start(self, samples):
        self._data = np.zeros(samples)
        self._task.stop()
        self._data = np.zeros(samples)
        self._task.timing.samp_quant_samp_per_chan = samples
        self._task.timing.samp_timing_type = SampleTimingType.IMPLICIT
        self._counter.ci_data_xfer_mech = \
            DataTransferActiveTransferMode.INTERRUPT
        self._thread = threading.Thread(target=self._read, args=[samples])
        self._task.start()
        self.stop = False
        self._thread.start()


    @property
    def done(self):
        return self._task.is_task_done()

    def stop(self):
        self._task.stop()

    def _read(self, samples):
        i = 0
        while not self.stop and samples != 0:
            self._data[i] = self._reader.read_one_sample_double(timeout=-1)
            i += 1
            samples -= 1

    @property
    def data(self):
       return self._data

    
class PulseGenerator:
    def __init__(self, channel, start_src=None):
        self._task = None
        self._channel = channel

        # TODO implement external start

    def __del__(self):
        if self._task is not None:
            self._task.close()

    def start(self,  samples, high_time, low_time, initial_delay=0):
        if self._task is not None:
            self._task.close()
        self._task = Task('timer')
        self._timer = self._task.co_channels.add_co_pulse_chan_time(
            self._channel, high_time=high_time, low_time=low_time,
            initial_delay=initial_delay)
        self._task.timing.samp_quant_samp_per_chan = samples
        self._task.timing.samp_timing_type = SampleTimingType.IMPLICIT
        self._task.start()

    def stop(self):
        self._task.stop()

    @property
    def done(self):
        return self._task.is_task_done()


class PulseWidthApplication:
    """
    Application to implement a
    """
    def __init__(self, yaml_file):
        with open(yaml_file) as f:
            self.config = yaml.full_load(f)

        # Do connections
        self.system = System.local()
        self.system.devices
        term_from = self.config['connections']['from']
        terms_to = self.config['connections']['to']
        for term_to in terms_to:
            self.system.connect_terms(term_from, term_to)
            print('Connect', term_from, 'to', term_to)

        self._timer = PulseGenerator(self.config['timer']['channel'])
        self._counters = {}
        for name, config in self.config['counters'].items():
            self._counters[name] = PulseCounter(
                config['channel'], name, config['gate'], config['source'])

    def __del__(self):
        term_from = self.config['connections']['from']
        terms_to = self.config['connections']['to']
        for term_to in terms_to:
            self.system.disconnect_terms(term_from, term_to)
            print('Disconnect', term_from, 'to', term_to)

    def start(self, high_time, low_time, samples):
        for counter in self._counters.values():
            counter.start(samples)
        time.sleep(0.0001)
        self._timer.start(samples, high_time, low_time)

    @property
    def done(self):
        return self._timer.done

    def get_data(self):
        data = {}
        for name, counter in self._counters.items():
            data[name] = counter.data
        return data


@click.command()
@click.argument('config', type=click.STRING)
@click.argument('runs', type=click.INT)
@click.argument('high_time', type=click.FLOAT)
@click.argument('low_time', type=click.FLOAT)
@click.argument('samples', type=click.INT)
def count(config, runs, high_time, low_time, samples):
    app = PulseWidthApplication(config)
    for i in range(runs):
        print('Run: ', i)
        app.start(high_time, low_time, samples)
        while not app.done:
            time.sleep(0.1)
        data = app.get_data()
        for name, value in data.items():
            print(name, len(value), value)


if __name__ == '__main__':
    count()
