
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "ftd2xx.h"
#include "libft4222.h"
#include <stdbool.h>

#define SLAVE_SELECT(x) (1 << (x))

int main(void)
{

    FT_STATUS ftStatus;
    FT_DEVICE_LIST_INFO_NODE *devInfo = NULL;
    DWORD numDevs = 0;

    int err = 0;

    ftStatus = FT_CreateDeviceInfoList(&numDevs);

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

    devInfo = calloc((size_t)numDevs, sizeof(FT_DEVICE_LIST_INFO_NODE));

    if (devInfo == NULL)
    {
        printf("allocation failure.\n");
        return -3;
    }

    // =======================

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

            FT_HANDLE ftHandle = (FT_HANDLE)NULL;

            // int success = 0;
            FT_STATUS ftStatus;
            FT4222_STATUS ft4222Status;
            FT4222_Version ft4222Version;
            // uint8 address;

            ftStatus = FT_OpenEx((PVOID)(uintptr_t)devInfo->LocId,
                                 FT_OPEN_BY_LOCATION,
                                 &ftHandle);
            if (ftStatus != FT_OK)
            {
                printf("FT_OpenEx failed (error %d)\n",
                       (int)ftStatus);
                return -1;
            }

            ft4222Status = FT4222_GetVersion(ftHandle,
                                             &ft4222Version);
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
                ftHandle,
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

            ft4222Status = FT4222_SPI_SetDrivingStrength(ftHandle,
                                                         DS_8MA,
                                                         DS_8MA,
                                                         DS_8MA);
            if (FT4222_OK != ft4222Status)
            {
                printf("FT4222_SPI_SetDrivingStrength failed (error %d)\n",
                       (int)ft4222Status);
                return -4;
            }

            if (err != 0)
            {

                if (devInfo != NULL)
                {
                    free(devInfo);
                    devInfo = NULL;
                }

                if (ftHandle != NULL)
                {
                    FT4222_UnInitialize(ftHandle);
                }

                return err;
            }

            for (int j = 0; j < 100; j++)
            {

                uint8_t recvData[64000];
                uint16_t sizeTransferred;

                ftStatus = FT4222_SPIMaster_SingleRead(ftHandle, &recvData[0], 64000, &sizeTransferred, true);

                if (ftStatus != FT_OK)
                {

                    if (devInfo != NULL)
                    {
                        free(devInfo);
                        devInfo = NULL;
                    }

                    if (ftHandle != NULL)
                    {
                        FT4222_UnInitialize(ftHandle);
                    }

                    return -5;
                }

                for (int i = j * 64000; i < (j + 1) * 64000; i++)
                {

                    if (recvData[i] != 255)
                    {
                        printf(" %d ", recvData[i]);
                    }

                    if (i % 8 == 0)
                    {
                        printf("\n");
                    }
                }
            }

            break;
        }
    }

    if (devInfo != NULL)
    {
        free(devInfo);
        devInfo = NULL;
    }

    return err;
}
