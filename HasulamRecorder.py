import os
from threading import RLock

from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

from ButtonSerial import ButtonSerial
import time
from pywinauto import application
import threading

# RECORDING_SOFTWARE = "Debut"
RECORDING_SOFTWARE = "WMEncoder"

CONTROL_PROGRAM_PATH = r"C:\Program Files (x86)\HasulamRecorderButton\RecorderGUI.exe"

if RECORDING_SOFTWARE == "Debut":

    PROGRAM_PATH = r"C:\Program Files\NCH Software\Debut\debut.exe"
    MAIN_WINDOW_TEXT = "Debut Professional"
    MAIN_WINDOW_CLASS_NAME = None

    MENU_START_RECORD = "File->Record"
    MENU_PAUSE_RECORD = "File->Pause"

elif RECORDING_SOFTWARE == "WMEncoder":

    PROGRAM_PATH = r"C:\Program Files (x86)\Windows Media Components\Encoder\wmenc.exe"
    MAIN_WINDOW_TEXT = "Windows Media Encoder"
    MAIN_WINDOW_CLASS_NAME = "MS Windows Media Encoder"

    MENU_START_RECORD = "&Control->Start &Encoding"
    MENU_PAUSE_RECORD = "&Control->&Pause"


def screen_log(txt):
    print(time.strftime("%H:%M") + ": " + txt)


BUTTON_PORT = 3

VIDEO_FOLDER = 'X:\\NewLessons'
VIDEO_EXTENSION = '.wmv'

WAIT_FOR_KEY_PATH = 'wait_for_key.py'
KEY_TO_PRESS = 'F10'



def cut_video(video_path, end_time, target_name):
    if end_time == 0:
        screen_log('Not Cutting from the end because a recording wasn\'t made')
    with VideoFileClip(video_path) as source_clip:
        source_length = source_clip.duration
    screen_log(
        'cutting {} from {} to {} into {}'.format(video_path, source_length - end_time, source_length, target_name))
    return ffmpeg_extract_subclip(video_path, source_length - end_time, source_length, target_name)


def get_ext(filename):
    return os.path.splitext(filename)[-1].lower()


def get_latest_filename(folder):
    file_names = (filename for filename in os.listdir(folder) if get_ext(filename) == VIDEO_EXTENSION)
    file_names = (os.path.join(folder, filename) for filename in file_names)
    return sorted(file_names, key=os.path.getctime, reverse=True)[0]


def convert_to_new_file_name(filename):
    new_file_dir_name = os.path.dirname(filename)
    new_file_name = 'summary_' + os.path.basename(filename)
    return os.path.join(new_file_dir_name, new_file_name)


class Stopwatch:
    def __init__(self):
        self._start = time.clock()
        self._end = self._start

    @property
    def duration(self):
        if self._start is None:
            return 0
        return self._end - self._start if self._end else time.clock() - self._start

    @property
    def running(self):
        return self._start and not self._end

    def start(self):
        if not self.running:
            self._start = time.clock() - self.duration
            self._end = None

    def stop(self):
        if self.running:
            self._end = time.clock()

    def chang_state(self):
        if self.running:
            self.stop()
            screen_log('Recorded {} seconds, than stopped recording'.format(self.duration))
        else:
            self.start()
            screen_log('Started recording')

def wait_for_key():
    os.system(WAIT_FOR_KEY_PATH)


def record_from_middle(button_serial, recorder, lock):
    print('Press {} at any time to start recording from that point\n'.format(KEY_TO_PRESS))
    wait_for_key()
    stop_watch = Stopwatch()
    with lock:
        if recorder.is_on:
            stop_watch.start()
        button_serial.register_call_back(stop_watch.chang_state)
    try:
        print('Press {} at any time to save the recording\n'.format(KEY_TO_PRESS))
        wait_for_key()
    finally:
        screen_log('{} pressed. Cutting the lessons {} seconds from the end.'.format(KEY_TO_PRESS, stop_watch.duration))
        video_name_to_cut = get_latest_filename(VIDEO_FOLDER)
        dst_video_name = convert_to_new_file_name(video_name_to_cut)
        cut_video(video_name_to_cut, stop_watch.duration, dst_video_name)


