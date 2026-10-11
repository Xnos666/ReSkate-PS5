#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <xinput.h>
#include <d3d12.h>
#include <dxgi1_4.h>
#include <stdio.h>

static FILE *logfile;
static bool check(const char *name,HRESULT result){
    fprintf(logfile,"%s=0x%08lx\n",name,(unsigned long)result);fflush(logfile);
    return SUCCEEDED(result);
}
static LRESULT CALLBACK window_proc(HWND w,UINT m,WPARAM p,LPARAM l){return DefWindowProcW(w,m,p,l);}
int main(){
    logfile=fopen("C:\\graphics-probe.txt","w");if(!logfile)return 1;
    setvbuf(logfile,NULL,_IONBF,0);
    HMODULE input=LoadLibraryW(L"xinput1_4.dll");
    auto getstate=input?(DWORD(WINAPI*)(DWORD,XINPUT_STATE*))GetProcAddress(input,"XInputGetState"):nullptr;
    XINPUT_STATE state{};DWORD controller=getstate?getstate(0,&state):GetLastError();
    fprintf(logfile,"XInputGetState=%lu packet=%lu\n",controller,state.dwPacketNumber);
    WNDCLASSW wc{};wc.lpfnWndProc=window_proc;wc.hInstance=GetModuleHandleW(nullptr);wc.lpszClassName=L"ReSkateGraphicsProbe";
    RegisterClassW(&wc);
    HWND window=CreateWindowExW(0,wc.lpszClassName,L"ReSkate PS5 graphics test",WS_OVERLAPPEDWINDOW|WS_VISIBLE,0,0,1280,720,nullptr,nullptr,wc.hInstance,nullptr);
    fprintf(logfile,"window=%p error=%lu\n",window,GetLastError());if(!window)return 2;
    IDXGIFactory4 *factory=nullptr;ID3D12Device *device=nullptr;
    if(!check("CreateDXGIFactory1",CreateDXGIFactory1(__uuidof(IDXGIFactory4),(void**)&factory)))return 3;
    IDXGIAdapter1 *adapter=nullptr;
    if(SUCCEEDED(factory->EnumAdapters1(0,&adapter))){
        DXGI_ADAPTER_DESC1 description{};adapter->GetDesc1(&description);
        char name[160]{};WideCharToMultiByte(CP_UTF8,0,description.Description,-1,name,sizeof(name),nullptr,nullptr);
        fprintf(logfile,"Adapter=%s Vendor=%04x Device=%04x\n",name,description.VendorId,description.DeviceId);
    }
    if(!check("D3D12CreateDevice",D3D12CreateDevice(adapter,D3D_FEATURE_LEVEL_11_0,__uuidof(ID3D12Device),(void**)&device)))return 4;
    D3D12_COMMAND_QUEUE_DESC qd{};qd.Type=D3D12_COMMAND_LIST_TYPE_DIRECT;ID3D12CommandQueue *queue=nullptr;
    if(!check("CreateCommandQueue",device->CreateCommandQueue(&qd,__uuidof(ID3D12CommandQueue),(void**)&queue)))return 5;
    char multi_mode[4]{};
    if(GetEnvironmentVariableA("RESKATE_TEST_MULTI_QUEUE",multi_mode,sizeof(multi_mode))&&multi_mode[0]=='1'){
        ID3D12CommandQueue *copy=nullptr,*compute=nullptr;
        qd.Type=D3D12_COMMAND_LIST_TYPE_COPY;
        if(!check("CreateCopyQueue",device->CreateCommandQueue(&qd,__uuidof(ID3D12CommandQueue),(void**)&copy)))return 19;
        qd.Type=D3D12_COMMAND_LIST_TYPE_COMPUTE;
        if(!check("CreateComputeQueue",device->CreateCommandQueue(&qd,__uuidof(ID3D12CommandQueue),(void**)&compute)))return 20;
        ID3D12Fence *copied=nullptr,*drawn=nullptr,*computed=nullptr;
        if(!check("CreateCopyFence",device->CreateFence(0,D3D12_FENCE_FLAG_NONE,__uuidof(ID3D12Fence),(void**)&copied)))return 21;
        if(!check("CreateDrawFence",device->CreateFence(0,D3D12_FENCE_FLAG_NONE,__uuidof(ID3D12Fence),(void**)&drawn)))return 22;
        if(!check("CreateComputeFence",device->CreateFence(0,D3D12_FENCE_FLAG_NONE,__uuidof(ID3D12Fence),(void**)&computed)))return 23;
        // Intentionally submit waits before their signals on other queues.
        if(!check("GraphicsWaitCopy",queue->Wait(copied,1)))return 24;
        if(!check("GraphicsSignal",queue->Signal(drawn,1)))return 25;
        if(!check("ComputeWaitGraphics",compute->Wait(drawn,1)))return 26;
        if(!check("ComputeSignal",compute->Signal(computed,1)))return 27;
        Sleep(100);
        if(!check("CopySignal",copy->Signal(copied,1)))return 28;
        HANDLE complete=CreateEventW(nullptr,FALSE,FALSE,nullptr);
        if(!check("CrossQueueEvent",computed->SetEventOnCompletion(1,complete)))return 29;
        DWORD cross=WaitForSingleObject(complete,5000);
        fprintf(logfile,"Cross-queue wait=%lu\n",cross);
        if(cross!=WAIT_OBJECT_0)return 30;
    }
    DXGI_SWAP_CHAIN_DESC1 sd{};sd.Width=1280;sd.Height=720;sd.Format=DXGI_FORMAT_R8G8B8A8_UNORM;sd.SampleDesc.Count=1;sd.BufferUsage=DXGI_USAGE_RENDER_TARGET_OUTPUT;sd.BufferCount=2;sd.SwapEffect=DXGI_SWAP_EFFECT_FLIP_DISCARD;
    char mode[4]{};bool waitable=GetEnvironmentVariableA("RESKATE_TEST_FRAME_LATENCY",mode,sizeof(mode))&&mode[0]=='1';
    if(waitable)sd.Flags=DXGI_SWAP_CHAIN_FLAG_FRAME_LATENCY_WAITABLE_OBJECT;
    IDXGISwapChain1 *swap=nullptr;
    if(!check("CreateSwapChainForHwnd",factory->CreateSwapChainForHwnd(queue,window,&sd,nullptr,nullptr,&swap)))return 6;
    DWORD latency_wait=WAIT_OBJECT_0;
    if(waitable){
        IDXGISwapChain2 *swap2=nullptr;
        if(!check("GetSwapChain2",swap->QueryInterface(__uuidof(IDXGISwapChain2),(void**)&swap2)))return 17;
        if(!check("SetMaximumFrameLatency",swap2->SetMaximumFrameLatency(1)))return 18;
        HANDLE ready=swap2->GetFrameLatencyWaitableObject();
        latency_wait=WaitForSingleObject(ready,5000);
        fprintf(logfile,"Initial frame latency wait=%lu handle=%p\n",latency_wait,ready);
        swap2->Release();
    }
    D3D12_DESCRIPTOR_HEAP_DESC hd{};hd.Type=D3D12_DESCRIPTOR_HEAP_TYPE_RTV;hd.NumDescriptors=1;ID3D12DescriptorHeap *heap=nullptr;
    if(!check("CreateDescriptorHeap",device->CreateDescriptorHeap(&hd,__uuidof(ID3D12DescriptorHeap),(void**)&heap)))return 7;
    ID3D12Resource *backbuffer=nullptr;
    if(!check("GetBuffer",swap->GetBuffer(0,__uuidof(ID3D12Resource),(void**)&backbuffer)))return 8;
    auto rtv=heap->GetCPUDescriptorHandleForHeapStart();device->CreateRenderTargetView(backbuffer,nullptr,rtv);
    ID3D12CommandAllocator *allocator=nullptr;ID3D12GraphicsCommandList *commands=nullptr;
    if(!check("CreateCommandAllocator",device->CreateCommandAllocator(D3D12_COMMAND_LIST_TYPE_DIRECT,__uuidof(ID3D12CommandAllocator),(void**)&allocator)))return 9;
    if(!check("CreateCommandList",device->CreateCommandList(0,D3D12_COMMAND_LIST_TYPE_DIRECT,allocator,nullptr,__uuidof(ID3D12GraphicsCommandList),(void**)&commands)))return 10;
    D3D12_RESOURCE_BARRIER barrier{};barrier.Type=D3D12_RESOURCE_BARRIER_TYPE_TRANSITION;barrier.Transition.pResource=backbuffer;barrier.Transition.StateBefore=D3D12_RESOURCE_STATE_PRESENT;barrier.Transition.StateAfter=D3D12_RESOURCE_STATE_RENDER_TARGET;barrier.Transition.Subresource=D3D12_RESOURCE_BARRIER_ALL_SUBRESOURCES;
    commands->ResourceBarrier(1,&barrier);float color[4]={0.03f,0.4f,0.7f,1.0f};commands->ClearRenderTargetView(rtv,color,0,nullptr);
    barrier.Transition.StateBefore=D3D12_RESOURCE_STATE_RENDER_TARGET;barrier.Transition.StateAfter=D3D12_RESOURCE_STATE_PRESENT;commands->ResourceBarrier(1,&barrier);
    if(!check("CloseCommandList",commands->Close()))return 11;
    ID3D12CommandList *lists[]={commands};queue->ExecuteCommandLists(1,lists);
    if(!check("Present",swap->Present(1,0)))return 12;
    ID3D12Fence *fence=nullptr;
    if(!check("CreateFence",device->CreateFence(0,D3D12_FENCE_FLAG_NONE,__uuidof(ID3D12Fence),(void**)&fence)))return 13;
    if(!check("Signal",queue->Signal(fence,1)))return 14;
    HANDLE event=CreateEventW(nullptr,FALSE,FALSE,nullptr);
    if(!check("SetEventOnCompletion",fence->SetEventOnCompletion(1,event)))return 15;
    DWORD wait=WaitForSingleObject(event,10000);
    bool passed=wait==WAIT_OBJECT_0&&latency_wait==WAIT_OBJECT_0;
    fprintf(logfile,"GPU fence wait=%lu\nRESULT=%s\n",wait,passed?"PASS":"FAIL");
    Sleep(2000);fclose(logfile);return passed?0:16;
}
