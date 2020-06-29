import nidaqmx
from nidaqmx.constants import AcquisitionType
import click
import time


@click.command()
@click.argument('high_time', type=click.FLOAT)
@click.argument('low_time', type=click.FLOAT)
@click.argument('samples', type=click.INT)
def gen_pulses(high_time, low_time, samples, counter='/Dev1/ctr1'):
    with nidaqmx.Task() as task:
        task.co_channels.add_co_pulse_chan_time(counter, high_time=high_time,
                                                low_time=low_time)
        task.timing.cfg_implicit_timing(sample_mode=AcquisitionType.FINITE,
                                        samps_per_chan=samples)
        task.start()
        while not task.is_task_done():
            time.sleep(0.001)


if __name__ == '__main__':
    print('Connect output and auxiliar')
    system = nidaqmx.system.System.local()
    system.connect_terms('/Dev1/PFI32', '/Dev1/PFI33')