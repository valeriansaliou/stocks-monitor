#!/usr/bin/env python

# Add lib to PYTHON_PATH
import sys, os, time
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))

# Imports
import websocket, thread, time, json
from Adafruit_CharLCD import Adafruit_CharLCD
from MtGox import MtGox

# GPIO 
try:
    import RPi.GPIO as GPIO
except ImportError:
    import Mock_GPIO as GPIO

PIN_LED_GREEN = 11
PIN_LED_RED = 9

class Colors(object):
    """
    Map colors for terminal
    """

    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    OKYELLOW = '\033[33m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


    @classmethod
    def disable(_class):
        """
        Disable all colors
        """
        _class.HEADER = ''
        _class.OKBLUE = ''
        _class.OKGREEN = ''
        _class.OKYELLOW = ''
        _class.WARNING = ''
        _class.FAIL = ''
        _class.ENDC = ''



class Stocks(object):
    """
    Stocks operations
    """
    def __init__(self, currency='USD', lcd=None):
        self.__last_value = 0
        self.__currency = currency
        self.__lcd = lcd
        self.__currency_value = 'BTC'
        self.__status_checkpoint = None
        self.__status_breakpoint = 1
        self.__initializing = False

        #Initialisation LED
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(PIN_LED_RED, GPIO.OUT)
        GPIO.setup(PIN_LED_GREEN, GPIO.OUT)

        self.__lcd.begin(16,1)
        self.__lcd.clear()

        self.write_pin(PIN_LED_RED, 0)
        self.write_pin(PIN_LED_GREEN, 0)

        self.initialize()


    def initialize(self):
        self.__initializing = True

        print Colors.OKYELLOW + 'Initializing...' + Colors.ENDC

        self.__lcd.clear()
        self.__lcd.message('Initializing... \n')

        data = MtGox().request('/BTCUSD/money/ticker_fast')

        if data:
            buy_value = data.get('buy', {}).get('value', 0)

            if buy_value >= 0:
                self.__last_value = buy_value
                print Colors.OKGREEN + ('Got initial value: %s %s' % (self.__last_value, self.__currency)) + Colors.ENDC

                self.__lcd.clear()
                self.__lcd.message("1 %s = \n" % (self.__currency_value))
                self.__lcd.message(str(self.__last_value) + ' %s \n' %(self.__currency))

        self.check_breakpoint()
        self.open_socket()

        
    def open_socket(self):
        self.ws = websocket.WebSocketApp('wss://websocket.mtgox.com:443/mtgox?Currency={currency}'.format(currency=self.__currency),
                                          on_message = self.on_message,
                                          on_error = self.on_error,
                                          on_close = self.on_close,
                                          on_open = self.on_open
                                        )
        self.ws.run_forever()


    def reopen_socket(self):
        print Colors.HEADER + 'Re-opening socket...' + Colors.ENDC

        self.__lcd.clear()
        self.__lcd.message('Lost connection \n')
        self.__lcd.message('Reconnecting... \n')

        # After a little while...
        time.sleep(5)
        self.open_socket()


    def write_pin(self, pin, value):
        print 'Set GPIO pin %s to %s' % (pin, value)
        GPIO.output(pin,value)


    def on_message(self, ws, message):
        if message:
            msg = json.loads(message)

            if msg['private'] == 'ticker':
                value = msg['ticker']['buy']['value']

                if value >= 0 and value != self.__last_value:
                    self.__last_value = value
                    print Colors.OKBLUE + ('Value changed to: %s %s' % (self.__last_value, self.__currency)) + Colors.ENDC

                    self.__lcd.clear()
                    self.__lcd.message('1 %s = \n' % (self.__currency_value))
                    self.__lcd.message(str(self.__last_value) + ' %s \n' %(self.__currency))

                    self.check_breakpoint()


    def on_error(self, ws, error):
        print Colors.FAIL + ('Error: %s' % error) + Colors.ENDC

        self.reopen_socket()


    def on_close(self, ws):
        print Colors.OKYELLOW + 'Socket closed' + Colors.ENDC

        self.reopen_socket()


    def on_open(self, ws):
        print Colors.OKGREEN + 'Socket opened' + Colors.ENDC

        if self.__initializing is False:
            self.__lcd.clear()
            self.__lcd.message('Reconnected, \n syncing...')
            self.__lcd.message('[!] %s %s' % (self.__last_value, self.__currency))

        self.__initializing = False


    def check_breakpoint(self):
        if self.__status_checkpoint is None:
            self.__status_checkpoint = self.__last_value
        else:
            # Process variation
            trigger_variation = 0.01 * float(self.__status_breakpoint) * float(self.__status_checkpoint)
            current_variation = float(self.__last_value) - float(self.__status_checkpoint)

            print 'Variation: %s' % current_variation

            # There was a significant variation, trigger!
            if abs(current_variation) >= trigger_variation:
                self.__status_checkpoint = self.__last_value

                if current_variation < 0:
                    # Red LED
                    print Colors.FAIL + ('Red LED on') + Colors.ENDC

                    self.write_pin(PIN_LED_RED, 1)
                    self.write_pin(PIN_LED_GREEN, 0)
                else:
                    # Green LED
                    print Colors.OKGREEN + ('Green LED on') + Colors.ENDC

                    self.write_pin(PIN_LED_GREEN, 1)
                    self.write_pin(PIN_LED_RED, 0)


if __name__ == '__main__':
    # Debug
    websocket.enableTrace(True)

    Stocks(
        'USD',
        Adafruit_CharLCD()
    )
