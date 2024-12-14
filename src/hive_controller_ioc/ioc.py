import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

import cothread
from pvi._format.dls import DLSFormatter
from pvi._format.template import format_template
from pvi.device import Device, SignalR, SignalRW, SignalX
from softioc import builder, softioc

from ._pv_poller import PV_Poller


def start_ioc(host: str, prefix: str, bobfile_dir: str, log_level: str | None = None):
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
    pv_connection_status = builder.stringIn(
        "HCU:CONNECTION_STATUS",
        initial_value="Disconnected",
    )
    pv_restart_ioc = builder.aOut(  # noqa: F841
        "HCU:RESTART_IOC", initial_value=0, on_update=lambda val: restart_ioc(val)
    )
    # ao = builder.aOut("AO", on_update=lambda v: ai.set(v))  # noqa: F841

    make_screen(prefix, bobfile_dir)

    # This is super janky but works. PVI doesnt seem to have an option to
    # achieve this
    add_precision_tag_to_pvs(bobfile_dir, [pv_temp.name, pv_humidity.name])
    builder.LoadDatabase()
    softioc.iocInit()

    myPoller = PV_Poller(
        host,
        pv_poll_rate,
        pv_update_time,
        pv_connection_status,
        [pv_humidity, pv_temp],
    )

    cothread.Spawn(myPoller.poll)
    softioc.interactive_ioc(globals())


def restart_ioc(val):
    if val == 1:
        softioc.safeEpicsExit()


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
        SignalR(
            name="HardwareConnectionStatus", read_pv=prefix + ":HCU:CONNECTION_STATUS"
        ),
        SignalX(
            name="RestartIOC",
            write_pv=prefix + ":HCU:RESTART_IOC",
        ),
        # SignalX(name="Command", write_pv="Go", value="1"),
    ]
    device = Device(label="Hive Control Unit", children=signals)

    format_template(device, prefix, Path(filename))
    DLSFormatter().format(device, Path(filename))


def add_precision_tag_to_pvs(filename: str, pv_names: list):
    # Open the XML file and parse it
    try:
        with open(filename) as file:
            xml_string = file.read()
    except FileNotFoundError:
        print(f"Error: The file {filename} does not exist.")
        return
    except Exception as e:
        print(f"Error: {e}")
        return

    root = ET.fromstring(xml_string)
    for widget in root.findall(".//widget"):
        # Check if the widget has a "pv_name" tag
        pv_name_element = widget.find("pv_name")
        pv_name = None

        if pv_name_element is not None:
            pv_name = pv_name_element.text

        # Proceed only if the "pv_name" value is found and matches one of the pv_names
        if pv_name and pv_name in pv_names:
            # Create a <precision> tag with value '3'
            precision_tag = ET.Element("precision")
            precision_tag.text = "2"

            # Append the precision tag to the widget
            widget.append(precision_tag)

    # Write the modified XML back to the file
    try:
        with open(filename, "w") as file:
            file.write(ET.tostring(root, encoding="unicode"))
        print(f"Precision tags added successfully to {filename}")
    except Exception as e:
        print(f"Error writing to file {filename}: {e}")
