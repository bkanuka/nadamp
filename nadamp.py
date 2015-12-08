import sys
import time

import RPIO
#RPIO.setwarnings(False)

from pyharmony import auth
from pyharmony import client as harmony_client

class Amp:
    def __init__(self, harmony_ip, harmony_port, email, password):
        self.harmony_ip = harmony_ip
        self.harmony_port = harmony_port
        self.email = email
        self.password = password

        self.amp_id = None

        RPIO.setup(19, RPIO.OUT, initial=RPIO.HIGH)
        RPIO.setup(5, RPIO.IN)
        RPIO.setup(6, RPIO.IN)
        RPIO.setup(13, RPIO.IN)

        self.volmap = {
                (True, True, True): -120,
                (False, True, True): -120,
                (True, False, True): -100,
                (False, False, True): -80,
                (True, True, False): -60,
                (False, True, False): -40,
                (True, False, False): -20,
                (False, False, False): 0,
                }

        self.sourcemap = {
                'bluetooth' : 'InputBluetooth',
                'aux1' : 'InputAux1',
                'aux2' : 'InputAux2',
                'coax' : 'InputCoax2',
                'usb' : 'InputComputer',
                'optical1' : 'InputOptical1',
                'optical2' : 'InputOptical2',
                }

    def get_client(self):
        token = auth.login(self.email, self.password)
        if not token:
            sys.exit('Could not get token from Logitech server.')

        session_token = auth.swap_auth_token(
            self.harmony_ip, self.harmony_port, token)
        if not session_token:
            sys.exit('Could not swap login token for session token.')

        client = harmony_client.create_and_connect_client(
            self.harmony_ip, self.harmony_port, session_token)
        return client

    def get_amp_id(self, client):
        config = client.get_config()

        dev = [ dev for dev in config['device'] if dev['label'] == u'NAD Amp' ][0]
        self.amp_id = dev['id']

    def db_to_vol(self, x):
        return (16.5/20) * x + 99

    def vol_to_db(self, x):
        return (20/16.5) * x - 120

    def get_gpio_values(self):
        return (RPIO.input(5), RPIO.input(6), RPIO.input(13))

    def get_vol(self):
        gpio_val = self.get_gpio_values()
        db = self.volmap[gpio_val]
        vol = self.db_to_vol(db)
        return vol

    def volume_up(self, client):
        if not self.amp_id:
            self.get_amp_id(client)

        client.send_command(self.amp_id, "VolumeUp")
        time.sleep(0.5)

    def volume_down(self, client):
        if not self.amp_id:
            self.get_amp_id(client)

        client.send_command(self.amp_id, "VolumeDown")
        time.sleep(0.5)

    def set_vol(self, x):
        if x < 0 or x > 100:
            raise ValueError('Volume must be between 0 and 100')

        try:
            client = self.get_client()

            if self.get_vol() == 0:
                self.volume_up(client)
                self.volume_up(client)

            if self.get_vol() == 0:
                raise AssertionError('Pressed VolumeUp and no change. Is the Amp on?')

            count = 0
            orig_max_vol = self.get_vol()
            while self.get_vol() == orig_max_vol:
                self.volume_down(client)
                count = count + 1
                if count > 30:
                    raise AssertionError('Pressed VolumeDown and no change. Is the Amp on?')

            while self.get_vol() > x:
                self.volume_down(client)

            vol = self.get_vol()
            while vol < x:
                self.volume_up(client)
                vol = vol + 16.5/10

        finally:
            client.disconnect(wait=True, send_close=True)

    def set_source(self, source):
        if source not in self.sourcemap.keys():
            raise ValueError("Source must be one of: " + str(self.sourcemap.keys()))

        client = self.get_client()
        try:
            if not self.amp_id:
                self.get_amp_id(client)

            client.send_command(self.amp_id, self.sourcemap[source])

        finally:
            client.disconnect(wait=True, send_close=True)
