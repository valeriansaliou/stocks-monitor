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
        self.__initializing = False

        #Initialisation LED
        self.GPIO.setmode(GPIO.BCM)
        self.GPIO.setup(8, GPIO.OUT)
        self.GPIO.setup(7, GPIO.OUT)

        self.__lcd.begin(16,1)
        self.__lcd.clear()

        self.initialize()


    def initialize(self):
        self.__initializing = True

        print Colors.OKYELLOW + 'Initializing...' + Colors.ENDC

        self.__lcd.clear()
        self.__lcd.message('Initializing...')

        data = MtGox().request('/BTCUSD/money/ticker_fast')

        if data:
            sell_value = data.get('sell', {}).get('value', 0)

            if sell_value >= 0:
                self.__last_value = sell_value
                print Colors.OKGREEN + ('Got initial value: %s %s' % (self.__last_value, self.__currency)) + Colors.ENDC

                self.__lcd.clear()
                self.__lcd.message("1 %s = \n" % (self.__currency_value))
                self.__lcd.message(str(self.__last_value) + ' %s \n' %(self.__currency))
                GPIO.output(8, 1)
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
        self.__lcd.message('Lost connection')
        self.__lcd.message('Reconnecting...')

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
                    self.__lcd.message("1 %s = \n" % (self.__currency_value))
                    self.__lcd.message(str(self.__last_value) + ' %s \n' %(self.__currency))

                    GPIO.output(7, 1)
                    
		    

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
            self.__lcd.message('Reconnected, syncing...')
            self.__lcd.message('[!] %s %s' % (self.__last_value, self.__currency))

        self.__initializing = False


if __name__ == '__main__':
    # Debug
    websocket.enableTrace(True)

    Socket(
        'USD',
        Adafruit_CharLCD()
    )
