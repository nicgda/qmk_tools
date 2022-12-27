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

class kb_ids:
    def __init__(self, vid:int, pid:int, usage_page:int, usage_id:int):
        self.vid = vid
        self.pid = pid
        self.usage_page = usage_page
        self.usage_id = usage_id

# HID Nic's Commands
HNC_ON = b'\x01'
HNC_OFF = b'\x02'
HNC_SET = b'\x03'
HNC_GET = b'\x04'
HNC_SAVE = b'\x05'

keyboards_hid_ids = {
    # GMMK Pro rev1 ANSI
    'gmmk_pro':
        kb_ids(
            vid=0x320F,
            pid=0x5044,
            usage_page=0xFF60,
            usage_id=0x61
        ),
    # Idobao ID80v2
    'ID80v2':
        kb_ids(
            vid=0x6964,
            pid=0x0080,
            usage_page=0xFF60,
            usage_id=0x61
        ),
}

device_path = None

parser = argparse.ArgumentParser()
group_args = parser.add_mutually_exclusive_group(required=True)
group_args.add_argument('--on', help='Enable led notification', action='store_true')
group_args.add_argument('--off', help='Disable led notification', action='store_true')
group_args.add_argument('--get', help='Get current HSV values', action='store_true')
group_args.add_argument('--set', help='Set the HSV values', type=functools.partial(int, base=0), nargs=3)
group_args.add_argument('--save', help='Save current HSV values', action='store_true')
args = parser.parse_args()

for keys in keyboards_hid_ids.values():
    devices = hid.enumerate(keys.vid, keys.pid)
    if not len(devices):
        print('Device not present')
        continue
    for device in devices:
        # print(device)
        if (
            device['vendor_id'] == keys.vid
            and device['product_id'] == keys.pid
            and device['usage'] == keys.usage_id
            and device['usage_page'] == keys.usage_page
        ):
            device_path = device['path']
            break
    if device_path is not None:
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
