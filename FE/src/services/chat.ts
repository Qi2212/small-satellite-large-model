import axios from "axios";
import { useChatStore } from "@/stores/chat";
import { useUserStore } from "@/stores/user";
const userStore = useUserStore();
import { http } from "../utils/http";
export let source: any;
/**
 * 获取相似文本
 * @param question 问题
 */
export const postSimilarText = (question: string): any => {
  const chatStore = useChatStore();
  source = axios.CancelToken.source();
  return http.post(
    "/model/similartext/",
    {
      query: question,
      account: userStore.user.account,
      type: chatStore.currentBase!.type,
      pid: chatStore.currentBase!.id,
    },
    {
      cancelToken: source.token,
    }
  );
};
export const deleteQuestion = (): any => {
  return http.delete("/delete/");
};
