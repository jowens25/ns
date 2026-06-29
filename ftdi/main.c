
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "ftd2xx.h"
#include "libft4222.h"
#include <stdbool.h>
#include <unistd.h>

#include <gpiod.h>

#define SLAVE_SELECT(x) (1 << (x))

int getDeviceLocationId()
{
    FT_DEVICE_LIST_INFO_NODE *devInfo = NULL;
    DWORD numDevs = 0;

    FT_STATUS ftStatus = FT_CreateDeviceInfoList(&numDevs);

    if (ftStatus != FT_OK)
    {
        printf("FT_CreateDeviceInfoList failed (error code %d)\n", (int)ftStatus);
        return -1;
    }

    if (numDevs == 0)
    {
        printf("No devices connected.\n");
        return -2;
    }

    devInfo = calloc((size_t)1, sizeof(FT_DEVICE_LIST_INFO_NODE));

    if (devInfo == NULL)
    {
        printf("allocation failure.\n");
        return -3;
    }

    ftStatus = FT_GetDeviceInfoList(devInfo, &numDevs);
    if (ftStatus != FT_OK)
    {
        printf("FT_GetDeviceInfoList failed (error code %d)\n",
               (int)ftStatus);
        if (devInfo != NULL)
        {
            free(devInfo);
            devInfo = NULL;
        }
        return -4;
    }

    for (int i = 0; i < (int)numDevs; i++)
    {
        if (devInfo[i].Type == FT_DEVICE_4222H_3)
        {
            printf("\nDevice %d is FT4222H in mode 3 (single Master or Slave):\n", i);
            printf("0x%08x  %s  %s\n", (unsigned int)devInfo[i].ID, devInfo[i].SerialNumber, devInfo[i].Description);

            int deviceLocationId = devInfo->LocId;

            if (devInfo != NULL)
            {
                free(devInfo);
                devInfo = NULL;
            }

            return deviceLocationId;
        }
    }

    if (devInfo != NULL)
    {
        free(devInfo);
        devInfo = NULL;
    }

    return -1;
}

int configureDevice(int devLocId, FT_HANDLE *ftHandle)
{

    FT4222_Version ft4222Version;

    FT_STATUS ftStatus = FT_OpenEx((PVOID)(uintptr_t)devLocId,
                                   FT_OPEN_BY_LOCATION,
                                   ftHandle);
    if (ftStatus != FT4222_OK)
    {
        printf("FT_OpenEx failed (error %d)\n",
               (int)ftStatus);
        return -1;
    }

    FT4222_STATUS ft4222Status = FT4222_GetVersion(*ftHandle, &ft4222Version);
    if (FT4222_OK != ft4222Status)
    {
        printf("FT4222_GetVersion failed (error %d)\n",
               (int)ft4222Status);
        return -2;
    }

    printf("Chip version: %08X, LibFT4222 version: %08X\n",
           (unsigned int)ft4222Version.chipVersion,
           (unsigned int)ft4222Version.dllVersion);

    // Configure the FT4222 as an SPI Master.
    ft4222Status = FT4222_SPIMaster_Init(
        *ftHandle,
        SPI_IO_SINGLE,    // 1 channel
        CLK_DIV_8,        // 60 MHz / 32 == 1.875 MHz
        CLK_IDLE_LOW,     // clock idles at logic 0
        CLK_LEADING,      // data captured on rising edge
        SLAVE_SELECT(0)); // Use SS0O for slave-select
    if (FT4222_OK != ft4222Status)
    {
        printf("FT4222_SPIMaster_Init failed (error %d)\n",
               (int)ft4222Status);
        return -3;
    }

    ft4222Status = FT4222_SPI_SetDrivingStrength(*ftHandle,
                                                 DS_8MA,
                                                 DS_8MA,
                                                 DS_8MA);
    if (FT4222_OK != ft4222Status)
    {
        printf("FT4222_SPI_SetDrivingStrength failed (error %d)\n",
               (int)ft4222Status);
        return -4;
    }

    return 0;
}

#define BUFFER_SIZE 4096

