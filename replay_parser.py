import json
import lzma

__author__ = "Ugrend"
"""
Copyright (c) 2016 Ugrend

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""

MODS = {"NONE": {"value": 0, "multi": 1, "code": "", "name": "No Mod", "icon": ""},
        "NO_FAIL": {"value": 1, "multi": 0.5, "code": "NF", "name": "No Fail", "icon": "selection_mod_nofail"},
        "EASY": {"value": 2, "multi": 0.5, "code": "EZ", "name": "Easy", "icon": "selection_mod_easy"},
        "NO_VIDEO": {"value": 4, "multi": 1, "code": "", "name": "No Video", "icon": ""},
        "HIDDEN": {"value": 8, "multi": 1.06, "code": "HD", "name": "Hidden", "icon": "selection_mod_hidden"},
        "HARD_ROCK": {"value": 16, "multi": 1.06, "code": "HR", "name": "Hard Rock", "icon": "selection_mod_hardrock"},
        "SUDDEN_DEATH": {"value": 32, "multi": 1, "code": "SD", "name": "Sudden Death",
                         "icon": "selection_mod_suddendeath"},
        "DOUBLE_TIME": {"value": 64, "multi": 1.12, "code": "DT", "name": "Double Time",
                        "icon": "selection_mod_doubletime"},
        "RELAX": {"value": 128, "multi": 0, "code": "", "name": "", "icon": ""},
        "HALF_TIME": {"value": 256, "multi": 0.3, "code": "HT", "name": "Half Time", "icon": "selection_mod_halftime"},
        "NIGHT_CORE": {"value": 512, "multi": 1.12, "code": "NT", "name": "Night Core",
                       "icon": "selection_mod_nightcore"},
        "FLASH_LIGHT": {"value": 1024, "multi": 1.12, "code": "FL", "name": "Flash Light",
                        "icon": "selection_mod_flashlight"},
        "AUTO_PLAY": {"value": 2048, "multi": 0, "code": "", "name": "Auto Play", "icon": ""},
        "SPUN_OUT": {"value": 4096, "multi": 0.9, "code": "SO", "name": "Spun Out", "icon": "selection_mod_spunout"},
        "RELAX_2": {"value": 8192, "multi": 0, "code": "AP", "name": "Auto Pilot", "icon": ""},
        "PERFECT": {"value": 16384, "multi": 1, "code": "PF", "name": "Perfect", "icon": "selection_mod_perfect"}}

KEYS = {"NONE": 0, "M1": 1, "M2": 2, "K1": 4, "K2": 8, "SMOKE": 16}


class ReplayParser:
    def __init__(self):
        self.loaded = False
        self.__byteIndex = 0

    def load_from_file(self, filename):
        with open(filename, 'rb') as f:
            data = f.read()
        self.load_replay(data)

    def load_replay(self, data):
        self.data = data
        self.replay = {
            'type': self.__get_byte(),
            'version': self.__get_int(),
            'bmMd5Hash': self.__get_string(),
            'playerName': self.__get_string(),
            'rMd5Hash': self.__get_string(),
            'h300': self.__get_short(),
            'h100': self.__get_short(),
            'h50': self.__get_short(),
            'hGekis': self.__get_short(),
            'hKatus': self.__get_short(),
            'tScore': self.__get_int(),
            'tCombo': self.__get_short(),
            'hMisses': self.__get_short(),
            'fullClear': self.__get_byte(),
            'mods': self.__get_int(),
            'lifeBar': self.__get_string(),
            'time_played': int((self.__get_long() - 621355968000000000) / 10000),
            'replayByteLength': self.__get_int(),
        }
        self.replay['replayData'] =self.__decode_replay()
        for k, v in self.replay.items():
            setattr(self, k, v)
        self.loaded = True

    def get_mods(self):
        return self.__get_mods(self.replay['mods'])

    def to_json(self, indent=None):
        if self.loaded:
            return json.dumps(self.replay, indent=indent)

    def get_replay(self):
        if self.loaded:
            return self.replay

    def __get_byte(self):
        result = self.data[self.__byteIndex]
        self.__byteIndex += 1
        return result

    def __get_short(self):
        return self.__get_byte() | (self.__get_byte() << 8)

    def __get_int(self):
        return self.__get_byte() | (self.__get_byte() << 8) | (self.__get_byte() << 16) | (self.__get_byte() << 24)

    def __get_long(self):
        return self.__get_int() + self.__get_int() * 0x100000000

    def __get_ueb128(self):
        t = 0
        s = 0
        while (True):
            byte = self.__get_byte()
            t |= ((byte & 0x7F) << s)
            if (byte & 0x80) == 0:
                break
            s += 7
        return t

    def __get_string(self):
        start_byte = self.__get_byte()
        if start_byte == 0x0B:
            len = self.__get_ueb128()
            s = ""
            for i in range(len):
                s += chr(self.__get_byte())
            return s
        return ""

    @staticmethod
    def __get_mods(val):
        """
        Gets the mods for mod int
        :param val: (int) of mods
        :return:
        """
        mods = []
        if val == 0:
            mods.append(MODS['NONE'])
            return mods
        for k, v in MODS.items():
            bit = val & v['value']
            if bit == v['value'] and bit != 0:
                mods.append(v)
        return mods

    @staticmethod
    def __get_keys(key):
        keys = []
        if key == 0:
            keys.append(KEYS['NONE'])
            return keys
        for k, v in KEYS.items():
            bit = key & v
            if bit == v and bit != 0:
                keys.append(v)
        if KEYS['M1'] in keys and KEYS['K1'] in keys:
            keys.remove(KEYS['M1'])

        if KEYS['M2'] in keys and KEYS['K2'] in keys:
            keys.remove(KEYS['M2'])

        return keys

    def __decode_replay(self):
        replay_data = []
        lzma_data = self.data[self.__byteIndex:self.__byteIndex+self.replay['replayByteLength']]
        replay_events = lzma.decompress(lzma_data, format=lzma.FORMAT_AUTO).decode('ascii')[:-1].split(",")
        last_time_frame = 0
        for i in replay_events:
            split_data = [float(x) for x in i.split('|')]
            if len(split_data) < 4:
                continue
            if split_data[0] > 0:
                time = split_data[0]
                split_data[0] = time + last_time_frame
                last_time_frame += time
            replay_data.append({
                't': split_data[0],
                'x': split_data[1],
                'y': split_data[2],
                'keys': self.__get_keys(int(split_data[3]))
            })
        return replay_data


if __name__ == "__main__":
    r = ReplayParser()
    r.load_from_file('main.py')
    print(r.to_json(indent=4))
