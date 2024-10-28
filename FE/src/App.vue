<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import { ElConfigProvider } from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
</script>

<template>
  <el-config-provider :locale="zhCn">
    <div class="app">
      <RouterView />
    </div>
  </el-config-provider>
</template>

<style lang="scss">
*{
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

.app {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  background-color: #F4F5FA;
}
</style>