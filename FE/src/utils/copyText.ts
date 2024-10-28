import { ElMessage } from "element-plus";

export const copyText = (text: string) => {
  navigator.clipboard.writeText(text)
    .then(() => {
      ElMessage({
        message: "复制成功",
        type: "success",
        plain: true,
      });
    })
    .catch((err) => {
      console.error("复制文本时出错：", err);
    });
};
