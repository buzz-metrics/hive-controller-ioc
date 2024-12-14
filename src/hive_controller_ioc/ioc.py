from datetime import datetime
from pathlib import Path

import cothread
from pvi._format.dls import DLSFormatter
from pvi._format.template import format_template
from pvi.device import Device, SignalR, SignalRW
from softioc import builder, softioc

from ._pv_poller import PV_Poller


def start_ioc(host: str, prefix: str, bobfile_dir: str):
    builder.SetDeviceName(prefix)

    pv_temp = builder.aIn("HCU:TEMPERATURE", initial_value=-99)
    pv_humidity = builder.aIn("HCU:HUMIDITY", initial_value=-99)
    pv_poll_rate = builder.aOut(
        "HCU:POLL_RATE",
        initial_value=10,
        on_update=lambda value: pv_poll_rate_rbv.set(value),
    )
    pv_poll_rate_rbv = builder.aIn(
        "HCU:POLL_RATE_RBV", initial_value=pv_poll_rate.get()
    )
    pv_update_time = builder.stringIn(
        "HCU:UPDATE_TIME", initial_value=datetime.now().strftime("%H:%M:%S. %d/%m/%Y")
    )
    # ao = builder.aOut("AO", on_update=lambda v: ai.set(v))  # noqa: F841

    make_screen(prefix, bobfile_dir)

    builder.LoadDatabase()
    softioc.iocInit()

    myPoller = PV_Poller(
        host,
        pv_poll_rate,
        pv_update_time,
        [pv_humidity, pv_temp],
    )
    cothread.Spawn(myPoller.poll)

    softioc.interactive_ioc(globals())


def make_screen(prefix: str, filename: str):
    signals = [
        SignalR(name="Temperature", read_pv=prefix + ":HCU:TEMPERATURE"),
        SignalR(name="Humidity", read_pv=prefix + ":HCU:HUMIDITY"),
        SignalRW(
            name="UpdateFrequency",
            read_pv=prefix + ":HCU:POLL_RATE_RBV",
            write_pv=prefix + ":HCU:POLL_RATE",
        ),
        SignalR(name="LastUpdate", read_pv=prefix + ":HCU:UPDATE_TIME"),
        # SignalX(name="Command", write_pv="Go", value="1"),
    ]
    device = Device(label="Hive Control Unit", children=signals)

    format_template(device, prefix, Path(filename))
    DLSFormatter().format(device, Path(filename))
