
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "ftd2xx.h"
#include "libft4222.h"
#include <stdbool.h>

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
    if (ftStatus != FT_OK)
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
        CLK_DIV_32,       // 60 MHz / 32 == 1.875 MHz
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

int main(int argc, char *argv[])
{

    if (argc < 3)
    {

        fprintf(stderr, "usage: %s <operation> <file>\n", argv[0]);
        return -1;
    }

    FILE *f;

    int read, write = 0;

    if (strncmp("read", argv[1], 4) == 0)
    {
        f = fopen(argv[2], "rb");
        read = 1;
    }
    else if (strncmp("write", argv[1], 5) == 0)
    {
        f = fopen(argv[2], "wb");
        write = 1;
    }
    else
    {
        printf("operation not supported\n");
        return -2;
    }

    if (!f)
    {
        printf("failed to open file\n");
        return -2;
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

    uint8_t chunk[4096];
    uint16_t sizeTransferred;

    FT4222_STATUS ftStatus;

    size_t n = 0;
    size_t m = 0;

    if (read == 1)
    {

        while (sizeTransferred != 0)
        {

            ftStatus = FT4222_SPIMaster_SingleRead(ftHandle, &chunk[0], sizeof(chunk), &sizeTransferred, true);

            if (ftStatus != FT_OK)
            {
                printf("FT4222_SPIMaster_SingleRead failed\n");
                break;
            }

            m = fwrite(chunk, sizeof(chunk[0]), sizeTransferred, f);

            if (m != sizeTransferred)
            {

                printf("fwrite failed\n");
                break;
            }
        }
    }

    if (write == 1)
    {

        while (n != 0)
        {
            n = fread(chunk, sizeof(chunk[0]), sizeof(chunk), f);

            ftStatus = FT4222_SPIMaster_SingleWrite(ftHandle, &chunk[0], sizeof(chunk), &sizeTransferred, true);

            if (n != sizeTransferred)
            {

                printf("fwrite failed\n");
                break;
            }

            if (ftStatus != FT_OK)
            {
                printf("FT4222_SPIMaster_SingleRead failed\n");
                break;
            }
        }
    }

    fclose(f);

    FT4222_UnInitialize(ftHandle);

    return 0;
}