uint8_t tx[BUFFER_SIZE] = {0};
uint8_t rx[BUFFER_SIZE] = {0};

// returns negative errors or number written
int spiReadWrite(FT_HANDLE ftHandle, uint8_t instruction, int32_t addr, uint8_t *data, uint16_t data_length, uint8_t header_length)
{

    memset(rx, 0, sizeof(rx));
    memset(tx, 0, sizeof(tx));
    uint16_t total_transfer_size = 0;

    tx[0] = instruction;

    total_transfer_size += 1;

    if (addr >= 0)
    {

        tx[1] = (addr >> 24) & 0xFF;
        tx[2] = (addr >> 16) & 0xFF;
        tx[3] = (addr >> 8) & 0xFF;
        tx[4] = addr & 0xFF;

        total_transfer_size += 4;
    }

    // writing...
    if (instruction == 0x12)
    {
        memcpy(tx + header_length, data, data_length);
    }

    total_transfer_size += data_length;

    if (total_transfer_size > sizeof(tx))
    {
        printf("the total transfer size is too big\n");
        return -1;
    }

    uint16_t n;

    FT4222_STATUS ftStatus = FT4222_SPIMaster_SingleReadWrite(ftHandle, rx, tx, total_transfer_size, &n, true);

    if (ftStatus != FT4222_OK)
    {
        printf("FT4222_SPIMaster_SingleReadWrite failed (error %d)\n", (int)ftStatus);
        return -1;
    }

    if (n != total_transfer_size)
    {
        printf("transfer failed\n");
        return -2;
    }

    if (data != 0)
    {

        memcpy(data, &rx[header_length], n - header_length);
    }

    return n - header_length;
}

void spiReadId(FT_HANDLE *ftHandle)
{

    uint8_t buf[8] = {0};

    int err = spiReadWrite(ftHandle, 0x9F, -1, buf, 8, 1);

    if (err < 0)
    {
        printf("err in spi read id: %d\n", err);
        return;
    }

    printf("ID bytes: %02X %02X %02X %02X %02X %02X %02X %02X\n",
           buf[0], buf[1], buf[2], buf[3], buf[4], buf[5], buf[6], buf[7]);
}

// returns register value...
uint8_t spiReadConfigurationRegister1(FT_HANDLE *ftHandle)
{

    uint8_t buf[1] = {0};
    spiReadWrite(ftHandle, 0x35, -1, buf, sizeof(buf), 1);

    if (buf[0] & (1 << 0))
    {
        printf("bit 0: Block protection and OTP locked\n");
    }
    else
    {
        printf("bit 0: Block protection and OTP un-locked\n");
    }

    if (buf[0] & (1 << 1))
    {
        printf("bit 1: Quad\n");
    }
    else
    {
        printf("bit 1: Dual or Serial\n");
    }

    if (buf[0] & (1 << 3))
    {
        printf("bit 3: Volatile\n");
    }
    else
    {
        printf("bit 4: Non-volatile\n");
    }

    if (buf[0] & (1 << 5))
    {
        printf("bit 5: BP starts at bottom (low addr)\n");
    }
    else
    {
        printf("bit 5: BP starts at top (high addr)\n");
    }

    printf("Bits 6-7: Latency Code: %d\n", (buf[0] >> 6) & 0x03);

    return buf[0];
}

int clearStatusRegister(FT_HANDLE *ftHandle)
{

    printf("clearing status reg...\n");
    return spiReadWrite(ftHandle, 0x30, -1, 0, 0, 1);
}

