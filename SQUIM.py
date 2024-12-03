from st3m.application import Application, ApplicationContext
from st3m.input import InputController
import st3m.run

from math import cos, sin
from socket import AF_INET, SOCK_DGRAM, socket
import heapq
import time

# hack to be able to run with the generated_tlv.py from both
# the flow3r menu and through `mpremote run SQUIM.py` / REPL
try:
    from .generated_tlv import *
except ImportError:
    import sys
    sys.path.append('/sd/apps/mazzoo-SQUIM')
    from generated_tlv import *

import bl00mbox

square_count = 450
SQUIM_PORT = 11000
POLYPHONY = 32
ANIM_MS = 100
DB_MUTE = -9999

note_names = [
    'C',
    'C#',
    'D',
    'D#',
    'E',
    'F',
    'F#',
    'G',
    'G#',
    'A',
    'A#',
    'B',
]

class NoteBuffer:
    def __init__(self):
        self.buffer = []

    def add_note(self, timestamp, midinote, on_off):
        # sort in notes by timestamp
        heapq.heappush(self.buffer, (timestamp, midinote, on_off))
        print(f'adding note_{"on" if on_off else "off"} {midinote}')

    def poll_next(self, due):
        if self.buffer and self.buffer[0][0] <= due:
            return heapq.heappop(self.buffer)
        return None

