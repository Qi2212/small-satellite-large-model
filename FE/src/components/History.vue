<script setup lang="ts">
const isOpen = defineModel<boolean>('isOpen')
import { ref } from 'vue'

const activeNames = ref(['1'])
const handleChange = (val: string[]) => {
  console.log(val)
}
</script>
<template>
<el-drawer v-model="isOpen" title="I am the title" :with-header="false" direction="ltr" size="300">
  <div class="w-full flex border-2 border-blue-500 rounded-xl mb-5 bg-white py-2 px-2">
    <svg t="1716044286442" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="8903" width="25" height="25"><path d="M472.615385 905.846154a433.230769 433.230769 0 1 0 0-866.461539 433.230769 433.230769 0 0 0 0 866.461539z m0-78.769231a354.461538 354.461538 0 1 1 0-708.923077 354.461538 354.461538 0 0 1 0 708.923077z" fill="#467cfd" p-id="8904"></path><path d="M715.697231 755.081846a39.384615 39.384615 0 0 1 55.689846 0l167.069538 167.069539a39.384615 39.384615 0 1 1-55.689846 55.689846l-167.069538-167.069539a39.384615 39.384615 0 0 1 0-55.689846z m55.689846 55.689846a39.384615 39.384615 0 0 0 0-55.689846l167.069538 167.069539a39.384615 39.384615 0 1 0-55.689846 55.689846l-167.069538-167.069539a39.384615 39.384615 0 0 0 55.689846 0z" fill="#467cfd" p-id="8905"></path></svg>
    <input type="text" class="flex-1 ml-1 focus:outline-none" size="large" placeholder="搜索历史记录"/>
  </div>
    <el-collapse v-model="activeNames" @change="handleChange">
      <el-collapse-item title="今天" name="1">
        <div v-for="item in 1" class="mb-1 hover:bg-gray-100 hover:rounded-xl px-3 py-1 flex justify-between">
          <span>山西经济发展如何 </span>
          <span>16:28</span>
        </div>
      </el-collapse-item>
      <el-collapse-item title="本周" name="2">
        <div v-for="item in 1" class="mb-1 hover:bg-gray-100 hover:rounded-xl px-3 py-1 flex justify-between">
          <span>山西经济发展如何 </span>
          <span>星期三</span>
        </div>
      </el-collapse-item>
      <el-collapse-item title="本月" name="3">
        <div v-for="item in 1" class="mb-1 hover:bg-gray-100 hover:rounded-xl px-3 py-1 flex justify-between">
          <span>山西经济发展如何 </span>
          <span>05月05日</span>
        </div>
      </el-collapse-item>
      <el-collapse-item title="本年" name="4">
        <div v-for="item in 1" class="mb-1 hover:bg-gray-100 hover:rounded-xl px-3 py-1 flex justify-between">
          <span>山西经济发展如何 </span>
          <span>04月04日</span> 
        </div>
      </el-collapse-item>
    </el-collapse>
</el-drawer>
</template>
<style lang="scss">
// .el-overlay{
//   background-color: transparent;
// }
</style>