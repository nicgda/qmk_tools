"""
Little tool to change the led effect on the Glorious Model O mouse.

This is very incomplete since I personally don't need the other
commands... yet.

Many thanks to Samuel Čavoj for doing the reverse engineering job
and sharing it at https://rustrepo.com/repo/sammko-gloryctl-rust-utilities

This code used the hid package, using the hidapi library.

On macOS, hidapi is available through brew.
"""
import argparse

import hid

from hid_glorious import (GloriousEffect,
                          GloriousModelORecord,
                          model_O_ids)

device_path = None

parser = argparse.ArgumentParser()
group_args = parser.add_mutually_exclusive_group(required=True)
group_args.add_argument('--on', help='Enable led notification', action='store_true')
group_args.add_argument('--off', help='Disable led notification', action='store_true')
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
        print(f'req res: {res}')
        config = h.get_feature_report(0x04, 520)
        print(f'config: {config.hex(sep=" ")}')
        mor = GloriousModelORecord(config)
        print(f'mor: {mor}')
        update = False
        if args.on:
            if mor.effect != GloriousEffect.SINGLE_COLOUR:
                mor.effect = GloriousEffect.SINGLE_COLOUR
                mor.single_rgb = 0x330066
                update = True
        elif args.off:
            if mor.effect != GloriousEffect.OFF:
                mor.effect = GloriousEffect.OFF
                update = True
        if update:
            res = h.send_feature_report(mor.record)
except hid.HIDException as err:
    print(f'Error: {err}')
