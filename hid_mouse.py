"""
Little tool to change the led effect on the Glorious Model O mouse.

This is very incomplete since I personally don't need the other
commands... yet.

Many thanks to Samuel Čavoj for doing the reverse engineering job
and sharing it at https://rustrepo.com/repo/sammko-gloryctl-rust-utilities

This code used the hid package, using the hidapi library.
It also needs to run as root, until I found a better solution.

On macOS, hidapi is available through brew.
"""
import argparse

import hid

from hid_glorious import (EffectDirection,
                          GloriousEffect,
                          GloriousModelORecord,
                          model_O_ids)

device_path = None

parser = argparse.ArgumentParser()
group_args = parser.add_mutually_exclusive_group(required=False)
group_args.add_argument('--off', help='Disable led', action='store_true')
group_args.add_argument('--glorious', help='Glorious effect, opt: direction (0/1), speed (1-4)', action='store_true')
group_args.add_argument('--single', help='Single fix colour, opt: RGB hex value, brightness (1-4)', action='store_true')
group_args.add_argument('--breath', help='Breathing with custom colours, opt: speed (1-4), upto seven RGB hex values', action='store_true')
group_args.add_argument('--tail', help='Random finger to palm, opt: brightness (1-4), speed (1-4)', action='store_true')
group_args.add_argument('--seamless', help='Seamless breathing. opt speed (1-4)', action='store_true')
group_args.add_argument('--six', help='Six fixed colours', action='store_true')
group_args.add_argument('--rave', help='Two colours rave, opt: brightness (1-4), speed (1-3), two RGB vex values ', action='store_true')
group_args.add_argument('--random', help='Random changing colours on each led, opt: speed (1-3)', action='store_true')
group_args.add_argument('--wave', help='Colour wave from palm to finger, opt: brightness (1-4), speed (1-3)', action='store_true')
group_args.add_argument('--breath_mono', help='Single colour breathing, opt speed (1-4), RGB hex value', action='store_true')
parser.add_argument('--config', help='Prints the current configuration', action='store_true')
parser.add_argument('--raw_config', help='Prints the current raw configuration', action='store_true')
args = parser.parse_known_args()
# Not the best, but it's working.
extra = args[1]  # Extra parameter for option customization
args = args[0]

devices = hid.enumerate(model_O_ids.vid, model_O_ids.pid)
if not len(devices):
    print('Device not present')
    exit(0)
for device in devices:
    if (
        device['vendor_id'] == model_O_ids.vid
        and device['product_id'] == model_O_ids.pid
        and device['usage'] == model_O_ids.usage_id
        and device['usage_page'] == model_O_ids.usage_page
    ):
        device_path = device['path']
        break

if device_path is None:
    print('Device not present')
    exit(0)

try:
    with hid.Device(path=device_path) as h:
        version_req = b'\x05\x11\x00\x00\x00\x00'
        res = h.send_feature_report(version_req)
        config = h.get_feature_report(0x04, 520)
        mor = GloriousModelORecord(config)
        update = False
        if args.off:
            mor.effect = GloriousEffect.OFF
            update = True
        elif args.glorious:
            if len(extra):
                try:
                    mor.glorious_direction = EffectDirection(int(extra[0]))
                    if len(extra) > 1:
                        mor.glorious_speed = int(extra[1])
                except ValueError:
                    pass
            mor.effect = GloriousEffect.GLORIOUS
            update = True
        elif args.single:
            if len(extra):
                try:
                    mor.single_rgb = int(extra[0], 16)
                    if len(extra) > 1:
                        mor.single_rgb_brightness = int(extra[1])
                except ValueError:
                    pass
            mor.effect = GloriousEffect.SINGLE_COLOUR
            update = True
        elif args.breath:
            if len(extra):
                try:
                    mor.breath_speed = int(extra[0])
                    if len(extra) > 1:
                        values = []
                        count = len(extra) - 1
                        if count > 7:
                            count = 7
                        for pos in range(1, count + 1):
                            values.append(int(extra[pos], 16))
                        mor.breath_rgbs = values
                except ValueError:
                    pass
            mor.effect = GloriousEffect.BREATHING
            update = True
        elif args.tail:
            if len(extra):
                try:
                    mor.tail_brightness = int(extra[0])
                    if len(extra) > 1:
                        mor.tail_speed = int(extra[1])
                except ValueError:
                    pass
            mor.effect = GloriousEffect.TAIL
            update = True
        elif args.seamless:
            if len(extra):
                try:
                    mor.x_speed = int(extra[0])
                except ValueError:
                    pass
            mor.effect = GloriousEffect.SEAMLESS_BREATHING
            update = True
        elif args.six:
            if len(extra) == 6:
                try:
                    values = []
                    for pos in range(6):
                        values.append(int(extra[pos], 16))
                    mor.constant_rgbs = values
                except ValueError:
                    pass
            mor.effect = GloriousEffect.CONSTANT_RGB
            update = True
        elif args.rave:
            if len(extra):
                try:
                    mor.rave_brightness = int(extra[0])
                    if len(extra) > 1:
                        mor.rave_speed = int(extra[1])
                    if len(extra) == 4:
                        values = []
                        for pos in range(2, 4):
                            values.append(int(extra[pos], 16))
                        mor.rave_rgbs = values
                except ValueError:
                    pass
            mor.effect = GloriousEffect.RAVE
            update = True
        elif args.random:
            if len(extra):
                try:
                    mor.random_speed = int(extra[0])
                except ValueError:
                    pass
            mor.effect = GloriousEffect.RANDOM
            update = True
        elif args.wave:
            try:
                mor.wave_brightness = int(extra[0])
                if len(extra) > 1:
                    mor.wave_speed = int(extra[1])
            except ValueError:
                pass
            mor.effect = GloriousEffect.WAVE
            update = True
        elif args.breath_mono:
            if len(extra):
                try:
                    mor.single_breath_speed = int(extra[0])
                    if len(extra) > 1:
                        mor.single_breath_rgb = int(extra[1], 16)
                except ValueError:
                    pass
            mor.effect = GloriousEffect.SINGLE_BREATHING
            update = True
        if update:
            res = h.send_feature_report(mor.record)
        if args.config:
            config = h.get_feature_report(0x04, 520)
            mor = GloriousModelORecord(config)
            print(mor)
        if args.raw_config:
            config = h.get_feature_report(0x04, 520)
            base = 0
            while base < len(config):
                print(config[base:base + 16].hex(' '))
                base += 16
except hid.HIDException as err:
    print(f'Error: {err}')
