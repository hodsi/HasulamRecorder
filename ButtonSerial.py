import time
import thread
import serial

TIMEOUT = 0.05


class ButtonSerial:

    def __init__(self, com_port=3):
        self.com_port = com_port
        self.serial_instance = None
        self.call_back_functions = []
        
    def __del__(self):
        self.close()

    def register_call_back(self, *call_back_functions):
        self.call_back_functions.extend(call_back_functions)

    def start_calling_callbacks(self):
        thread.start_new_thread(self.call_back_main_loop, ())

    def call_back_main_loop(self):
        while True:
            if self.is_on():
                for func in self.call_back_functions:
                    func()
                while self.is_on():
                    time.sleep(TIMEOUT)
                    continue
            time.sleep(TIMEOUT)

    def close(self):
        if self.serial_instance:
            self.serial_instance.close()
        self.serial_instance = None
        
    def is_communication_available(self):

        if not self.serial_instance.isOpen():
            return False
        
        for i in range(5):
            try:
                self.serial_instance.flushInput()
                self.serial_instance.flushOutput()
                self.serial_instance.write("\xab\xab")
                if self.serial_instance.read(1) == "\xab":
                    time.sleep(TIMEOUT)
                    return True
            except serial.SerialTimeoutException:
                pass
            except:
                break
        return False

    def is_on(self):
        try:
            if not self.serial_instance:
                self.serial_instance = serial.Serial(port='COM%d' % self.com_port, timeout=TIMEOUT)
                
                if not self.serial_instance.isOpen():
                    print("Error: Cannot connect to serial!")
                    return False
                
            return self.is_communication_available()

        except KeyboardInterrupt:
            raise
        except Exception as e:
            print("Exception: %s" % str(e))
            self.close()
            
        return False
    
    def is_off(self):
        return not self.is_on()