uint8_t spiReadStatusRegister1(FT_HANDLE *ftHandle)
{

    clearStatusRegister(ftHandle);

    uint8_t buf[1] = {0};
    spiReadWrite(ftHandle, 0x05, -1, buf, sizeof(buf), 1);

    if (buf[0] & (1 << 0))
    {
        printf("bit 0: Device Busy\n");
    }
    else
    {
        printf("bit 0: Ready Device\n");
    }

    if (buf[0] & (1 << 1))
    {
        printf("bit 1: Device accepts writes\n");
    }
    else
    {
        printf("bit 1: Device ignores writes\n");
    }

    if (buf[0] & (1 << 2))
    {
        printf("bit 2: BP0\n");
    }

    if (buf[0] & (1 << 3))
    {
        printf("bit 3: BP1\n");
    }

    if (buf[0] & (1 << 4))
    {
        printf("bit 4: BP2\n");
    }

    if (buf[0] & (1 << 5))
    {
        printf("bit 5: Erase error\n");
    }

    if (buf[0] & (1 << 6))
    {
        printf("bit 6: Programing error\n");
    }

    if (buf[0] & (1 << 7))
    {
        printf("bit 7: Locks state of SRWD, BP, and config reg bits\n");
    }
    else
    {
        printf("bit 7: no protection\n");
    }

    return buf[0];
}

int isWriteInProgress(FT_HANDLE *ftHandle)
{
    uint8_t buf[1] = {0};

    spiReadWrite(ftHandle, 0x05, -1, buf, 1, 1);

    printf("is write in progress buf: %d\n", buf[0]);

    if (buf[0] & (1 << 0))
    {
        printf("wip\n");
        return 1;
    }
    else
    {
        // printf("not wip\n");
        return 0;
    }
}

int isWriteEnableLatch(FT_HANDLE *ftHandle)
{
    uint8_t buf[1] = {0};

    spiReadWrite(ftHandle, 0x05, -1, buf, 1, 1);

    if (buf[0] & (1 << 1))
    {
        // printf("Device accepts write registers\n");
        return 1;
    }
    else
    {
        printf("Device ignores write registers\n");
        return 0;
    }
}

#define PAGE_SIZE 512

void spiWriteEnable(FT_HANDLE *ftHandle)
{

    spiReadWrite(ftHandle, 0x06, -1, 0, 0, 1);
}

int spi4PageProgram(FT_HANDLE *ftHandle, uint32_t addr, uint8_t *page)
{
    int wrote = 0;
    spiWriteEnable(ftHandle);

    int timeouts = 5000;
    do
    {
        if (isWriteEnableLatch(ftHandle))
        {
            break;
        }

        if (timeouts)
        {
            printf("timeouts: %d\n", timeouts);
            timeouts--;
        }

        usleep(1000);

    } while (timeouts > 0);

    wrote = spiReadWrite(ftHandle, 0x12, addr, page, PAGE_SIZE, 5);

    timeouts = 1000;
    do
    {

        if (!isWriteInProgress(ftHandle))
        {
            break;
        }
        if (timeouts)
        {
            printf("timeouts:%d\n", timeouts);
            timeouts--;
        }
        usleep(1000);
    } while (timeouts > 0);

    return wrote;
}

int spiWriteEnableWithTimeout(FT_HANDLE *ftHandle)
{
    spiWriteEnable(ftHandle);

    int timeouts = 5000;
    do
    {
        if (isWriteEnableLatch(ftHandle))
        {
            return 0;
        }

        if (timeouts)
        {
            printf("timeouts: %d\n", timeouts);
            timeouts--;
        }

        if (timeouts <= 0)
        {
            return -1;
        }

        usleep(1000);

    } while (timeouts > 0);

    return -1;
}

int waitForWriteInProgress(FT_HANDLE *ftHandle)
{
    int timeouts = 60; // 200s at 1ms poll interval — check your datasheet's max chip erase time
    while (isWriteInProgress(ftHandle) && timeouts > 0)
    {
        usleep(1000000);
        timeouts--;
    }

    if (timeouts <= 0)
    {
        printf("bulk erase timed out waiting for completion\n");
        return -2;
    }

    return 0;
}

int spiBulkErase(FT_HANDLE *ftHandle)
{

    if (spiWriteEnableWithTimeout(ftHandle) < 0)
    {

        printf("spi wrie enable with timeout failed\n");
        return -1;
    }

    spiReadWrite(ftHandle, 0xC7, -1, 0, 0, 1);

    waitForWriteInProgress(ftHandle);

    return 0;
}

