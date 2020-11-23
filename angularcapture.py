import nidaqmx
from nidaqmx.stream_readers import CounterReader
from nidaqmx.constants import EncoderType, EncoderZIndexPhase, AngleUnits
import numpy as np
import click


@click.command()
@click.argument('samples', type=click.INT)
@click.argument('encodertype')
@click.argument('encoderzindex')
@click.argument('anlgeunits')
def angularposition(samples=100, encodertype=EncoderType.X_4, encoderzindex=EncoderZIndexPhase.AHIGH_BHIGH, anlgeunits=AngleUnits.DEGREES, counter='Dev1/ctr6', source_trigger='/Dev1/RTSI0'):

    argum=check_arguments(encodertype, encoderzindex, anlgeunits)

    with nidaqmx.Task() as task:
        # DAQmxCreateCIAngEncoderChan(taskHandle,"Dev1/ctr0","",DAQmx_Val_X4,0,0.0,DAQmx_Val_AHighBHigh,DAQmx_Val_Degrees,24,0.0,"")
        # task.ci_channels.add_ci_ang_encoder_chan(counter, "", EncoderType.X_4, False, 0, EncoderZIndexPhase.AHIGH_BHIGH, AngleUnits.DEGREES, 24, 0.0, "")
        task.ci_channels.add_ci_ang_encoder_chan(counter, "", argum[0], False, 0, argum[1], argum[2], 24, 0.0, "")
        # DAQmxCfgSampClkTiming(taskHandle,"/Dev1/PFI9",1000.0,DAQmx_Val_Rising,DAQmx_Val_ContSamps,1000)
        task.timing.cfg_samp_clk_timing(1000.0, source_trigger, samps_per_chan=samples) # (source_trigger, Edge.RISING, AcquisitionType.FINITE, 1000)

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

def check_arguments(encodertype, encoderzindex, anlgeunits):

    argum = []

    if encodertype == "TWO_PULSE_COUNTING":
        argum.append(EncoderType.TWO_PULSE_COUNTING)
    elif encodertype == "X_1":
        argum.append(EncoderType.X_1)
    elif encodertype == "X_2":
        argum.append(EncoderType.X_2)
    elif encodertype == "X_4":
        argum.append(EncoderType.X_4)
    else:
        usage()

    if encoderzindex == "AHIGH_BHIGH":
        argum.append(EncoderZIndexPhase.AHIGH_BHIGH)
    elif encoderzindex == "AHIGH_BLOW":
        argum.append(EncoderZIndexPhase.AHIGH_BLOW)
    elif encoderzindex == "ALOW_BHIGH":
        argum.append(EncoderZIndexPhase.ALOW_BHIGH)
    elif encoderzindex == "ALOW_BLOW":
        argum.append(EncoderZIndexPhase.ALOW_BLOW)
    else:
        usage()

    if anlgeunits == "DEGREES":
        argum.append(AngleUnits.DEGREES)
    elif anlgeunits == "FROM_CUSTOM_SCALE":
        argum.append(AngleUnits.FROM_CUSTOM_SCALE)
    elif anlgeunits == "RADIANS":
        argum.append(AngleUnits.RADIANS)
    elif anlgeunits == "TICKS":
        argum.append(AngleUnits.TICKS)
    else:
        usage()

    return argum

def usage():
    print("Usage:")
    print("python3 AngularPosition-Buff-Cont.py number_samples EncoderType EncoderZIndexPhase AngleUnits")
    print("Example: python3 AngularPosition-Buff-Cont.py 100 X_4 AHIGH_BHIGH DEGREES\n")
    print("Loock the manual from view the values: https://nidaqmx-python.readthedocs.io/en/latest/constants.html")
    return 0


if __name__ == '__main__':
    angularposition()

