<script setup lang="ts">
import { ref, watch, watchEffect } from "vue";
import type { Mode } from "@/types/chat";
import { useChatStore } from "@/stores/chat";
const chatStore = useChatStore();
import { copyText } from "@/utils/copyText";
import { ElMessage, ElMessageBox } from 'element-plus'
import IconCopy from "./icons/IconCopy.vue";
import IconLike from "./icons/IconLike.vue";
import IconDislike from "./icons/IconDislike.vue";
import IconFire from "./icons/IconFire.vue";
import { scroll } from "@/utils/scroll";

//获取窗口滚动元素
const main = ref<HTMLElement>();
watch(
  () => chatStore.questionList[chatStore.questionList.length - 1],
  () => {
    scroll(main.value!);
  }
);

const changeActiveAnswer = (question: string, mode: Mode, index: number) => {
  // console.log(question, mode, index);
  // console.log(chatStore.questionList[index][mode].status);
  // console.log("切换了");
  if (chatStore.questionList[index][mode].status !== "undo") return;
  chatStore.getAnswer(question, mode, index);
};
</script>

<template>
  <div
    class="main md:h-[calc(100vh-80px-130px)] h-[calc(100vh-60px-120px)]"
    ref="main"
  >
    <!-- 问答列表 -->
    <div
      v-for="(item, index) in chatStore.questionList"
      class="md:w-1/2 w-11/12 mx-auto my-5 transition ease-in-out duration-200 relative"
    >
      <div class="mx-auto w-full md:w-[50vw] flex justify-end">
        <div class="bg-blue-500 rounded-lg text-white px-3 py-3 text-sm shadow-sm">
          <span>{{ item.question }}</span>
        </div>
        <img
          src="../../../assets/user.png"
          class="absolute -right-10 top-0 w-8 hidden md:block"
        />
      </div>
      <div class="relative">
        <div
          class="bg-white w-8 p-1 rounded-full absolute -left-10 top-14 hidden md:block shadow-sm"
        >
          <img src="../../../assets/image/satellite.svg" />
        </div>
        <el-tabs
          v-model="item.activeAnswer"
          class="mx-auto md:w-[50vw]"
          @tab-change="changeActiveAnswer(item.question, item.activeAnswer, index)"
        >
          <el-tab-pane
            :disabled="chatStore.chatStatus === 'doing'"
            v-for="mode in chatStore.modeList"
            :label="mode.label"
            :name="mode.value"
          >
            <div class="bg-white rounded-lg max-w-2/3 px-3 py-3 shadow-sm">
              <IconFire v-if="item[mode.value].content === '' && item[mode.value].status === 'undo'"/>
              <IconFire
                class="animate-pulse"
                v-else-if="item[mode.value].content === ''"
              />
              <el-text
                class="answer text-black" size="large"
                v-html="item[mode.value].content">
              </el-text>
            </div>
          </el-tab-pane>
          <div class="w-full h-6 relative mt-1">
            <div
              class="absolute left top-0 text-blue-400 text-sm hover:text-gray-400"
            >
              <button
                v-if="chatStore.questionList[index][item.activeAnswer].status === 'doing'"
                @click="chatStore.closeQuestion(item.activeAnswer, index)"
              >
                停止生成
              </button>
              <button
                v-else-if="chatStore.questionList[index][item.activeAnswer].status ==='done' && chatStore.chatStatus !== 'doing'"
                @click="chatStore.reQuestion(item.question, item.activeAnswer, index)"
              >
                重新生成
              </button>
              <button
                v-else-if="chatStore.questionList[index][item.activeAnswer].status === 'undo'"
                @click="chatStore.reQuestion(item.question, item.activeAnswer, index)"
                class="text-gray-400"
              >
                已停止
              </button>
            </div>
            <div class="absolute right-0 top-0 flex gap-2">
              <span @click="copyText(chatStore.questionList[index][item.activeAnswer].text)">
                <IconCopy />
              </span>
              <span><IconLike /></span>
              <span><IconDislike /></span>
            </div>
          </div>
        </el-tabs>
      </div>
    </div>
  </div>
</template>
<style scoped lang="scss">
.main {
  overflow: auto;
  &::-webkit-scrollbar {
    width: 3px; /* 滚动条宽度 */
  }
  &::-webkit-scrollbar-track {
    /* 滚动条轨道样式 */
    background-color: #f5f5f5;
    border-radius: 10px;
  }
  &::-webkit-scrollbar-thumb {
    /* 滚动条滑块样式 */
    background-color: #9c9c9c;
    border-radius: 10px;
  }
  &::-webkit-scrollbar-thumb:hover {
    /* 滑块在hover时的样式 */
    background-color: #aaa;
  }
}
.answer {
  font-size: 0.875rem; /* 14px */
  line-height: 1.25rem; /* 20px */
  @media (min-width: 768px) {
    font-size: 0.875rem; /* 16px */
    line-height: 1.25rem; /* 24px */
  }
  :deep(h1) {
    font-weight: 600;
    @media (min-width: 768px) {
      font-size: 1.4rem;
    }
  }
  :deep(h2) {
    font-weight: 500;
    @media (min-width: 768px) {
      font-size: 1.3rem;
    }
  }
  :deep(h3) {
    font-weight: 500;
    @media (min-width: 768px) {
      font-size: 1.2rem;
    }
  }
  :deep(h4) {
    font-weight: 500;
    @media (min-width: 768px) {
      font-size: 1.1rem;
    }
  }
  :deep(h5) {
    font-size: 1rem;
    font-weight: 600;
  }
  :deep(p) {
    margin: 0.3rem 0;
  }
}
</style>