int configureFlash(FT_HANDLE *ftHandle)
{

    // enable writing
    int res = spiWriteEnableWithTimeout(ftHandle);

    if (res != 0)
    {
        return -1;
    }

    int sr1 = spiReadStatusRegister1(ftHandle);
    int cr1 = spiReadConfigurationRegister1(ftHandle);

    cr1 &= ~(1 << 1); // should set to serial mode.

    uint8_t temp_data[2] = {0};
    temp_data[0] = sr1;
    temp_data[1] = cr1;

    // write register instruction
    spiReadWrite(ftHandle, 0x1, -1, temp_data, 2, 1);

    printf("======post cfg======\n");

    spiReadStatusRegister1(ftHandle);
    spiReadConfigurationRegister1(ftHandle);

    return 0;
}

int main(int argc, char *argv[])
{

    if (argc < 3)
    {

        fprintf(stderr, "usage: %s <operation> <file>\n", argv[0]);
        return -1;
    }

    FILE *f;

    int read = 0;
    int write = 0;
    int erase = 0;
    int id = 0;
    int cfg = 0;

    if (strncmp("read", argv[1], 4) == 0)
    {
        f = fopen(argv[2], "wb");
        read = 1;
    }
    else if (strncmp("write", argv[1], 5) == 0)
    {
        f = fopen(argv[2], "rb");
        write = 1;
    }
    else if (strncmp("erase", argv[1], 5) == 0)
    {
        erase = 1;
    }
    else if (strncmp("id", argv[1], 2) == 0)
    {
        id = 1;
    }
    else if (strncmp("cfg", argv[1], 3) == 0)
    {
        cfg = 1;
    }
    else
    {
        printf("operation not supported\n");
        return -2;
    }

    if (write == 1 || read == 1)
    {

        if (!f)
        {
            printf("failed to open file\n");
            return -2;
        }
    }

    int deviceLocationId = getDeviceLocationId();

    if (deviceLocationId <= 0)
    {
        perror("getDeviceLocationId failed");
        printf("err: %d", deviceLocationId);
        return -3;
    }

    FT_HANDLE ftHandle = (FT_HANDLE)NULL;

    int err = configureDevice(deviceLocationId, &ftHandle);

    if (err != 0)
    {
        perror("configureDevice failed");
        printf("err: %d", err);

        FT4222_UnInitialize(ftHandle);
        return -4;
    }

    if (id == 1)
    {
        spiReadId(ftHandle);
        spiReadConfigurationRegister1(ftHandle);
        spiReadStatusRegister1(ftHandle);
        return 0;
    }

    if (cfg == 1)
    {

        configureFlash(ftHandle);

        return 0;
    }

    if (read == 1)
    {

        spiReadId(ftHandle);
        spiReadConfigurationRegister1(ftHandle);
        spiReadStatusRegister1(ftHandle);

        uint8_t chunk[PAGE_SIZE] = {0};
        printf("reading from flash...\n");

        const uint32_t totalSize = 64u * 1024 * 1024;
        int addr = 0;
        int n = 0;
        while (addr < totalSize)
        {

            printf("Reading addr: %d\n", addr);

            n = spiReadWrite(ftHandle, 0x13, addr, chunk, PAGE_SIZE, 5);

            if (n <= 0)
            {
                break;
            }

            addr += n;

            fwrite(chunk, sizeof(chunk[0]), (size_t)n, f);
        }
    }

    if (write == 1)
    {

        uint8_t chunk[PAGE_SIZE] = {0};
        printf("writing to flash...\n");

        size_t n = -1;
        size_t m = -1;
        int addr = 0;
        while (n != 0)
        {

            n = fread(chunk, sizeof(chunk[0]), sizeof(chunk), f);

            printf("writing %ld bytes to addr: %08X\n", n, addr);

            m = spi4PageProgram(ftHandle, addr, chunk);

            if (m < 0)
            {
                printf("spi4pageProgram failed: %ld\n", m);
                break;
            }

            addr += m;
        }
    }

    if (erase == 1)
    {

        printf("sending bulk erase command...\n");

        spiBulkErase(ftHandle);
    }

    // fclose(f);
    FT4222_UnInitialize(ftHandle);
    FT_Close(ftHandle);

    return 0;
}
