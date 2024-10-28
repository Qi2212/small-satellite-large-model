<script setup lang="ts">
import { ref, watch,watchEffect } from "vue";
import { RouterView, useRouter } from "vue-router";
const router = useRouter();
import Input from "./components/Input.vue";
import { useChatStore } from "@/stores/chat";
const chatStore = useChatStore();

watchEffect(() => {
  if (chatStore.questionList.length === 0) {
    router.push("/index");
  }
  if (chatStore.questionList.length > 0) {
    router.push("/chat");
  }
})

</script>

<template>
  <router-view v-slot="{ Component }">
    <component :is="Component"/>
  </router-view>
  <Input />
</template>

<style scoped lang="scss">
</style>