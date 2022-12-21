####
#
# https://github.com/Drugantibus/qmk-hid-rgb/blob/master/hid_rgb.py
# https://github.com/BlankSourceCode/qmk-hid-display/blob/master/index.js
#
#
#
import argparse
import functools

import hid


# HID Nic's Commands
HNC_ON = b'\x01'
HNC_OFF = b'\x02'
HNC_SET = b'\x03'
HNC_GET = b'\x04'
HNC_SAVE = b'\x05'

# GMMK Pro rev1 ANSI
vid = 0x320F
pid = 0x5044
usage_page = 0xFF60
usage_id = 0x61

device_path = None

parser = argparse.ArgumentParser()
group_args = parser.add_mutually_exclusive_group(required=True)
group_args.add_argument('--on', help='Enable led notification', action='store_true')
group_args.add_argument('--off', help='Disable led notification', action='store_true')
group_args.add_argument('--get', help='Get current HSV values', action='store_true')
group_args.add_argument('--set', help='Set the HSV values', type=functools.partial(int, base=0), nargs=3)
group_args.add_argument('--save', help='Save current HSV values', action='store_true')
args = parser.parse_args()

devices = hid.enumerate(vid, pid)
if not len(devices):
    print('Device not present')
    exit(0)
for device in devices:
    # print(device)
    if (
        device['vendor_id'] == vid
        and device['product_id'] == pid
        and device['usage'] == usage_id
        and device['usage_page'] == usage_page
    ):
        device_path = device['path']
        break
if device_path is None:
    print('Device not present')
    exit(0)

try:
    with hid.Device(path=device_path) as h:
        msg = b'NIC'
        if args.set is not None:
            msg += HNC_SET + bytes(args.set)
        elif args.on:
            msg += HNC_ON
        elif args.off:
            msg += HNC_OFF
        elif args.get:
            msg += HNC_GET
        elif args.save:
            msg += HNC_SAVE

        h.write(bytes(msg + b'\x00' * (64 - len(msg))))
        reply = h.read(64, 200)
        if args.set is not None:
            print(f'HSV : {reply[4]:02X} {reply[5]:02X} {reply[6]:02X}')
        print(f'reply: {reply.hex(sep=" ")}')
except hid.HIDException as err:
    print(f'Error: {err}')
