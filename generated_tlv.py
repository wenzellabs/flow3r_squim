# this stuff is automagically generated from
# tlv_generator.py - do not edit

import struct


# base TLV Packet class
class TLVPacket:
    type_class_map = {}

    def __init__(self, type, payload):
        self.type = type
        self.len = 2 + len(payload)  # header length is 2 bytes
        self.payload = payload

    def to_bytes(self):
        header = struct.pack('<BB', self.type, self.len)
        return header + self.payload

    @staticmethod
    def from_bytes(data):
        type, length = struct.unpack('<BB', data[:2])
        payload = data[2:length]
        packet_class = TLVPacket.type_class_map.get(type, TLVPacket)
        return packet_class.from_bytes(data)

    @classmethod
    def register_type(cls, tlv_nonce):
        def wrapper(subclass):
            cls.type_class_map[tlv_nonce] = subclass
            return subclass
        return wrapper


# derived classes for specific TLV types

@TLVPacket.register_type(0x01)
class TLVPacketTime(TLVPacket):
    def __init__(self, us_since_1900):
        tlv_nonce = 0x01
        self.us_since_1900 = us_since_1900
        payload = struct.pack('<Q', us_since_1900)
        super().__init__(tlv_nonce, payload)

    @staticmethod
    def from_bytes(data):
        us_since_1900, = struct.unpack('<Q', data[2:])
        return TLVPacketTime(us_since_1900, )

@TLVPacket.register_type(0x11)
class TLVPacketNoteOn(TLVPacket):
    def __init__(self, us_since_1900, note, channel, velocity):
        tlv_nonce = 0x11
        self.us_since_1900 = us_since_1900
        self.note = note
        self.channel = channel
        self.velocity = velocity
        payload = struct.pack('<QBBB', us_since_1900, note, channel, velocity)
        super().__init__(tlv_nonce, payload)

    @staticmethod
    def from_bytes(data):
        us_since_1900, note, channel, velocity, = struct.unpack('<QBBB', data[2:])
        return TLVPacketNoteOn(us_since_1900, note, channel, velocity, )

@TLVPacket.register_type(0x12)
class TLVPacketNoteOff(TLVPacket):
    def __init__(self, us_since_1900, note, channel, velocity):
        tlv_nonce = 0x12
        self.us_since_1900 = us_since_1900
        self.note = note
        self.channel = channel
        self.velocity = velocity
        payload = struct.pack('<QBBB', us_since_1900, note, channel, velocity)
        super().__init__(tlv_nonce, payload)

    @staticmethod
    def from_bytes(data):
        us_since_1900, note, channel, velocity, = struct.unpack('<QBBB', data[2:])
        return TLVPacketNoteOff(us_since_1900, note, channel, velocity, )

@TLVPacket.register_type(0x13)
class TLVPacketNoteOnOff(TLVPacket):
    def __init__(self, on, off, note, channel, velocity):
        tlv_nonce = 0x13
        self.on = on
        self.off = off
        self.note = note
        self.channel = channel
        self.velocity = velocity
        payload = struct.pack('<QQBBB', on, off, note, channel, velocity)
        super().__init__(tlv_nonce, payload)

    @staticmethod
    def from_bytes(data):
        on, off, note, channel, velocity, = struct.unpack('<QQBBB', data[2:])
        return TLVPacketNoteOnOff(on, off, note, channel, velocity, )

@TLVPacket.register_type(0x1f)
class TLVPacketPanic(TLVPacket):
    def __init__(self):
        tlv_nonce = 0x1f
        payload = b''
        super().__init__(tlv_nonce, payload)

    @staticmethod
    def from_bytes(data):
        return TLVPacketPanic()

@TLVPacket.register_type(0x20)
class TLVPacketBeat(TLVPacket):
    def __init__(self, bpm, count):
        tlv_nonce = 0x20
        self.bpm = bpm
        self.count = count
        payload = struct.pack('<BI', bpm, count)
        super().__init__(tlv_nonce, payload)

    @staticmethod
    def from_bytes(data):
        bpm, count, = struct.unpack('<BI', data[2:])
        return TLVPacketBeat(bpm, count, )

@TLVPacket.register_type(0x21)
class TLVPacketStart(TLVPacket):
    def __init__(self, us_since_1900, bpm, count):
        tlv_nonce = 0x21
        self.us_since_1900 = us_since_1900
        self.bpm = bpm
        self.count = count
        payload = struct.pack('<QBI', us_since_1900, bpm, count)
        super().__init__(tlv_nonce, payload)

    @staticmethod
    def from_bytes(data):
        us_since_1900, bpm, count, = struct.unpack('<QBI', data[2:])
        return TLVPacketStart(us_since_1900, bpm, count, )

