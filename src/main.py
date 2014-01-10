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

    pin_7 = 7
    pin_8 = 8


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



class Socket(object):
    """
    Socket operations
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
        GPIO.setup(pin_8, GPIO.OUT)
        GPIO.setup(pin_7, GPIO.OUT)

        self.__lcd.begin(16,1)
        self.__lcd.clear()

        self.initialize()


    def initialize(self):
        self.__initializing = True

        print Colors.OKYELLOW + 'Initializing...' + Colors.ENDC

        self.__lcd.clear()
        self.__lcd.message('Initializing... \n')

        data = MtGox().request('/BTCUSD/money/ticker_fast')

        if data:
            sell_value = data.get('sell', {}).get('value', 0)

            if sell_value >= 0:
                self.__last_value = sell_value
                print Colors.OKGREEN + ('Got initial value: %s %s' % (self.__last_value, self.__currency)) + Colors.ENDC

                self.__lcd.clear()
                self.__lcd.message("1 %s = \n" % (self.__currency_value))
                self.__lcd.message(str(self.__last_value) + ' %s \n' %(self.__currency))
                on_pin(pin_8, 1)
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

                    self.on_pin(pin_7, 1)

                    

                    self.check_breakpoint()

                    
		    
    def on_pin(self,pin,value):
        GPIO.output(pin,value)
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
            trigger_variation = 0.01 * float(self.__status_breakpoint) * self.__status_checkpoint
            current_variation = self.__last_value - self.__status_checkpoint

            # There was a significant variation, trigger!
            if abs(current_variation) >= trigger_variation:
                self.__status_checkpoint = self.__last_value

                if current_variation < 0:
                    # Red LED
                    pass
                else:
                    # Green LED
                    pass


if __name__ == '__main__':
    # Debug
    websocket.enableTrace(True)

    Socket(
        'USD',
        Adafruit_CharLCD()
    )
