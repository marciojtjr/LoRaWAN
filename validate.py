import sys
from time import sleep
from SX127x.LoRa import *
from SX127x.LoRaArgumentParser import LoRaArgumentParser
from SX127x.board_config import BOARD
import LoRaWAN
from LoRaWAN.MHDR import MHDR

from pyRF95 import rf95

DEFAULT_LORA_FREQUENCY = rf95.CH_05_US
LORA_POWER = 23

def exitGracefully(loraObj):
        print("\nexiting gracefully...")            
        loraObj.set_mode_idle()
        print("set lora to idle...")
        sleep(1)
        loraObj.led_off()
        print("running cleanup...")
        loraObj.cleanup()
        sys.exit()

def setupRadio(loraObj): 

    # determine which frequency to broadcast on
    freq = DEFAULT_LORA_FREQUENCY

    loraObj.set_frequency(freq)
    print("freq = " + str(freq) + " MHz")

    # set power levels
    loraObj.set_tx_power(LORA_POWER)
    print("power level = " + str(LORA_POWER))

    # set custom modem config
    bandwidth = rf95.BW_62K5HZ
    coding_rate = rf95.CODING_RATE_4_8
    imp_header = rf95.IMPLICIT_HEADER_MODE_ON
    spreading_factor = rf95.SPREADING_FACTOR_2048CPS
    crc = rf95.RX_PAYLOAD_CRC_ON
    continuous_tx = rf95.TX_CONTINUOUS_MODE_OFF
    timeout = rf95.SYM_TIMEOUT_MSB
    agc_auto = rf95.AGC_AUTO_ON

    #  Low Data Rate Optimisation mandated for when the symbol length exceeds 16ms
    low_data_rate = 0x08 # aka mobile node


    loraObj.spi_write(rf95.REG_1D_MODEM_CONFIG1, \
            bandwidth | coding_rate | imp_header)

    loraObj.spi_write(rf95.REG_1E_MODEM_CONFIG2, \
            spreading_factor | continuous_tx | crc | timeout)

    # low data rate optimize prevents distortion of characters
    loraObj.spi_write(rf95.REG_26_MODEM_CONFIG3, \
            agc_auto | low_data_rate)

    print("bandwidth = " + str(bandwidth))
    print("spreading factor = " + str(spreading_factor))
    print("coding_rate = " + str(coding_rate))
    print("agc_auto = " + str(agc_auto))
    print("current mode = " + str(loraObj.spi_read(rf95.REG_01_OP_MODE)))

    # announce that modem is ready with lighting effects
    for x in range(0, 5):
        loraObj.flash_led(1)

testMenu = {}
def main_menu():
    print("1. lantern-workd/pyRF95")
    print("2. LoRaWAN single DIO")
    testType = int(input("Choose test mode: "))

    if testType > 2:
        sys.exit()
    testMenu[testType]()

def testPyRF95():
    lora = rf95.RF95(0, 25, None, 13)
    if not lora.init(): # returns True if found
        print("radio not found or not ready. please adjust hardware switch to CE0 or try later...")
        exitGracefully(lora)
    else:
        print("radio found...")
        setupRadio(lora)
        print()
        input("Enter any key to continue...")
        exitGracefully(lora)


def testLoRaWAN_singleDIO():  
    BOARD.setup()
    devaddr = [0x26, 0x01, 0x11, 0x5F]
    nwskey = [0xC3, 0x24, 0x64, 0x98, 0xDE, 0x56, 0x5D, 0x8C, 0x55, 0x88, 0x7C, 0x05, 0x86, 0xF9, 0x82, 0x26]
    appskey = [0x15, 0xF6, 0xF4, 0xD4, 0x2A, 0x95, 0xB0, 0x97, 0x53, 0x27, 0xB7, 0xC1, 0x45, 0x6E, 0xC5, 0x45]
    lora = LoRa()
    devaddr = nwkey = appkey = []
    lora.devaddr = devaddr
    lora.nwkey = nwkey
    lora.appkey = appkey

    # Setup
    lora.set_mode(MODE.SLEEP)
    lora.set_dio_mapping([1,0,0,0,0,0])
    lora.set_freq(915.00)
    lora.set_pa_config(pa_select=1)
    lora.set_spreading_factor(7)
    lora.set_pa_config(max_power=0x0F, output_power=0x0E)
    lora.set_sync_word(0x34)
    lora.set_rx_crc(True)

    print(lora)

testMenu = {1: testPyRF95, 2 : testLoRaWAN_singleDIO}
if __name__ == "__main__":
    # Launch main menu
    main_menu()