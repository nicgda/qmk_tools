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
import time

import hid

from hid_glorious import (EffectDirection,
                          GloriousEffect,
                          GloriousModelORecord,
                          model_O_ids)

device_path = None


def auto_int(value):
    return int(value, 0)


parser = argparse.ArgumentParser()
subparser = parser.add_subparsers(dest='cmd')
subparser.add_parser('off', help='Disable led')
sub = subparser.add_parser('glorious', help='Glorious effect')
sub.add_argument('direction', metavar='direction', nargs='?', choices=[0, 1], type=int, help='Finger to palm (0) or palm to finger (1)')
sub.add_argument('speed', metavar='speed', nargs='?', choices=range(1, 5), type=int, help='Animation speed (1-4)')
sub = subparser.add_parser('single', help='Single fix colour')
sub.add_argument('rgb', metavar='RGB', nargs='?', type=auto_int, help='RGB value in hex')
sub.add_argument('brightness', metavar='brightness', nargs='?', choices=range(1, 5), type=int, help='Led brightness (1-4)')
sub = subparser.add_parser('breath', help='Breathing with custom colours')
sub.add_argument('speed', metavar='speed', nargs='?', choices=range(1, 5), type=int, help='Animation speed (1-4)')
sub.add_argument('rgb', metavar='RGB', nargs='*', type=auto_int, help='Upto seven RGB values')
sub = subparser.add_parser('tail', help='Random finger to palm')
sub.add_argument('brightness', metavar='brightness', nargs='?', choices=range(1, 5), type=int, help='Led brightness (1-4)')
sub.add_argument('speed', metavar='speed', nargs='?', choices=range(1, 5), type=int, help='Animation speed (1-4)')
sub = subparser.add_parser('seamless', help='Seamless breathing')
sub.add_argument('speed', metavar='speed', nargs='?', choices=range(1, 5), type=int, help='Animation speed (1-4)')
sub = subparser.add_parser('six', help='Six fixed colours')
sub.add_argument('rgb', metavar='RGB', nargs='*', type=auto_int, help='Six RGB values')
sub = subparser.add_parser('rave', help='Two colours rave')
sub.add_argument('brightness', metavar='brightness', nargs='?', choices=range(1, 5), type=int, help='Led brightness (1-4)')
sub.add_argument('speed', metavar='speed', nargs='?', choices=range(1, 5), type=int, help='Animation speed (1-4)')
sub.add_argument('rgb', metavar='RGB', nargs='*', type=auto_int, help='Two RGB values to switch from')
sub = subparser.add_parser('random', help='Random changing colours on each led')
sub.add_argument('speed', metavar='speed', nargs='?', choices=range(1, 5), type=int, help='Animation speed (1-4)')
sub = subparser.add_parser('wave', help='Colour wave from palm to finger')
sub.add_argument('brightness', metavar='brightness', nargs='?', choices=range(1, 5), type=int, help='Led brightness (1-4)')
sub = subparser.add_parser('breath_mono', help='Single colour breathing')
sub.add_argument('speed', metavar='speed', nargs='?', choices=range(1, 5), type=int, help='Animation speed (1-4)')
sub.add_argument('rgb', metavar='RGB', nargs='?', type=auto_int, help='RGB values')
parser.add_argument('--config', help='Prints the current configuration', action='store_true')
parser.add_argument('--raw_config', help='Prints the current raw configuration', action='store_true')
args = parser.parse_args()

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
        update = True
        match args.cmd:
            case 'off':
                mor.effect = GloriousEffect.OFF
            case 'glorious':
                if args.direction is not None:
                    mor.glorious_direction = EffectDirection(args.direction)
                if args.speed is not None:
                    mor.glorious_speed = args.speed
                mor.effect = GloriousEffect.GLORIOUS
            case 'single':
                if args.rgb is not None:
                    mor.single_rgb = args.rgb
                if args.brightness is not None:
                    mor.single_rgb_brightness = args.brightness
                mor.effect = GloriousEffect.SINGLE_COLOUR
            case 'breath':
                if args.speed is not None:
                    mor.breath_speed = args.speed
                if args.rgb:
                    mor.breath_rgbs = args.rgb[:7]
                mor.effect = GloriousEffect.BREATHING
            case 'tail':
                if args.brightness is not None:
                    mor.tail_brightness = args.brightness
                if args.speed is not None:
                    mor.tail_speed = args.speed
                mor.effect = GloriousEffect.TAIL
            case 'seamless':
                if args.speed is not None:
                    mor.seamless_speed = args.speed
                mor.effect = GloriousEffect.SEAMLESS_BREATHING
            case 'six':
                if args.rgb and len(args.rgb) == 6:
                    mor.constant_rgbs = args.rgb
                mor.effect = GloriousEffect.CONSTANT_RGB
            case 'rave':
                if args.brightness is not None:
                    mor.rave_brightness = args.brightness
                if args.speed is not None:
                    mor.rave_speed = args.speed
                if args.rgb and len(args.rgb) == 2:
                    mor.rave_rgbs = args.rgb
                mor.effect = GloriousEffect.RAVE
            case 'random':
                if args.speed is not None:
                    mor.random_speed = args.speed
                mor.effect = GloriousEffect.RANDOM
            case 'wave':
                if args.brightness is not None:
                    mor.wave_brightness = args.brightness
                if args.speed is not None:
                    mor.wave_speed = args.speed
                mor.effect = GloriousEffect.WAVE
            case 'breath_mono':
                if args.speed is not None:
                    mor.single_breath_speed = args.speed
                if args.rgb:
                    mor.single_breath_rgb = args.rgb
                mor.effect = GloriousEffect.SINGLE_BREATHING
            case _:
                update = False
        if update:
            res = h.send_feature_report(mor.record)
            time.sleep(0.1)
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
