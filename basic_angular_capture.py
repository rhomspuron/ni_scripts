import nidaqmx
from nidaqmx.stream_readers import CounterReader
from nidaqmx.constants import EncoderType, EncoderZIndexPhase, AngleUnits, \
    AcquisitionType
import numpy as np
import click


@click.command()
@click.option('--samples', type=click.INT, default=100)
def angularposition(samples):
    counter = 'Dev1/ctr4'
    source_trigger = '/Dev1/RTSI0'
    encoder_decoding = EncoderType.X_4
    encoder_zidxphase = EncoderZIndexPhase.AHIGH_BHIGH
    angle_units = AngleUnits.TICKS

    with nidaqmx.Task() as task:
        # DAQmxCreateCIAngEncoderChan(taskHandle,"Dev1/ctr0","",DAQmx_Val_X4,0,0.0,DAQmx_Val_AHighBHigh,DAQmx_Val_Degrees,24,0.0,"")
        task.ci_channels.add_ci_ang_encoder_chan(counter,
                                                 "",
                                                 encoder_decoding,
                                                 False, 0,
                                                 encoder_zidxphase,
                                                 angle_units,
                                                 24, 0.0, "")
        # DAQmxCfgSampClkTiming(taskHandle,"/Dev1/PFI9",1000.0,DAQmx_Val_Rising,DAQmx_Val_ContSamps,1000)
        task.timing.cfg_samp_clk_timing(1000, source_trigger,
                                        sample_mode=AcquisitionType.FINITE,
                                        samps_per_chan=samples)

        reader = CounterReader(task.in_stream)

        task.start()
        print("Continuously reading. Press Ctrl+C to interrupt\n")

        data = np.zeros(samples)
        i = 0
        while True:

            # DAQmxReadCounterF64(taskHandle,1000,10.0,data,1000,&read,0)
            data[i] = reader.read_one_sample_double(timeout=-1)
            i += 1
            if i == samples-1:
                break

    print('Finish')
    print(data)


if __name__ == '__main__':
    angularposition()

