import axios from "axios";
import { http } from "../utils/http";
import { useUserStore } from "@/stores/user";
const userStore = useUserStore();
/**
 * POST 新建个人知识库
 * @param name 知识库名称
 * @param synopsis 知识库简介
 */
export const postCreatePersonalBaseAPI = (
  name: string,
  synopsis: string
): any => {
  return http.post("/api/db/psl/create_db", {
    partition_synopsis: synopsis,
    account: userStore.user.account,
    partition_nickname: name,
  });
};
/**
 * POST 新建公共知识库
 * @param
 */
export const postCreatePublicBaseAPI = (
  name: string,
  synopsis: string
): any => {
  return http.post("/api/db/pub/create_db", {
    partition_synopsis: synopsis,
    account: userStore.user.account,
    partition_nickname: name,
  });
};
/**
 * GET 获取知识库列表
 * @param
 */
export const getBaseListAPI = (page: number): any => {
  return http.get("/api/db/both/kdbrecords", {
    params: {
      page: page,
      account: userStore.user.account,
    },
  });
};
/**
 * GET 获取全部知识库名称及id
 * @param
 */
export const getAllBaseOptionAPI = (): any => {
  return http.get("/api/db/all/kdbs", {
    params: {
      account: userStore.user.account,
    },
  });
};
/**
 * GET 获取全部公共知识库名称及id
 * @param
 */
export const getPublicBaseOptionAPI = (): any => {
  return http.get("/api/db/pub/info", {
    params: {
      account: userStore.user.account,
    },
  });
};
/**
 * GET 获取所有普通用户文件上传记录
 * @param
 */
export const getAllFileRecordsAPI = (page: number): any => {
  return http.get("/api/db/psl/filerecords", {
    params: {
      page: page,
      account: userStore.user.account,
    },
  });
};
/**
 * GET 获取超管所有文件上传记录
 * @param
 */
export const getAdminFileRecordsAPI = (page: number): any => {
  return http.get("/api/db/adm/filerecords", {
    params: {
      page: page,
      account: userStore.user.account,
    },
  });
};
/**
 * GET 获取文件审核列表
 * @param
 */
export const getCheckFileListAPI = (page: number): any => {
  return http.get("/api/db/pub/check", {
    params: {
      page: page,
      account: userStore.user.account,
    },
  });
};
/**
 * PATCH 审核文件
 * @param
 */
export const patchCheckFileAPI = (
  operate: boolean,
  pid: string,
  fid: string
): any => {
  return http.patch("/api/db/pub/operate", {
    operate: operate,
    account: userStore.user.account,
    pid: pid,
    fid: fid,
  });
};
/**
 * GET 获取个人知识库文件
 * @param
 */
export const getPersonalFileAPI = (page: number, pid: string): any => {
  return http.get("/api/db/psl/kbasefiles", {
    params: {
      page: page,
      account: userStore.user.account,
      pid: pid,
    },
  });
};
/**
 * GET 获取公共知识库文件
 * @param
 */
export const getPublicFileAPI = (page: number, pid: string): any => {
  return http.get("/api/db/pub/kbasefiles", {
    params: {
      page: page,
      account: userStore.user.account,
      pid: pid,
    },
  });
};
/**
 * DELETE 删除知识库
 * @param
 */
export const deleteBaseAPI = (
  pid: string,
  type:string
): any => {
  return http.delete("/api/db/both/delpartition", {
    data: {
      account: userStore.user.account,
      pid: pid,
      type: type,
    },
  });
};
/**
 * DELETE 删除知识库文件
 * @param
 */
export const deleteFileAPI = (
  pid: string,
  fid: string,
  type:string
): any => {
  return http.delete("/api/db/both/delfilerecord", {
    data: {
      account: userStore.user.account,
      pid: pid,
      fid: fid,
      type: type,
    },
  });
};
/**
 * PATCH 知识库重命名
 * @param
 */
export const patchRenameBaseAPI = (
  new_nickname: string,
  pid: string,
  type: string
): any => {
  return http.patch("/api/db/both/renamekbase", {
    new_nickname: new_nickname,
    account: userStore.user.account,
    pid: pid,
    type: type,
  });
};
