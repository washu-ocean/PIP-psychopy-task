import serial
from psychopy import logging
import psychopy.constants as psyConst

class AirDevice():

    def __init__(self, 
                 name: str, 
                 serial_device: serial.Serial, 
                 channel_name: str, 
                 flexT: float, 
                 extT: float, 
                 intensity: int, 
                 reps: int,
                 fiber_sample_rate: float,
                 fiber_threshold: int,
                 internal_logging = True) -> None:
        
        if not channel_name in ("A", "B"):
            raise ValueError(f"channel name must be 'A' or 'B', input was {channel_name}")

        self.name = name
        self._serial_device = serial_device
        self._channel_name = channel_name
        self._flexT = flexT
        self._extT = extT
        self._intensity = intensity
        self._reps = reps
        self.fiber_sample_rate = fiber_sample_rate
        self.fiber_threshold = fiber_threshold
        self._should_log = internal_logging
        self.status = psyConst.NOT_STARTED
        self._message_index = 1 if channel_name == "A" else 2
        self._start_time = 0
        self._stop_time = 0


    def read(self, flush = False, no_data = False, tries = 3) -> bytes:
        if not self._serial_device:
            if self._should_log:
                logging.error("serial device is not connected")
            return None
        if flush:
            self._serial_device.reset_input_buffer()
            self._serial_device.readline()
            if no_data:
                return
        data = self._serial_device.readline()
        while (not data) and (tries > 0):
            data = self._serial_device.readline()
            tries -= 1
        return data
    
    
    def _write_to_serial(self, msg: str) -> None:
        if not self._serial_device:
            if self._should_log:
                logging.error("serial device is not connected")
            return
        if self._should_log:
            logging.info(f"to_serial: {msg}")
        self._serial_device.write(f"{msg}\n".encode("utf-8"))


    def data_from_message(self, msg) -> tuple:
        if not msg:
            raise ValueError("Received empty data string")
        msg_values = tuple(int(d.split(b':')[-1]) for d in msg[:-2].split(b','))
        if len(msg_values) == 3:
            # (time, channel A data, channel B data)
            return (msg_values[0], msg_values[self._message_index])
        else:
            # return just the timestamp
            return msg_values
    

    def start(self, wait_for_confirm = True) -> str:
        self.read(flush=True, no_data=True)
        flexTime = int(1000 * self._flexT)
        extTime = int(1000 * self._extT)
        self._write_to_serial(
            f"{self._channel_name},{flexTime},{extTime},{self._intensity},{self._reps}"
        )
        response = self.read()
        if wait_for_confirm:
            while not response.startswith(b'made' + self._channel_name.encode()):
                response = self.read()
        self._start_time = self.data_from_message(response)[0]
        return self._start_time
    

    def stop(self, wait_for_confirm = True) -> str:
        self.read(flush=True, no_data=True)
        self._write_to_serial(f"-1{self._channel_name}")
        response = self.read()
        if wait_for_confirm:
            while not response.startswith(b'stopped' + self._channel_name.encode()):
                response = self.read()
        self._stop_time = self.data_from_message(response)[0]
        return (self._stop_time, (self._stop_time - self._start_time)/1000)
    
    
    def check_fiber_value(self):
        data = self.data_from_message(self.read(flush=True))
        while len(data) != 2:
            data = self.data_from_message(self.read(flush=True))
        time, fiber_val = data
        time_from_start = (time - self._start_time)/1000
        check = False
        if time_from_start % (self._flexT + self._extT) < self._flexT:
            # if in flexion state
            check = fiber_val >= self.fiber_threshold
        else:
            # if in extension state
            check = fiber_val < self.fiber_threshold and fiber_val > 0
        return (check, fiber_val, time_from_start)