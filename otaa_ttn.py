#!/usr/bin/env python3
import sys
from time import sleep
from SX127x.LoRa import *
from SX127x.LoRaArgumentParser import LoRaArgumentParser
from SX127x.board_config import BOARD
import LoRaWAN
from LoRaWAN.MHDR import MHDR
from random import randrange

BOARD.setup()
parser = LoRaArgumentParser("LoRaWAN sender")

class LoRaWANotaa(LoRa):
    def __init__(self, verbose = False):
        super(LoRaWANotaa, self).__init__(verbose)

    def on_rx_done(self):
        print("RxDone")

        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True)

        lorawan = LoRaWAN.new([], appkey)
        lorawan.read(payload)
        print(lorawan.get_payload())
        print(lorawan.get_mhdr().get_mversion())

        if lorawan.get_mhdr().get_mtype() == MHDR.JOIN_ACCEPT:
            print("Got LoRaWAN join accept")
            print(lorawan.valid_mic())
            print(lorawan.get_devaddr())
            print(lorawan.derive_nwskey(devnonce))
            print(lorawan.derive_appskey(devnonce))
            print("\n")
            sys.exit(0)

        print("Got LoRaWAN message continue listen for join accept")

    def on_tx_done(self):
        self.clear_irq_flags(TxDone=1)
        print("TxDone")

        self.set_mode(MODE.STDBY)
        self.set_dio_mapping([0,0,0,0,0,0])
        self.set_invert_iq(1)
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)

    def start(self):
        self.tx_counter = 1

        lorawan = LoRaWAN.new(appkey)
        lorawan.create(MHDR.JOIN_REQUEST, {'deveui': deveui, 'appeui': appeui, 'devnonce': devnonce})

        self.write_payload(lorawan.to_raw())
        self.set_mode(MODE.TX)

        BOARD.blink(.3, 5)

        while True:
            sleep(1)


# Init
#devEUI: 70 B3 D5 7E D0 04 40 37
deveui = [0x70, 0xB3, 0xD5, 0x7E, 0xD0, 0x04, 0x40, 0x37]
#deveui = [0x37, 0x40, 0x04, 0xD0, 0x7E, 0xD5, 0xB3, 0x70]

#AppEUI: 70 B3 D5 7E F0 00 51 34
appeui = [0x70, 0xB3, 0xD5, 0x7E, 0xF0, 0x00, 0x51, 0x34]
#AppKey: C1 DA CF DE 6D 39 E8 12 90 86 7E CF DC 9B 6B 66
appkey = [0xC1, 0xDA, 0xCF, 0xDE, 0x6D, 0x39, 0xE8, 0x12, 0x90, 0x86, 0x7E, 0xCF, 0xDC, 0x9B, 0x6B, 0x66]
#appkey = [0x66, 0x6B, 0x9B, 0xDC, 0xCF, 0x7E, 0x86, 0x90, 0x12, 0xE8, 0x39, 0x6D, 0xDE, 0xCF, 0xDA, 0xC1]

devnonce = [randrange(256), randrange(256)]
lora = LoRaWANotaa(True, True, 915)

# Setup
lora.set_mode(MODE.SLEEP)
lora.set_dio_mapping([1,0,0,0,0,0])
lora.set_freq(912.1) #CH_05_US=913.88
lora.set_pa_config(pa_select=1)
lora.set_spreading_factor(10)
lora.set_coding_rate(1)
lora.set_bw(7) # 9 = 500k
lora.set_pa_config(max_power=0x0F, output_power=0x0E)
lora.set_sync_word(0x34)
lora.set_rx_crc(True)

print(lora)
assert(lora.get_agc_auto_on() == 1)

try:
    print("Sending LoRaWAN join request\n")
    lora.start()
except KeyboardInterrupt:
    sys.stdout.flush()
    print("\nKeyboardInterrupt")
finally:
    sys.stdout.flush()
    lora.set_mode(MODE.SLEEP)
    BOARD.teardown()