class MMRecordControl:

    def __init__(self):
        self.app = application.Application()
        self.main_window = None

        self.control_app = application.Application()
        self.control_window = None

        self.is_on = False

    def gui_send_state(self, is_record):
        if self.control_window is None:
            self.control_window = None
            try:
                self.control_app.connect(path=CONTROL_PROGRAM_PATH)
                self.control_window = self.control_app.Windows_()[0]
                screen_log("Recording Monitor FOUND and made controllable!")
            except:
                screen_log("Error finding Recording Monitor")
                return False

        if self.control_window is not None:
            if is_record:
                self.control_window.TypeKeys("^R")
            else:
                self.control_window.TypeKeys("^S")
            return True
        return False

    def is_window_available(self):
        if self.main_window is None or not self.main_window.Exists():
            self.main_window = None
            try:
                self.app.connect(path=PROGRAM_PATH)
                self.main_window = self.app.window_(title_re=(".*" + MAIN_WINDOW_TEXT),
                                                    class_name=MAIN_WINDOW_CLASS_NAME)

                screen_log("Recording Application FOUND and made controllable!")
            except:
                return False

        return self.main_window and self.main_window.Exists()

    def is_in_record_mode(self):
        return (not self.main_window.MenuItem(MENU_START_RECORD).IsEnabled()) and self.main_window.MenuItem(
            MENU_PAUSE_RECORD).IsEnabled()

    def record(self):
        record_menu_item = self.main_window.MenuItem(MENU_START_RECORD)
        if record_menu_item.IsEnabled():
            record_menu_item.Select()
            return True
        return False

    def pause(self):
        self.main_window.MenuSelect(MENU_PAUSE_RECORD)

    def button_pressed(self):
        self.is_on = not self.is_on

    def wait_for_state_and_get_mode(self, required_state):
        start_time = time.time()
        while self.is_in_record_mode() != required_state and start_time + 4 > time.time():
            time.sleep(0.5)
        return self.is_in_record_mode()


def main():
    lock = RLock()

    recorder = MMRecordControl()

    bs = ButtonSerial(3)
    bs.register_call_back(recorder.button_pressed)

    record_from_middle_thread = threading.Thread(target=record_from_middle, args=(bs, recorder, lock))
    record_from_middle_thread.start()

    bs.start_calling_callbacks()
    recorder.gui_send_state(False)

    while True:

        error_massage = None
        try:
            if recorder.is_window_available():
                with lock:
                    if recorder.is_on:
                        if not recorder.is_in_record_mode():
                            if recorder.record():
                                recorder.gui_send_state(True)
                                if not recorder.wait_for_state_and_get_mode(True):
                                    error_massage = "Record button clicked, but was not passed to Record Mode!"
                                    recorder.gui_send_state(False)
                                else:
                                    screen_log("Recording Started!")

                            else:
                                error_massage = "Record button is not available for recording!"

                    else:
                        if recorder.is_in_record_mode():
                            recorder.pause()
                            recorder.gui_send_state(False)
                            if recorder.wait_for_state_and_get_mode(False):
                                error_massage = "Cancel button clicked, but was not passed to Idle Mode!"
                                recorder.gui_send_state(True)
                            else:
                                screen_log("Recording Stoped!")

            else:
                error_massage = "Application was not found on desktop. please open application."

        except KeyboardInterrupt:
            screen_log("Keyboard Interrupt. Shuting down application.")
            break

        except Exception as e:
            # raise
            error_massage = str(e)

        if error_massage:
            # Show error_massage in Screen
            screen_log("error_massage: " + error_massage)
            time.sleep(5)
        else:
            time.sleep(0.1)


if __name__ == '__main__':
    main()
