import { ref, onMounted, onUnmounted } from "vue";
// 定义一个用于管理WebSocket的Composition API函数
export function useWebSocket(url:string) {
  // 创建WebSocket连接
  const ws = ref<any>(null);
  const message = ref("")
  // 定义响应WebSocket事件的函数
  const onOpen = (event:any) => {
    console.log("WebSocket connection opened:", event);
  };

  const onMessage = (event:any) => {
    console.log("WebSocket message received:", JSON.parse(event.data));
    message.value += JSON.parse(event.data).ans;
  };

  const onError = (event:any) => {
    console.error("WebSocket error:", event);
  };

  const onClose = (event: any) => {
    console.log(message.value);
    
    console.log("WebSocket connection closed:", event);
    // 考虑实现自动重连逻辑
  };

  // 设置WebSocket连接
  const connect = () => {
    ws.value = new WebSocket(url);
    ws.value.onopen = onOpen;
    ws.value.onmessage = onMessage;
    ws.value.onerror = onError;
    ws.value.onclose = onClose;
  };

  // 关闭WebSocket连接
  const close = () => {
    if (ws.value) {
      ws.value.close();
    }
  };

  // 当useWebSocket被调用时，尝试连接WebSocket服务器
  // onMounted(connect);

  // 当组件销毁时，关闭WebSocket连接
  // onUnmounted(close);

  // 返回WebSocket实例和其他可能需要导出的函数或响应
  return {
    ws,
    message,
    connect,
    close,
  };
}
