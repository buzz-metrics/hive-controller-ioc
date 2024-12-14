import logging
from datetime import datetime

import cothread
import requests

logger = logging.getLogger(__name__)


class PV_Poller:
    def __init__(
        self,
        host: str,
        pv_poller,
        pv_update_time,
        pv_connection_status,
        target_pvs: list,
    ):
        self.host = host
        self.poller_pv = pv_poller
        self.pv_update_time = pv_update_time
        self.pv_connection_status = pv_connection_status
        self.target_pvs = target_pvs

        self.target_pv_names = [pv.name.split(":")[-1].lower() for pv in target_pvs]
        print(self.target_pvs)

    def poll(self):
        while True:
            poll_delay = self.poller_pv.get()
            if poll_delay <= 0:
                cothread.Sleep(10)
                continue
            cothread.Sleep(poll_delay)
            self.update_pvs()

    def update_pvs(self):
        url = self.host + "/get_vals?fields="
        url += ",".join(self.target_pv_names)

        try:
            response = requests.get(url)

            if not response.ok:
                logger.critical(
                    f"Failed to get values from {self.host}. Response: {response.text}"
                )
                raise Exception(
                    f"Response code was not ok from {self.host}.\nGot {response.text} "
                )

            values = response.json()
            for i, pv in enumerate(self.target_pvs):
                val = values[self.target_pv_names[i]]
                pv.set(val)

            self.pv_update_time.set(datetime.now().strftime("%H:%M:%S %d/%m/%Y"))
            self.pv_connection_status.set("Connected")

        except Exception as e:
            logger.critical(f"Tried to update from hardware. Error:\n{str(e)}")
            self.pv_connection_status.set("Disconnected")
