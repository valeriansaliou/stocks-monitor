#!/usr/bin/env python

import websocket, thread, time, json
from Adafruit_CharLCD import Adafruit_CharLCD



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

        self.__lcd.begin(16,1)
        self.__lcd.clear()
        self.__lcd.message('Salut')
        self.ws = websocket.WebSocketApp('wss://websocket.mtgox.com:443/mtgox?Currency={currency}'.format(currency=self.__currency),
                                          on_message = self.on_message,
                                          on_error = self.on_error,
                                          on_close = self.on_close,
                                          on_open = self.on_open
                                        )
        self.ws.run_forever()

    def on_message(self, ws, message):
        if message:
            msg = json.loads(message)

            if msg['private'] == 'ticker':
                value = msg['ticker']['buy']['value']

                if value >= 0 and value != self.__last_value:
                    self.__last_value = value
                    print Colors.OKBLUE + ('Value changed to: %s %s' % (self.__last_value, self.__currency)) + Colors.ENDC

                    self.__lcd.clear()
		    self.__lcd.message(str(self.__last_value))
                    
		    

    def on_error(self, ws, error):
        print error

    def on_close(self, ws):
        print '### closed ###'

    def on_open(self, ws):
        print Colors.OKGREEN + 'Socket opened' + Colors.ENDC


if __name__ == '__main__':
    # Debug
    websocket.enableTrace(True)
    lcd = Adafruit_CharLCD()
    lcd.begin(16,1)
    Socket('USD',lcd)
