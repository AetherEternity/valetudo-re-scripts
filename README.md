# Dreame Gen3 FEL u-boot tools

Tools for working with the custom fastboot u-boot used in the Dreame Gen3 robot rooting method (L10s Ultra / D10s / X40 and other MR813-based models, see dontvacuum.me). 
## Tools

### decrypt.py — decrypt/encrypt flash dumps

The FEL u-boot's `fastboot get_staged` command dumps flash to `dustx100.bin`, `dustx101.bin`, `dustx102.bin` files. The data is obfuscated with a XOR keystream generated at u-boot init:

1. MD5 of the constant seed `0xc9acbcc6` seeds a 0x20000-byte table
2. The table is extended by an iterated MD5 chain (MD5 over the whole table, result appended, repeated)
3. Data is XORed in 0x200-byte rows: row `n` of the dump is XORed with table row `n & 0xff`

Since XOR is symmetric, the same routine decrypts and encrypts.

```bash
# decrypt a set of dump files into one flash image
python3 decrypt.py dustx100.bin dustx101.bin dustx102.bin
# -> flash_dump_decrypted.bin

# decrypt all dustx1xx.bin files found in a directory
python3 decrypt.py /path/to/dumps/

# encrypt a flash image again and split into dustx1xx parts
python3 decrypt.py --encrypt flash_dump_decrypted.bin
```

### dust_from_config.py — config value to dust value

The FEL u-boot gates `fastboot oem prep` behind an `oem dust <value>` check. The expected value is derived at runtime from the 32-char hex string returned by `fastboot getvar config`:

```
dust = (first 8 hex chars of config as u32) XOR 0xc9acbcc6
```

`0xc9acbcc6` is the same constant that seeds the dump XOR table.

```bash
python3 dust_from_config.py 7bb1387a791cc51a7c28de3e5951ed00
# b21d84bc

python3 dust_from_config.py --help
```
