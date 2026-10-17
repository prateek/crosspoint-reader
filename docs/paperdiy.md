# M5Stack PaperDIY bring-up

Status: experimental board support. No physical PaperDIY has been tested. Build and native-simulator checks cannot establish electrical compatibility, usable refresh waveforms, battery accuracy, or sleep current. Do not treat this as an official CrossPoint release.

## Build

Use the `feat/paperdiy` firmware checkout and its matching modified FreeInk SDK checkout. The SDK changes must be retained: the upstream pinned SDK does not contain this profile yet.

```sh
pio run -e paperdiy
sh freeink-sdk/libs/hardware/InputManager/test/host/run_paperdiy.sh
```

The environment uses ESP32-S3 N16R8, 16 MB flash, 8 MB OPI PSRAM, the existing OTA partition layout, and a pinned M5GFX revision. Outputs are under `.pio/build/paperdiy/`: `firmware.bin` is the application image and `firmware.factory.bin` includes bootloader and partitions. Back up the factory installation before flashing. Use only this board target; PaperS3 and PaperMono binaries have different power and input wiring.

The firmware carries the `paperdiy` board tag. OTA looks for an explicitly named PaperDIY asset and rejects other board tags. Upstream does not yet publish that asset; there is no release-workflow change in this port.

## Controls and hardware ownership

FreeInk owns the board profile, parallel display configuration, PMIC access and button interpretation. CrossPoint's HAL owns shutdown and its existing wake policy. The firmware adds no direct BookOrbit client.

- Button A (GPIO4): tap Up/previous page; hold Back.
- Button B (GPIO3): tap Down/next page; hold Confirm/menu.
- Hold both buttons: logical Power. The existing two-button hold threshold applies.
- PMIC power-button click: the configured short Power action; default Ignore acts as shutdown for this board. Hardware long-hold download recovery remains enabled; the existing double-click power-off configuration is preserved.
- Shutdown asks M5PM1 to cut power. If it returns with USB still supplying power, firmware disables the display supply and sleeps with either navigation key as a wake source. It waits for held keys to be released first.

The display is a 960x540 ED047TC1 parallel panel. M5PM1 on SDA41/SCL42 enables its supply through PYG2; M5GFX sequences the GPIO-controlled boost and display signals. The facade framebuffer uses PSRAM (64,800 bytes for one 1-bit plane); M5GFX and grayscale rendering have additional buffers. The native simulator's reported free memory is synthetic and is not a device memory measurement.

SD uses SPI on SCLK39, MISO40, MOSI38, CS47. Card-detect GPIO48 is not consumed by this profile. Charging reads M5PM1 PYG3, active low; external supply presence is read separately so full charge does not mean USB was unplugged. Battery percentage uses the SDK's voltage estimate, not a calibrated state-of-charge gauge. There is no touch, frontlight, RTC, speaker, or microphone in this profile.

## Validation layers

The SDK host test executes the real InputManager against controlled GPIO/I2C responses. It checks profile flags and pins, retry after PMIC failure, rail switching, button events and read-clear power clicks. The desktop simulator exercises application rendering, host files and network protocols; it substitutes the hardware HAL and does not run the parallel display or PMIC driver.

Use the matching simulator checkout for `simulator_paperdiy`. Its native 960x540 profile exposes logical keyboard events, while the SDK host test covers the two physical buttons. Keep the simulator alongside this checkout and use its macOS or Linux sample configuration with `simulator=symlink://../crosspoint-simulator`; the pre-build content-protection script must also reference that checkout when using a symlink dependency. Per-run results and screenshots belong in the review artifacts rather than this guide.

BookOrbit integration follows upstream CrossPoint's CrossPoint Sync protocol. Configure CrossPoint Sync as the reader's sync server, enable metadata sending for title/author matching, and link BookOrbit in CrossPoint Sync. Use the same EPUB edition on both sides for exact position conversion. The server connector owns BookOrbit credentials and XPath/CFI conversion. Keep this integration separate from the board port when proposing upstream changes.

## Physical acceptance when the kit arrives

1. Back up factory flash, then flash the PaperDIY target over USB. Confirm serial logs identify `paperdiy`, PSRAM initializes, and the SD card mounts. A black screen, reset loop, or PMIC error is a failed bring-up.
2. Open a known EPUB. Verify panel orientation, all four reading orientations, page turns, menu navigation and long-press actions. Check grayscale images, clipping at edges and repeated full/partial refreshes. Record ghosting or inverted panels; simulator images cannot validate these.
3. Verify power-button click, both-key hold, hardware double-click off, and long-hold recovery. Test shutdown and restart on battery and USB, including navigation-key wake on USB. Confirm the device is not stranded asleep or immediately rebooting.
4. Check charging and USB indicators with the cable inserted/removed and at full charge. Measure sleep and shutdown current on the assembled kit before claiming acceptable battery life.
5. Transfer an EPUB, read and save progress, reboot and resume, then sync to an isolated CrossPoint Sync/BookOrbit account in both directions. Check the displayed text location, not just the percentage. Repeat with Wi-Fi loss and a retry; confirm local progress remains intact.

Hardware acceptance is required before proposing a public upstream PR. The human owner must also accept the two-button interaction and PMIC shutdown/USB wake behavior.

## Hardware sources

- [M5Stack PaperDIY Assembly Kit](https://docs.m5stack.com/en/core/PaperDIY_Assembly_Kit)
- [M5GFX board detection and parallel pin configuration](https://github.com/m5stack/M5GFX/blob/347a23274081a105cb9fc0fc3bbf0e15c78e79c3/src/M5GFX.cpp)
- [M5Unified power implementation](https://github.com/m5stack/M5Unified/blob/master/src/utility/Power_Class.inl)
- [M5PM1 register implementation](https://github.com/m5stack/M5Unified/blob/master/src/utility/power/M5PM1_Class.inl)
