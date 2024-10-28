<script setup lang="ts">
import { ref , onMounted} from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";
const router = useRouter();
const route = useRoute()
import { useUserStore } from "@/stores/user";
const userStore = useUserStore();
import { useChatStore } from "@/stores/chat";
import { getAllBaseOptionAPI } from "@/services/base";
import History from "@/components/History.vue";
import BaseType from "@/components/BaseType.vue"
const chatStore = useChatStore();
const isHistoryOpen = ref(false);

const newChat = () => {
  chatStore.newQuestion();
  router.push("/index")
};

const getBaseOption = async() => {
  const res = await getAllBaseOptionAPI()  
  console.log(res);
  options.value = res.data.map((item: any) => {
    return {
      value: item.pid,
      label: item.name,
      type:  item.type,
    }
  })
}
onMounted(() => {
  getBaseOption()
})
const options = ref<{
  value: string,
  label: string,
  type: string
}[]>()
const baseSelectRef = ref()
const selectValue = ref('')
const changeBase = (value: string) => {
  console.log(value);
  const base = options.value?.find((item) => {
    return item.value === value
  })
  chatStore.currentBase!.id = base!.value
  chatStore.currentBase!.name = base!.label
  chatStore.currentBase!.type = base!.type
}
</script>
<template>
  <div
    class="md:flex hidden bg-[#f2f2f2] w-[240px] h-full fixed flex-col items-center shadow-xl z-50"
  >
    <h2 class="flex items-center text-[#28449C] font-bold mt-8 mb-2">
      <img
        src="../../assets/image/satellite.svg"
        class="h-[24px]"
      />小卫星私域大模型
    </h2>
    <span class="text-gray-500 text-xs">当前版本：v1.0.1</span>
    <div
      class="flex bg-white my-5 flex-col w-4/5 py-2 px-2 items-start rounded-md"
    >
      <button 
        class="w-full flex items-center p-2 my-1 hover:bg-slate-100 rounded-md" 
        @click="newChat"
        :class="route.name === 'index' ? 'is-active bg-slate-100' : ''">
        <span class="w-8"
          ><img src="../../assets/image/menu/talk.png" width="24" alt=""
        /></span>
        <span class="text-sm">开启对话</span>
      </button>
      <!-- <button class="w-full flex items-center" @click="isHistoryOpen = true">
        <span class="w-8"
          ><img src="../../assets/image/menu/history.png" width="24" alt=""
        /></span>
        <span class="text-xs">历史记录</span>
      </button> -->
      <!-- <button class="w-full flex items-center p-2 hover:bg-slate-100 rounded-md " @click="router.push('/library')">
        <span class="w-8"
          ><img src="../../assets/image/menu/base.png" width="20" alt=""
        /></span>
        <span class="text-sm">上传记录</span>
      </button> -->
      <button 
        class="w-full flex items-center p-2 my-1 hover:bg-slate-100 rounded-md " 
        @click="router.push('/library')"
        :class="route.name === 'library' ? 'is-active bg-slate-100' : ''">
        <span class="w-8"
          ><img src="../../assets/image/menu/base.png" width="20" alt=""
        /></span>
        <span class="text-sm" v-if="userStore.user.type === 'admin'">知识库管理</span>
        <span class="text-sm" v-else>知识库</span>
      </button>
      <button class="w-full flex items-center p-2 my-1 hover:bg-slate-100 rounded-md" 
        :class="route.name === 'fileRecords' ? 'is-active bg-slate-100' : ''"
        @click="router.push('/fileRecords')"
        >
        <span class="w-8"
          ><img src="../../assets/image/menu/history.png" width="20" alt=""
        /></span>
        <span class="text-sm">文件记录</span>
      </button>
    </div>
    <div class="flex bg-white my-5 flex-col w-4/5 py-3 px-2 items-start rounded-md">
      <span class="mb-2">
        <el-text>当前对话知识库：</el-text>
      </span>
      <el-select
        v-model="selectValue"
        placeholder="未选择"
        @focus = getBaseOption
        ref="baseSelectRef"
        @change="changeBase"
      >
        <el-option
          v-for="item in options"
          :key="item.value"
          :label="item.label"
          :value="item.value">
          <div class="flex justify-between items-center">
            <el-text size="small">{{ item.label }}</el-text>
            <BaseType :type="item.type" />
          </div>
        </el-option>
      </el-select>
    </div>
  </div>
  <History v-model="isHistoryOpen" />
</template>
<style scoped lang="scss">
.is-active{
  color: #01358e;
}
</style>
