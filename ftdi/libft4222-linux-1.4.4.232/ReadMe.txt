
libft4222 for Linux
-------------------

FTDI's libft4222 allows access to, and control of, the FT4222H. 
Depending on configuration, the FT4222H presents 1, 2 or 4 interfaces 
for I2C, SPI and GPIO functions. Please search ftdichip.com for the 
FT4222H data sheet, and Application Note AN_329 which describes the 
libft4222 API. 

The Linux version of libft4222 includes (statically links to) FTDI's 
libftd2xx which itself includes an unmodified version of libusb 
(http://libusb.info) which is distributed under the terms of the GNU 
Lesser General Public License (see http://www.gnu.org/licenses). Sources 
for libusb, plus re-linkable object files are included in the libftd2xx 
distribution, available from ftdichip.com. 


Installing
----------

1.  tar xfvz libft4222-1.4.4.232.tgz

This unpacks the archive, creating the following directory structure:

    build-x86_32
    build-x86_64
    build-arm-v6-hf
    build-arm-v7-hf
    build-arm-v7-sf
    build-arm-v7-hf-uclibc
    build-arm-v8
    libft4222-linux-1.4.4.221 for mips (base on libftd2xx v1.4.27)
    examples
    libft4222.h
    ftd2xx.h
    WinTypes.h
    install4222.sh

2.  sudo ./install4222.sh

for dynamic library
This copies the library (libft4222.so.1.4.4.232) and headers to 
/usr/local/lib and /usr/local/include respectively.  Also it creates a 
version-independent symbolic link, libft4222.so. 

for static library
This copies the library (libft4222.a) and headers to 
/usr/local/lib and /usr/local/include respectively.

Alternatively, you may manually copy the library and headers to a
custom location.




Building
--------

1.  cd examples

2.  build an excutable file

for dynamic library
sudo cc get-version.c -lft4222 -Wl,-rpath,/usr/local/lib

for static library
sudo cc -static get-version.c -lft4222 -Wl,-rpath,/usr/local/lib -ldl -lpthread -lrt -lstdc++

if you ld version is too old, building with static library may encounter error
you can run the following instruction to resolve it.
sudo apt-get update
sudo apt-get install binutils-2.26
export PATH="/usr/lib/binutils-2.26/bin:$PATH"

With an FT4222H device connected to a USB port, try:

3.  sudo ./a.out

You should see a message similar to this:

    Chip version: 42220400, LibFT4222 version: 010404E8
    
If you see a message such as "No devices connected" or "No FT4222H detected",
this may indicate that: 

    a.  There is no FT4222H connected.  Check by running 'lsusb', which 
        should output something similar to:

        Bus 001 Device 005: ID 0403:601c Future Technology Devices International, Ltd

    b.  Your program did not run with sufficient privileges to access USB.
        Use 'sudo', or 'su', or run as root.

If you see an error message about libft4222.so having an invalid ABI, please
try to upgrade glibc to version 2.10 or above.

If you enable the SPI feature, please check the SS pin first. The SS pin must be tied to high when SPI master mode is enabled.

Since libft4222-linux-1.4.4.232, we have stopped the advancement of libft4222 for MIPS platform. This package included the old MIPS libraries version 1.4.4.221. The new MIPS library is developed based on customer requirements. If you would like to upgrade the LibFT4222 MIPS library, please contact FTDI.

Release Notes
-------------


1.4.4.232
    To be consistent with libftd2xx, stop advancement for MIPS platform.
    Fixed the issue that isEndTransaction does not work when SPI Master single mode and the transfer size is a multiple of 512. (For the MIPS series, this issue can workaround by avoiding calls to FT4222_SPIMaster_SingleReadWrite / FT4222_SPIMaster_SingleRead / FT4222_SPIMaster_SingleWrite with data sizes that are multiples of 512 bytes.)
    Supported platforms : x86_32/x86_64/arm-v6-hf/arm-v7-hf/arm-v7-sf/arm-v7-hf-uclibc/arm-v8

1.4.4.221
    Add big-endian support
    Enable position-independent code
    Supported platforms : x86_32/x86_64/arm-v6-hf/arm-v7-hf/arm-v7-sf/arm-v8/mips-eglibc-hf/mips-eglibc-sf/mips-el-uclibc-hf/mips-openwrt-uclibc

1.4.4.188
    Add i386 support
    Add API FT4222_GetChipMode   

1.4.4.170
    support static library.
    now libft4222 supports all D2xx supported platform.
    supported platforms : x86_64/arm-v6-hf/arm-v7-hf/arm-v7-sf/arm-v8/mips-eglibc-hf/mips-eglibc-sf/mips-el-eglibc-hf/mips-el-uclibc-hf/mips-openwrt-uclibc

1.4.4.44
    Fix issue. Frequency 100K~400K in I2C Master is not accurate.
    Add Feature. Add API FT4222_I2CMaster_ResetBus. This function can reset i2c bus when it is abnormal.
    Add Feature. Add API FT4222_SPIMaster_SetCS. It can determine the CS is high or low when SPI bus is active. The default value is active-low.
    Remove Feature. Remove API FT4222_SPISlave_RxQuickResponse. It may cause data lost sometimes.
    Add Feature. Add license announce in libft4222.h

1.4.4.9
    Add i486 and Arm-V7-A83T support.
    Fix potential FT4222_I2CMaster_Read and FT4222_I2CMaster_ReadEx data lost.
    Fix issue. FT4222_I2CMaster_WriteEx does not return correct sizeTransferred.
    Fix issue. FT4222_SPIMaster_MultiReadWrite does not return correct sizeOfRead when multiReadBytes equal to zero

1.4.2.184
    New API gives SPI Slave protocol options.
    Fixed potential SPI Slave data loss.
    Fixed potential GPIO read error.
    Fixed potential SPISlave_GetMaxTransferSize error.
    Fixed potential inability for GPIO_Read to get interrupt status.

1.2.1.4
    Added Linux support, extended I2C Master API.
    Added portable C examples.

1.1.0.0
    Added 64-bit Windows support.

1.0.0.0
    Initial version.  Windows only.
