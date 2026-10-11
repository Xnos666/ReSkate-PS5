#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <stdio.h>

static DWORD WINAPI worker(void *context) {
    SetEvent((HANDLE)context);
    return 37;
}

int main(void) {
    FILE *log = fopen("C:\\loader-probe.txt", "w");
    if (!log) return 11;
    setvbuf(log, NULL, _IONBF, 0);
    fprintf(log, "RESKATE_PS5_LOADER_PROBE entry reached\n");
    char value[1024];
    GetEnvironmentVariableA("USERPROFILE", value, sizeof(value));
    fprintf(log, "USERPROFILE=%s\n", value);
    GetEnvironmentVariableA("LOCALAPPDATA", value, sizeof(value));
    fprintf(log, "LOCALAPPDATA=%s\n", value);
    GetModuleFileNameA(GetModuleHandleA("kernel32.dll"), value, sizeof(value));
    fprintf(log, "kernel32=%s\n", value);
    HANDLE event = CreateEventA(NULL, TRUE, FALSE, NULL);
    HANDLE thread = CreateThread(NULL, 0, worker, event, 0, NULL);
    DWORD wait = WaitForSingleObject(event, 5000), result = 0;
    if (thread) {
        WaitForSingleObject(thread, 5000);
        GetExitCodeThread(thread, &result);
        CloseHandle(thread);
    }
    CloseHandle(event);
    fprintf(log, "worker wait=%lu exit=%lu\n", wait, result);
    fprintf(log, "RESULT=%s\n", wait == WAIT_OBJECT_0 && result == 37 ? "PASS" : "FAIL");
    fclose(log);
    return wait == WAIT_OBJECT_0 && result == 37 ? 0 : 12;
}
