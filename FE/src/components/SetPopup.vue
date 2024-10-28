<script setup lang="ts">
import  { ref } from "vue"
import type { UploadProps, UploadUserFile } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import Upload from "./Upload.vue";

const isShow = defineModel('isShow')

const fileList = ref<UploadUserFile[]>([])

const handleRemove: UploadProps['onRemove'] = (uploadFile, uploadFiles) => {
  console.log(uploadFile, uploadFiles)
}
const handlePreview: UploadProps['onPreview'] = (file) => {
  console.log(file)
}
//上传数据
</script>

<template>
<!-- 上传语料弹窗 -->
<el-dialog v-model="isShow" top="20vh" width="40vw" destroy-on-close title="对话设置":z-index="9999">
  <Upload />
  <template #footer>
    <el-button type="primary">保存</el-button>
  </template>
</el-dialog>
</template>
<style scoped lang="scss">
</style>