/* Minimal FT4222H SPI MASTER test against an S25FL512S.
 *
 * Goal: manually issue SPI commands to determine whether the chip is in
 * 3-byte or 4-byte addressing mode, and whether the "Enter 4-Byte Address
 * Mode" command (0xB7) lets us successfully read data back.
 *
 * This is diagnostic only -- it does NOT erase or write anything.
 *
 * Build (Linux):
 *   gcc spi_probe.c -lft4222 -Wl,-rpath,/usr/local/lib -o spi_probe
 * Run:
 *   sudo ./spi_probe
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include "ftd2xx.h"
#include "libft4222.h"

/* SPI Master can assert SS0O in single mode; SS0O..SS3O in quad mode. */
#define SLAVE_SELECT(x) (1 << (x))

static void hexdump(const char *label, uint8 *buf, int len)
{
    printf("%s (%d bytes): ", label, len);
    for (int i = 0; i < len; i++)
        printf("%02x ", buf[i]);
    printf("\n");
}

/* Issue a single SPI transaction: write `wlen` bytes from wbuf, then read
 * `rlen` bytes into rbuf, all under one CS assertion. Uses
 * FT4222_SPIMaster_SingleReadWrite so write and read share the same
 * transfer (CS stays low across both phases). */
static int spi_txn(FT_HANDLE h, uint8 *wbuf, uint16 wlen, uint8 *rbuf, uint16 rlen)
{
    FT4222_STATUS st;
    uint16 sizeTransferred = 0;

    /* Build combined buffer: command/address bytes followed by dummy
     * bytes for the read phase (FT4222 single-read-write clocks out
     * wbuf and simultaneously clocks in the same number of bytes; we
     * pad with zeros for the read portion). */
    uint16 total = wlen + rlen;
    uint8 *outbuf = calloc(total, 1);
    uint8 *inbuf = calloc(total, 1);
    memcpy(outbuf, wbuf, wlen);

    st = FT4222_SPIMaster_SingleReadWrite(h, inbuf, outbuf, total,
                                          &sizeTransferred, TRUE /* isEndTransaction */);
    if (st != FT4222_OK)
    {
        printf("FT4222_SPIMaster_SingleReadWrite failed (error %d)\n", (int)st);
        free(outbuf);
        free(inbuf);
        return -1;
    }

    if (rlen > 0 && rbuf != NULL)
        memcpy(rbuf, inbuf + wlen, rlen);
    free(outbuf);
    free(inbuf);
    return 0;
}

