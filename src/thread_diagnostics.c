#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <tlhelp32.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>

typedef struct { uintptr_t base; DWORD size; char name[MAX_PATH]; } Module;
static Module modules[256];
static unsigned module_count;
static void describe(FILE *out, const char *label, uintptr_t address) {
    for (unsigned i=0;i<module_count;i++) {
        if(address>=modules[i].base && address-modules[i].base<modules[i].size) {
            fprintf(out,"%s %s+0x%llx (%llx)\n",label,modules[i].name,
                (unsigned long long)(address-modules[i].base),(unsigned long long)address);
            return;
        }
    }
    if(label[0]!='s')fprintf(out,"%s 0x%llx\n",label,(unsigned long long)address);
}
static void snapshot(FILE *out) {
    HANDLE snap=CreateToolhelp32Snapshot(TH32CS_SNAPMODULE,GetCurrentProcessId());
    MODULEENTRY32 m={.dwSize=sizeof(m)};module_count=0;
    if(snap!=INVALID_HANDLE_VALUE) {
        for(BOOL ok=Module32First(snap,&m);ok&&module_count<256;ok=Module32Next(snap,&m)) {
            Module *dest=&modules[module_count++];dest->base=(uintptr_t)m.modBaseAddr;dest->size=m.modBaseSize;
            snprintf(dest->name,sizeof(dest->name),"%s",m.szModule);
        }
        CloseHandle(snap);
    }
    fprintf(out,"SNAPSHOT tick=%llu modules=%u\n",GetTickCount64(),module_count);fflush(out);
    snap=CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD,0);
    THREADENTRY32 t={.dwSize=sizeof(t)};
    if(snap==INVALID_HANDLE_VALUE){fprintf(out,"snapshot failed %lu\n",GetLastError());return;}
    for(BOOL ok=Thread32First(snap,&t);ok;ok=Thread32Next(snap,&t)) {
        if(t.th32OwnerProcessID!=GetCurrentProcessId()||t.th32ThreadID==GetCurrentThreadId())continue;
        HANDLE thread=OpenThread(THREAD_SUSPEND_RESUME|THREAD_GET_CONTEXT|THREAD_QUERY_INFORMATION,FALSE,t.th32ThreadID);
        if(!thread){fprintf(out,"thread %lu open failed %lu\n",t.th32ThreadID,GetLastError());continue;}
        CONTEXT ctx={.ContextFlags=CONTEXT_FULL};uintptr_t stack[256];SIZE_T bytes=0;
        FILETIME create,exit,kernel,user;BOOL times=GetThreadTimes(thread,&create,&exit,&kernel,&user);
        BOOL got=FALSE;DWORD suspended=SuspendThread(thread);
        if(suspended!=(DWORD)-1) {
            got=GetThreadContext(thread,&ctx);
            if(got)ReadProcessMemory(GetCurrentProcess(),(void*)ctx.Rsp,stack,sizeof(stack),&bytes);
            ResumeThread(thread);
        }
        CloseHandle(thread);
        fprintf(out,"THREAD %lu (0x%lx) captured=%d stack=%llu kernel=%llu user=%llu\n",t.th32ThreadID,t.th32ThreadID,got,(unsigned long long)bytes,
            times?((unsigned long long)kernel.dwHighDateTime<<32)|kernel.dwLowDateTime:0,
            times?((unsigned long long)user.dwHighDateTime<<32)|user.dwLowDateTime:0);
        if(got) {
            describe(out,"RIP",ctx.Rip);
            fprintf(out,"RSP=%llx RAX=%llx RCX=%llx RDX=%llx R8=%llx R9=%llx\n",ctx.Rsp,ctx.Rax,ctx.Rcx,ctx.Rdx,ctx.R8,ctx.R9);
            for(unsigned i=0;i<bytes/sizeof(stack[0]);i++) {
                char label[32];snprintf(label,sizeof(label),"stack+%03x",i*8);describe(out,label,stack[i]);
            }
        }
        fflush(out);
    }
    CloseHandle(snap);fprintf(out,"END SNAPSHOT\n");fflush(out);
}
static DWORD WINAPI worker(void *unused) {
    (void)unused;FILE *out=fopen("C:\\Games\\ReSkate\\logs\\ps5-threads.log","w");
    if(!out)return 1;setvbuf(out,NULL,_IONBF,0);
    fprintf(out,"ReSkate PS5 diagnostic sampling started\n");
    char configured[20];DWORD delay=45000;
    if(GetEnvironmentVariableA("RESKATE_DIAGNOSTICS_DELAY",configured,sizeof(configured))){
        unsigned long value=strtoul(configured,NULL,10);if(value>=5&&value<=600)delay=value*1000;
    }
    Sleep(delay);snapshot(out);Sleep(30000);snapshot(out);fclose(out);return 0;
}
__declspec(dllexport) void WINAPI StartDiagnostics(void) {
    HANDLE thread=CreateThread(NULL,0,worker,NULL,0,NULL);if(thread)CloseHandle(thread);
}
