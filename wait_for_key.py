from pynput.keyboard import Key, Listener


KEY_TO_WAIT_TO = Key.f10


def wait_for_key(key):
    def on_press(key_pressed):
        return key_pressed != key
    with Listener(on_press=on_press) as l:
        l.join()


if __name__ == '__main__':
    wait_for_key(KEY_TO_WAIT_TO)
