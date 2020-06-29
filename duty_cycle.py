import nidaqmx
import click


@click.command()
@click.argument('channel', type=click.STRING)
def duty_cycle(channel):
    print('Acquiring...')
    with nidaqmx.Task() as task:
        task.ci_channels.add_ci_period_chan(channel)
        period = task.read()
    with nidaqmx.Task() as task:
        task.ci_channels.add_ci_pulse_width_chan(channel)
        width = task.read()
    print('duty cycle:',width/period*100)


if __name__ == '__main__':
     duty_cycle()