class SQUIM(Application):
    def __init__(self, app_ctx: ApplicationContext) -> None:
        super().__init__(app_ctx)
        self.input = InputController()
        self.radius = 5
        self.twist = 2.9645
        self.anim_ms = ANIM_MS
        self.tick = self.anim_ms

        # mada RX socket
        self.udp = socket(AF_INET, SOCK_DGRAM)
        self.udp.bind(('', SQUIM_PORT))
        self.udp.setblocking(0)

        self.artist = 'mazzoo'
        self.title = '    square immersion    '
        self.mqc = 0 # marquee counter

        self.powerup_time = time.ticks_us()

        self.midi2frequency = [440 * (2 ** ((note - 69) / 12)) for note in range(128)]
        self.poly = POLYPHONY
        self.note_buffer = NoteBuffer()
        self.last_note = 'py'
        self._build_synth()

    def marquee(self, the_text, width, counter):
        if len(the_text) <= width:
            cycle_length = max(1, (width - len(the_text)) * 2)
            position = counter % cycle_length
            if position >= (width - len(the_text)):
                position = cycle_length - position
            return " " * position + the_text + " " * (width - len(the_text) - position)
        else:
            scroll_length = len(the_text) - width + 1
            cycle_length = max(1, 2 * scroll_length)
            position = counter % cycle_length
            if position < scroll_length:
                start_idx = position
            else:
                start_idx = 2 * scroll_length - position - 1
            end_idx = start_idx + width
            result = the_text[start_idx:end_idx]
            return result + " " * (width - len(result))

    def draw(self, ctx: Context) -> None:
        ctx.rgb(0, 0, 0).rectangle(-120, -120, 240, 240).fill()

        ctx.rgba(1.0, 1.0, 1.0, 0.3)
        for i in range(23, square_count-1):
            x = 0
            y = 0
            dist = i // 4
            twisted = i * self.twist
            x += cos(twisted) * dist
            y += sin(twisted) * dist
            ctx.save()
            ctx.translate(x, y)
            ctx.rotate(twisted*cos(twisted/square_count))
            ctx.rectangle(-self.radius, -self.radius, self.radius*2, self.radius*2)
            ctx.restore()
            ctx.fill()
        ctx.rgba(0., .8, .5, .8).move_to(-50, -50).text('SQUIM')

        self.mqc += 1
        ctx.rgba(0., .6, 1, .9).move_to(-110, -25).text(f'{self.marquee(self.artist, 17, self.mqc)}')
        ctx.rgba(0., .6, 1, .9).move_to(-110, 25).text(f'{self.marquee(self.title, 17, self.mqc)}')
        #ctx.rgba(5., .5, .8, .8).move_to(-110, 55).text(f'{self.anim_ms}')
        ctx.rgba(5., .5, .8, .8).move_to(-20, 100).text(f'{self.last_note}')

    def think(self, ins: InputState, delta_ms: int) -> None:
        self.input.think(ins, delta_ms)

        if self.input.buttons.app.middle.pressed:
            pass

        if self.input.buttons.app.left.pressed:
            self.twist -= 0.0001
            if self.anim_ms > 1:
                self.anim_ms -= 1
        elif self.input.buttons.app.right.pressed:
            self.twist += 0.0001
            if self.anim_ms < ANIM_MS:
                self.anim_ms += 1

        self.tick -= delta_ms
        while self.tick < 0:
            self.twist += 0.000001
            self.tick += self.anim_ms

        data = ''
        try:
            data, address = self.udp.recvfrom(256)
        except OSError:
            pass
        except:
            print('nope')

        if len(data) > 0:
            self.dispatch_packet(data)

        self.play_due_notes()

    def dispatch_packet(self, data):
        p = TLVPacket.from_bytes(data)
        if isinstance(p, TLVPacketChord):
            self.handle_Chord(p)
        elif isinstance(p, TLVPacketNoteOnOff):
            self.handle_NoteOnOff(p)
        elif isinstance(p, TLVPacketTitle):
            self.handle_Title(p)
        elif isinstance(p, TLVPacketArtist):
            self.handle_Artist(p)
        elif isinstance(p, TLVPacketTime):
            self.handle_Time(p)
        else:
            print(f'got UNHANDLED {p.__class__.__name__}')

    def handle_NoteOnOff(self, p:TLVPacketNoteOnOff) -> None:
        print(f'NoteOnOff for {(p.off-p.on) // 1000} ms we play {p.note}')
        self.note_buffer.add_note(p.on, p.note, True)
        self.note_buffer.add_note(p.off, p.note, False)

    def handle_Chord(self, p:TLVPacketChord) -> None:
        print(f'Chord for {(p.off-p.on) // 1000} ms we play {[n for n in p.note if n != 128]}')
        # start simple, play all chord notes
        for n in p.note:
            if n != 128:
                self.note_buffer.add_note(p.on, n, True)
                self.note_buffer.add_note(p.off, n, False)

    def handle_Title(self, p:TLVPacketTitle) -> None:
        self.title = bytes(p.title).decode('ascii').rstrip('\x00')
        print(f'{self.title=}')

    def handle_Artist(self, p:TLVPacketArtist) -> None:
        self.artist = bytes(p.artist).decode('ascii').rstrip('\x00')
        print(f'{self.artist=}')

    def handle_Time(self, p:TLVPacketTime) -> None:
        self.powerup_time = p.us_since_1900 - time.ticks_us()
        print(f'his master\'s clock strikes {p.us_since_1900} microseconds after 1900')

    def _build_synth(self):
        self.bl00m = bl00mbox.Channel('SQUIM')
        self._osc = [ self.bl00m.new(bl00mbox.plugins.osc) for _ in range(self.poly) ]
        self._osc_idle = [ True for _ in range(self.poly)]
        self._mixer = self.bl00m.new(bl00mbox.plugins.mixer, self.poly)

        for i in range(self.poly):
            self._osc[i].signals.output = self._mixer.signals.input[i]
            self._mixer.signals.input_gain[i].dB = DB_MUTE # off
            self._osc[i].signals.waveform = self._osc[i].signals.waveform.switch.SQUARE

        self._mixer.signals.output = self.bl00m.mixer

    def play_due_notes(self):
        # any notes due for playing?
        note = self.note_buffer.poll_next(self.powerup_time + time.ticks_us())
        if note:
            if note[2]: # NoteOn
                # find a muted osc
                found = False
                for i in range(self.poly):
                    if self._osc_idle[i]:
                        self._osc[i].signals.pitch.freq = self.midi2frequency[note[1]]
                        self.last_note = note_names[note[1]%12] + str(note[1]//12-1)
                        self._mixer.signals.input_gain[i].dB = 0
                        self._osc_idle[i] = False
                        found = True
                        break
                if not found:
                    print(f'WARNING: no free osc found for {note}')
            else: # NoteOff
                # find the osc
                for i in range(self.poly):
                    if not self._osc_idle[i]:
                        if self._osc[i].signals.pitch.freq == self.midi2frequency[note[1]]:
                            self._mixer.signals.input_gain[i].dB = DB_MUTE
                            self._osc_idle[i] = True
            print(f'playing {note}')

    def on_exit(self) -> None:
        if self.bl00m is not None:
            self.bl00m.clear()
            self.bl00m.free = True
        self.bl00m = None

if __name__ == '__main__':
    st3m.run.run_app(SQUIM)
