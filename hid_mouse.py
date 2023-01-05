####
#
# https://github.com/...
# https://rustrepo.com/repo/sammko-gloryctl-rust-utilities
#
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
    # print(f'usage_page: {device["usage_page"]:04X}, usage: {device["usage"]:02X}, interface: {device["interface_number"]}')
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
        print(f'mor: {mor.effect}')
        # ba_config = bytearray(config)
        # print(f'46: {ba_config[0x35]:02X}')
        update = False
        if args.on:
            if mor.effect != GloriousEffect.GLORIOUS:
                mor.effect = GloriousEffect.GLORIOUS
                update = True
        elif args.off:
            if mor.effect != GloriousEffect.OFF:
                mor.effect = GloriousEffect.OFF
                update = True
        # print(f'config: {config.hex(sep=" ")}')
        if update:
            res = h.send_feature_report(mor.record)
        # print(f'req res: {res}')
except hid.HIDException as err:
    print(f'Error: {err}')
