#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <stdbool.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>

int temp(void)
{
    FILE *in = fopen("NOVUS_REFDESIGN.bin", "rb");

    if (!in)
    {
        return -1;
    }

    FILE *out = fopen("out.bin", "wb");

    if (!out)
    {

        return -2;
    }

    uint8_t chunk[4096];

    size_t n = 1;
    size_t m = 0;
    while (n != 0)
    {

        n = fread(chunk, sizeof(chunk[0]), sizeof(chunk), in);

        m = fwrite(chunk, sizeof(chunk[0]), n, out);

        if (m != n)
        {
            fclose(in);
            fclose(out);
            return -3;
        }
    }

    perror("help me");
    fclose(in);
    fclose(out);

    return 0;
}