@TLVPacket.register_type(0x30)
class TLVPacketKeyNotes(TLVPacket):
    def __init__(self, root, third, fifth, seventh, ninth, eleventh, thirteenth):
        tlv_nonce = 0x30
        self.root = root
        self.third = third
        self.fifth = fifth
        self.seventh = seventh
        self.ninth = ninth
        self.eleventh = eleventh
        self.thirteenth = thirteenth
        payload = struct.pack('<BBBBBBB', root, third, fifth, seventh, ninth, eleventh, thirteenth)
        super().__init__(tlv_nonce, payload)

    @staticmethod
    def from_bytes(data):
        root, third, fifth, seventh, ninth, eleventh, thirteenth, = struct.unpack('<BBBBBBB', data[2:])
        return TLVPacketKeyNotes(root, third, fifth, seventh, ninth, eleventh, thirteenth, )

@TLVPacket.register_type(0x31)
class TLVPacketChord(TLVPacket):
    def __init__(self, on, off, note):
        tlv_nonce = 0x31
        self.on = on
        self.off = off
        self.note = note
        payload = struct.pack('<QQ16B', on, off, *note)
        super().__init__(tlv_nonce, payload)

    @staticmethod
    def from_bytes(data):
        on, off, *note, = struct.unpack('<QQ16B', data[2:])
        return TLVPacketChord(on, off, note, )

@TLVPacket.register_type(0x32)
class TLVPacketScale(TLVPacket):
    scale_type_map = {
        'major': 1,
        'minor': 2,
        'harmonic_minor': 3,
        'melodic_minor': 4,
        'dorian': 5,
        'phrygian': 6,
        'lydian': 7,
        'mixolydian': 8,
        'locrian': 9,
        'major_pentatonic': 10,
        'minor_pentatonic': 11,
        'blues_minor': 12,
        'blues_major': 13,
        'whole_tone': 14,
        'chromatic': 15,
    }
    def __init__(self, root, scale_type):
        tlv_nonce = 0x32
        self.root = root
        self.scale_type = scale_type
        scale_type_mapped = self.scale_type_map.get(scale_type)
        if scale_type_mapped is None:
            # FIXME print is not the smartes move, but raise would be worse
            print(f' invalid enum {scale_type}')
        payload = struct.pack('<BB', root, scale_type_mapped)
        super().__init__(tlv_nonce, payload)

    @staticmethod
    def from_bytes(data):
        root, *scale_type_id, = struct.unpack('<BB', data[2:])
        # reverse lookup for scale_type_name
        scale_type_name = next(
            (name for name, value in TLVPacketScale.scale_type_map.items() if value == scale_type_id),
            None
        )
        if scale_type_name is None:
            # FIXME print is not the smartes move, but raise would be worse
            print(f'unknown scale_type_id {scale_type_id}')
        return TLVPacketScale(root, scale_type_name, )

@TLVPacket.register_type(0x23)
class TLVPacketArtist(TLVPacket):
    def __init__(self, artist):
        tlv_nonce = 0x23
        self.artist = artist
        payload = struct.pack('<234b', *artist)
        super().__init__(tlv_nonce, payload)

    @staticmethod
    def from_bytes(data):
        *artist, = struct.unpack('<234b', data[2:])
        return TLVPacketArtist(artist, )

@TLVPacket.register_type(0x24)
class TLVPacketTitle(TLVPacket):
    def __init__(self, title):
        tlv_nonce = 0x24
        self.title = title
        payload = struct.pack('<234b', *title)
        super().__init__(tlv_nonce, payload)

    @staticmethod
    def from_bytes(data):
        *title, = struct.unpack('<234b', data[2:])
        return TLVPacketTitle(title, )

@TLVPacket.register_type(0x40)
class TLVPacketLedColor(TLVPacket):
    def __init__(self, led, r, g, b):
        tlv_nonce = 0x40
        self.led = led
        self.r = r
        self.g = g
        self.b = b
        payload = struct.pack('<BBBB', led, r, g, b)
        super().__init__(tlv_nonce, payload)

    @staticmethod
    def from_bytes(data):
        led, r, g, b, = struct.unpack('<BBBB', data[2:])
        return TLVPacketLedColor(led, r, g, b, )


# end of automagically generated code
