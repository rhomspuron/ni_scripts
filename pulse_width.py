from nidaqmx import Task
from nidaqmx.system import System
from nidaqmx.constants import AcquisitionType, TimeUnits
from nidaqmx.stream_readers import CounterReader
import time
import click
import numpy as np
Reader = None
data = None
ready = 0

@click.command()
@click.argument('high_time', type=click.FLOAT)
@click.argument('low_time', type=click.FLOAT)
@click.argument('samples', type=click.INT)
def count(high_time, low_time, samples):
    global Reader, data

    print('Configure internal connections..')
    system = System.local()
    system.connect_terms('/Dev1/PFI32', '/Dev1/RTSI0')
    with Task('ct1_task') as ct1_task, Task('timer') as timer_task:
        data = np.zeros(samples)
        # configure counter channel and task
        ct1 = ct1_task.ci_channels.add_ci_pulse_width_chan(
            'Dev1/ctr2', 'counter', min_val=2, max_val=100000000,
            units=TimeUnits.TICKS)
        ct1_task.timing.cfg_implicit_timing(samps_per_chan=samples)
        ct1.ci_ctr_timebase_src = '/Dev1/PFI31'
        ct1.ci_pulse_width_term = '/Dev1/RTSI0'
        Reader = CounterReader(ct1_task.in_stream)

        ct1_task.register_every_n_samples_acquired_into_buffer_event(
        1, sample_readies)

        ct1_task.start()

        timer_task.co_channels.add_co_pulse_chan_time(
            'Dev1/ctr1', high_time=high_time, low_time=low_time)
        timer_task.timing.cfg_implicit_timing(
            sample_mode=AcquisitionType.FINITE, samps_per_chan=samples)
        timer_task.start()

        while not timer_task.is_task_done():
             time.sleep(0.001)
        print(data)
        print(len(data))

s = '/'
def sample_readies(task_handle, every_n_samples_event_type,
                  number_of_samples, callback_data):
    global data, ready
    print(time.time())
    sub_data = data[ready: ready+number_of_samples]
    read = Reader.read_many_sample_double(sub_data, number_of_samples, 1)
    ready += read
    return 0


if __name__ == '__main__':
    count()