int main(void)
{
    FT_STATUS ftStatus;
    FT_HANDLE ftHandle = (FT_HANDLE)NULL;
    FT4222_STATUS ft4222Status;
    FT_DEVICE_LIST_INFO_NODE *devInfo = NULL;
    DWORD numDevs = 0;
    int i;
    int found = 0;
    uint8 rdid_cmd[1] = {0x9F};
    uint8 rdid_resp[3] = {0};
    uint8 read3_cmd[4] = {0x03, 0x00, 0x00, 0x00};
    uint8 read4_cmd[5] = {0x13, 0x00, 0x00, 0x00, 0x00};
    uint8 en4ba_cmd[1] = {0xB7};
    uint8 rdsr_cmd[1] = {0x05};
    uint8 rdsr_resp[1] = {0};
    uint8 readback[16];

    ftStatus = FT_CreateDeviceInfoList(&numDevs);
    if (ftStatus != FT_OK || numDevs == 0)
    {
        printf("No FTDI devices found (status %d, numDevs %u)\n",
               (int)ftStatus, (unsigned)numDevs);
        return 1;
    }
    printf("Found %u FTDI device(s)\n", (unsigned)numDevs);

    devInfo = calloc((size_t)numDevs, sizeof(FT_DEVICE_LIST_INFO_NODE));
    if (devInfo == NULL)
    {
        printf("Allocation failure.\n");
        return 1;
    }

    ftStatus = FT_GetDeviceInfoList(devInfo, &numDevs);
    if (ftStatus != FT_OK)
    {
        printf("FT_GetDeviceInfoList failed (error %d)\n", (int)ftStatus);
        free(devInfo);
        return 1;
    }

    /* Same enumeration pattern as FTDI's spis.c/spim.c examples: find
     * the FT4222H "mode 3" interface (single Master/Slave) and open it
     * by location ID. If your board's FT4222 is in a different mode
     * (0, 1, or 2), this won't match -- tell me and we'll adjust. */
    for (i = 0; i < (int)numDevs; i++)
    {
        if (devInfo[i].Type == FT_DEVICE_4222H_3)
        {
            printf("Device %d is FT4222H mode 3: 0x%08x %s %s\n", i,
                   (unsigned int)devInfo[i].ID,
                   devInfo[i].SerialNumber,
                   devInfo[i].Description);
            ftStatus = FT_OpenEx((PVOID)(uintptr_t)devInfo[i].LocId,
                                 FT_OPEN_BY_LOCATION, &ftHandle);
            found = 1;
            break;
        }
    }

    if (!found)
    {
        printf("No FT4222H mode-3 device found. Devices seen:\n");
        for (i = 0; i < (int)numDevs; i++)
            printf("  [%d] Type=%d Desc=%s\n", i, devInfo[i].Type, devInfo[i].Description);
        free(devInfo);
        return 1;
    }
    free(devInfo);

    if (ftStatus != FT_OK)
    {
        printf("FT_OpenEx failed (error %d)\n", (int)ftStatus);
        return 1;
    }

    ft4222Status = FT4222_SPIMaster_Init(ftHandle,
                                         SPI_IO_SINGLE,
                                         CLK_DIV_32, /* 60MHz / 32 ~= 1.875MHz -- conservative, matches FTDI's own example */
                                         CLK_IDLE_LOW,
                                         CLK_LEADING,
                                         SLAVE_SELECT(0));
    if (ft4222Status != FT4222_OK)
    {
        printf("FT4222_SPIMaster_Init failed (error %d)\n", (int)ft4222Status);
        goto exit;
    }

    ft4222Status = FT4222_SPI_SetDrivingStrength(ftHandle, DS_8MA, DS_8MA, DS_8MA);
    if (ft4222Status != FT4222_OK)
    {
        printf("FT4222_SPI_SetDrivingStrength failed (error %d)\n", (int)ft4222Status);
        goto exit;
    }

    printf("\n--- Step 1: RDID (0x9F) sanity check ---\n");
    if (spi_txn(ftHandle, rdid_cmd, 1, rdid_resp, 3) == 0)
        hexdump("RDID response", rdid_resp, 3);
    /* Expect something like 01 02 20 for S25FL512S (Spansion/Cypress mfg ID 0x01,
     * memory type 0x02, capacity 0x20). If this comes back all 0x00 or 0xFF,
     * basic SPI wiring/timing is suspect before we even get to addressing mode. */

    printf("\n--- Step 2: Read Status Register (0x05) ---\n");
    if (spi_txn(ftHandle, rdsr_cmd, 1, rdsr_resp, 1) == 0)
        hexdump("Status register", rdsr_resp, 1);

    printf("\n--- Step 3: Plain 3-byte READ (0x03) at address 0x000000 ---\n");
    memset(readback, 0, sizeof(readback));
    if (spi_txn(ftHandle, read3_cmd, 4, readback, sizeof(readback)) == 0)
        hexdump("3-byte READ data", readback, sizeof(readback));

    printf("\n--- Step 4: Enter 4-Byte Address Mode (0xB7) ---\n");
    if (spi_txn(ftHandle, en4ba_cmd, 1, NULL, 0) == 0)
        printf("Sent 0xB7 (no response expected)\n");

    printf("\n--- Step 5: Read Status Register again after 0xB7 ---\n");
    if (spi_txn(ftHandle, rdsr_cmd, 1, rdsr_resp, 1) == 0)
        hexdump("Status register", rdsr_resp, 1);

    printf("\n--- Step 6: 4-byte READ (0x13) at address 0x00000000 ---\n");
    memset(readback, 0, sizeof(readback));
    if (spi_txn(ftHandle, read4_cmd, 5, readback, sizeof(readback)) == 0)
        hexdump("4-byte READ data", readback, sizeof(readback));

    printf("\nDone. Compare Step 3 vs Step 6 output.\n");
    printf("If Step 1/2 return garbage (all 00 or all FF), the issue is\n");
    printf("electrical/timing, not addressing mode -- try lowering CLK_DIV\n");
    printf("(use CLK_DIV_16 or CLK_DIV_32 for a slower, more conservative clock).\n");

exit:
    if (ftHandle != (FT_HANDLE)NULL)
    {
        FT4222_UnInitialize(ftHandle);
        FT_Close(ftHandle);
    }
    return 0;
}