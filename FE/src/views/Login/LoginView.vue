<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useChatStore } from "@/stores/chat";
import Login from "./components/Login.vue";
import Register from "./components/Register.vue";

const chatStore = useChatStore();
const router = useRouter();

const status = ref<"login" | "register">("login");
</script>
<template>
  <div class="flex">
    <div class="bg-[url(/src/assets/image/login/loginBg.png)] bg-cover bg-no-repeat h-[100vh] w-[30vw] flex flex-col items-center">
      <img src="../../assets/title.png" class="mt-28 w-3/5" />
      <h1 class="z-50 text-white text-2xl mt-20">{{ chatStore.title }}</h1>
      <span class="text-white text-xs mt-2">
        你好，欢迎使用{{ chatStore.title }}
      </span>
    </div>
    <div class="flex flex-1 items-center justify-center">
      <div 
        class="bg-white flex flex-col items-center h-[320px] w-2/5 justify-between px-10 py-6 rounded-xl border">
        <Login 
          v-if="status === 'login'" 
          v-model:status="status" />
        <Register
          v-else-if="status === 'register'"
          v-model:status="status" />
      </div>
    </div>
  </div>
</template>
<style scoped></style>
