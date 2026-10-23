"""
PlatformIO post script for the paperdiy-companion env: upload CrossPoint into
ota_1 (0x650000) instead of ota_0, where the Companion firmware lives, and
leave otadata alone so the device keeps booting whichever slot it booted.

The platform derives the app offset from the ota_0 row of partitions.csv, and
FLASH_EXTRA_IMAGES includes boot_app0.bin, which resets otadata to ota_0.
"""

Import("env")  # noqa: F821  (provided by PlatformIO)

COMPANION_READER_SLOT = "0x650000"  # ota_1 in partitions.csv

env.Replace(ESP32_APP_OFFSET=COMPANION_READER_SLOT)  # noqa: F821
env.Replace(  # noqa: F821
    FLASH_EXTRA_IMAGES=[
        image
        for image in env.get("FLASH_EXTRA_IMAGES", [])  # noqa: F821
        if "boot_app0" not in str(image[1])
    ]
)

# The uploader flags already carry the extra images as offset/path pairs.
flags = []
for flag in env.get("UPLOADERFLAGS", []):  # noqa: F821
    if "boot_app0" in str(flag):
        flags.pop()  # its offset
    else:
        flags.append(flag)
env.Replace(UPLOADERFLAGS=flags)  # noqa: F821
