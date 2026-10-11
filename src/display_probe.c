#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <stdio.h>
int main(void) {
    FILE *log=fopen("C:\\display-probe.txt","w");if(!log)return 1;
    DEVMODEW mode={.dmSize=sizeof(mode)};
    for(DWORD i=0;i<300&&EnumDisplaySettingsW(NULL,i,&mode);i++)
        fprintf(log,"%lu %lu %lu %lu %lu\n",i,mode.dmPelsWidth,mode.dmPelsHeight,mode.dmBitsPerPel,mode.dmDisplayFrequency);
    fclose(log);return 0;
}
