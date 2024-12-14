from datetime import datetime

import cothread
import requests


class PV_Poller:
    def __init__(self, host: str, pv_poller, pv_update_time, target_pvs: list):
        self.host = host
        self.poller_pv = pv_poller
        self.pv_update_time = pv_update_time
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
        print(url)

        response = requests.get(url)
        if not response.ok:
            raise Exception(f"Failed to get values from {self.host}\n{response.text}")

        values = response.json()
        for i, pv in enumerate(self.target_pvs):
            val = values[self.target_pv_names[i]]
            pv.set(val)

        self.pv_update_time.set(datetime.now().strftime("%H:%M:%S. %d/%m/%Y"))
