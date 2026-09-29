#!/usr/bin/env python3
"""Convert a Dreame fastboot `getvar config` value to the matching `oem dust` value.

The dust value expected by the FEL u-boot is derived from the config string
at runtime: the first 8 hex chars of the config are interpreted as a 32-bit
big-endian value and XORed with the constant 0xc9acbcc6 (the same seed used
to generate the flash-dump XOR table).

Example:
    config 7bb1387a791cc51a7c28de3e5951ed00  ->  dust b21d84bc
"""
import argparse
import sys

DUST_XOR_KEY = 0xc9acbcc6


def config_to_dust(config_hex: str) -> str:
    if len(config_hex) < 8:
        raise ValueError("config must be at least 8 hex chars")
    config_first4 = int(config_hex[:8], 16)
    dust_val = config_first4 ^ DUST_XOR_KEY
    return format(dust_val & 0xFFFFFFFF, "08x")


def dust_to_config_first4(dust_hex: str) -> str:
    if len(dust_hex) < 8:
        raise ValueError("dust must be at least 8 hex chars")
    dust_val = int(dust_hex[:8], 16)
    config_first4 = dust_val ^ DUST_XOR_KEY
    return format(config_first4 & 0xFFFFFFFF, "08x")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert between Dreame fastboot 'getvar config' values and "
                    "'oem dust' unlock values.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="examples:\n"
               "  %(prog)s 7bb1387a791cc51a7c28de3e5951ed00\n"
               "  %(prog)s --to-dust 7bb1387a791cc51a7c28de3e5951ed00\n"
               "  %(prog)s --to-config b21d84bc\n",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--to-dust", "-d", action="store_true",
                       help="convert config -> dust (default)")
    group.add_argument("--to-config", "-c", action="store_true",
                       help="convert dust -> first 8 chars of config")
    parser.add_argument("value",
                        help="config value (32 hex chars) or dust value (8 hex chars)")
    args = parser.parse_args()

    value = args.value.strip().lower()
    try:
        if args.to_config:
            print(dust_to_config_first4(value))
        else:
            print(config_to_dust(value))
    except ValueError as e:
        parser.error(str(e))
    return 0


if __name__ == "__main__":
    sys.exit(main())
