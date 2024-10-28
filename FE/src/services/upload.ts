import axios from "axios"
import { http } from "../utils/http";
import { useUserStore } from "@/stores/user";
const userStore = useUserStore(); 
export let source: any;
/**
 * POST 上传文件
 *
 * @param name 知识库名称
 * @param synopsis 知识库简介
 */
export const postUploadAPI = (
  pid: string,
  is_share: boolean,
  sid: string,
  file:File
): any => {
    source = axios.CancelToken.source();
    const formData = new FormData();
    formData.append("pid", pid);
    formData.append("is_share", String(is_share));
    formData.append("sid", String(sid));
    formData.append("file", file);
    formData.append("account", userStore.user.account);
    return http.post("/api/db/psl/upload", formData,
    {
      cancelToken: source.token,
    });
};
/**
 * POST 超管向公共知识库上传文件
 *
 * @param name 知识库名称
 * @param synopsis 知识库简介
 */
export const postUploadToPublicFromAdminAPI = (
  pid: string,
  file:File
): any => {
    source = axios.CancelToken.source();
    const formData = new FormData();
    formData.append("pid", pid);
    formData.append("file", file);
    formData.append("account", userStore.user.account);
    return http.post("/api/db/pub/upload", formData, {
        onUploadProgress: function (progressEvent) {
            // 处理原生进度事件
            console.log(progressEvent);
        },
        cancelToken: source.token,
    });
};
