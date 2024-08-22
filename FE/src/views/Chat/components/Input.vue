<script setup lang="ts">
import { ref, watch } from "vue";
import { useChatStore } from "@/stores/chat";
import { useUserStore } from "@/stores/user";
const userStore = useUserStore();
import UploadPopup from "@/components/UploadPopup.vue";
import SetPopup from "@/components/SetPopup.vue";
import IconSet from "@/components/icons/IconSet.vue"
import IconUpload from "@/components/icons/IconUpload.vue"
import { ElMessage, ElMessageBox } from "element-plus";

const chatStore = useChatStore();
const input = ref("");

const dialogFormVisible = ref(false);
const feedData = () => {
  if (chatStore.currentBase!.id === "") {
    ElMessage({
      type: 'error',
      message: '尚未选择知识库',
      duration:2000
    })
    return
  }
  if (userStore.user.type === 'normal' && chatStore.currentBase.type === 'public') {
    ElMessage({
      type: 'error',
      message: '暂无权限将文件上传至公共知识库',
      duration:2000
    })
    return
  }
  dialogFormVisible.value = true;
};

// 发送问题
const sendQuestion = async () => {
  console.log(input.value);
  if (chatStore.currentBase!.id === "" && chatStore.chatMode !== "rawAnswer") {
    ElMessage({
      type: 'error',
      message: '尚未选择对话知识库',
      duration:2000
    })
    return
  }
  const question = input.value as string;
  input.value = "";
  if (question === "" || chatStore.chatStatus === "doing") return;
  chatStore.questionList.push({
    question: question,
    rawAnswer: { content: "", text: "", status: "undo" },
    enhancedAnswer: { content: "", text: "", status: "undo" },
    similarText: { content: "", text: "", status: "undo" },
    activeAnswer: chatStore.chatMode,
  });
  // scroll(main.value!)
  chatStore.getAnswer(
    question,
    chatStore.chatMode,
    chatStore.questionList.length - 1
  );
};
defineEmits(["sendQuestion"]);
</script>

<template>
  <div class="index-100 fixed bottom-0 h-[120px] md:h-[130px] w-full">
    <div class="flex flex-wrap justify-between md:w-1/2 w-11/12 mx-auto mb-2">
      <div class="flex gap-px sm:gap-1 mb-2">
        <button
          v-for="item in chatStore.modeList"
          :class="
            chatStore.chatMode == item.value
              ? 'bg-[#253c8e] text-white'
              : 'border border-[#253c8e] text-[#253c8e] bg-white'
          "
          class="transition duration-300 lg:px-4 px-1 py-1 rounded text-xs sm:text-sm"
          @click="chatStore.chatMode = item.value"
        >
          {{ item.label }}
        </button>
      </div>
      <div class="bg-white py-3 px-2 flex flex-between rounded-lg w-full">
        <el-tooltip effect="light" content="文件上传" placement="top">
          <button
            @click="feedData"
            class="transition duration-300 ease-in-out scale-75 md:scale-100 text-white mr-1"
          >
            <IconUpload />
          </button>
        </el-tooltip>
        <input
          v-model="input"
          class="bg-transparent focus:outline-none md:w-11/12 w-5/6"
          @keyup.enter="sendQuestion"
          placeholder="请输入你的问题或关键词"
        />
        <button
          :disabled="input!.length === 0 || chatStore.chatStatus === 'doing'"
          @click="sendQuestion"
          class="transition duration-300 ease-in-out scale-75 md:scale-100"
        >
          <svg
            t="1715924109995"
            class=""
            viewBox="0 0 1024 1024"
            version="1.1"
            xmlns="http://www.w3.org/2000/svg"
            p-id="22200"
            width="30"
            height="30"
          >
            <path
              d="M917.333333 473.6l-763.733333-384c-38.4-17.066667-81.066667 17.066667-64 55.466667l106.666667 285.866666L682.666667 512 196.266667 593.066667l-106.666667 285.866666c-12.8 38.4 25.6 72.533333 64 51.2l763.733333-384c29.866667-12.8 29.866667-55.466667 0-72.533333z"
              p-id="22201"
              :fill="
                input && chatStore.chatStatus !== 'doing' ? '#467cfd' : 'grey'
              "
            ></path>
          </svg>
        </button>
      </div>
    </div>
    <div class="w-screen text-center text-gray-600 text-xs md:text-sm">
      所有内容均由{{
        chatStore.title
      }}生成，其准确性和完整性无法保证，不代表我们的态度或观点
    </div>
  </div>
  <!-- 上传语料弹窗 -->
  <UploadPopup v-model:isShow="dialogFormVisible" :base="chatStore.currentBase" />
</template>
