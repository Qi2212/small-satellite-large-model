<script setup lang="ts">
import  { ref , computed ,onMounted} from "vue"
import type { UploadProps, UploadFile } from 'element-plus'
import { UploadFilled , Close} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from "@/stores/user";
const userStore = useUserStore()
import { postUploadAPI,postUploadToPublicFromAdminAPI,source} from "@/services/upload";
import { getPublicBaseOptionAPI } from "@/services/base";
const props = defineProps<{
  base?: {
    id: string,
    name: string,
    type:string
  }
}>()
console.log(props.base);
const isUploading = ref(false)

const fileList = ref<UploadFile[]>([])
const fileSizeFormat = (size: number) => {
  if (size < 1024) return size + 'B'
  if (size < 1024 * 1024) return (size / 1024).toFixed(2) + 'KB'
  if (size < 1024 * 1024 * 1024) return (size / 1024 / 1024).toFixed(2) + 'MB'
}
const handleRemove: UploadProps['onRemove'] = (uploadFile:UploadFile, uploadFiles) => {
  console.log(uploadFile, uploadFiles)
  fileList.value = uploadFiles.filter((item:UploadFile) => item.uid !== uploadFile.uid)
}
const handlePreview: UploadProps['onPreview'] = (file:UploadFile) => {
  console.log(file)
}
const handleChange: UploadProps['onChange'] = (uploadFile) => {
  console.log(uploadFile);
  const type = uploadFile.raw!.type
  const size = uploadFile.raw!.size
  console.log(type,size);
  if (type !== 'text/plain'&& type!=='application/vnd.openxmlformats-officedocument.wordprocessingml.document' && type!=='application/pdf' ) {
    ElMessage.error('上传文件必须为DOCX/TXT格式!')
    return
  } else if ( size / 1024 / 1024 > 50) {
    ElMessage.error('文件大小不能超过50MB!')
    return
  }
  fileList.value.push(uploadFile)  
}
const options = ref<{
  value: string,
  label: string,
  type: string
}[]>()
onMounted(async () => {
  const res = await getPublicBaseOptionAPI()
  options.value = res.data.map((item: any) => {
    return {
      value: item.pid,
      label: item.name,
      type:  item.type,
    }
  })
})
const data = ref<any>({
  pid:props.base?.id,
  is_share: false,
  account: userStore.user.account,
  sid:null
})
const submit = async () => {
  console.log(data.value);
  isUploading.value = true
  let result: any
  if (userStore.user.type === 'admin' && props.base?.type === 'public') {
    result = await postUploadToPublicFromAdminAPI(data.value.pid,fileList.value[0].raw as File)
  } else {
    result = await postUploadAPI(data.value.pid, data.value.is_share, data.value.sid, fileList.value[0].raw as File)  
  }
  isUploading.value = false
  if (result.code === 200) {
    ElMessage({type: 'success',message: '上传成功,文件正在转换',duration: 2000})
  } else {
    ElMessage({type: 'error',message: '上传失败',duration: 1000})
  }
}
defineExpose({
  submit
})
</script>

<template>
    <el-upload 
      v-loading = "isUploading"
      :auto-upload="false"
      :on-change="handleChange"
      :on-preview="handlePreview" 
      action="http://bf73703.r11.cpolar.top/api/db/psl/upload"
      :data="data"
      drag 
      :limit="1"
      :show-file-list="false"
      class="md:block" hidden>
      <el-icon class="el-icon--upload"><upload-filled /></el-icon>
      <div class="md:block hidden el-upload__text">将文件拖到此处或 <em>点击上传</em></div>
      <div class="el-upload__tip">仅支持TXT/DOCX格式；单个文件最大50MB </div>
    </el-upload>
    <el-scrollbar max-height="200px" :always="true">
      <div v-for="file in fileList" class="mt-1 mr-2 h-10 px-2 rounded-md flex justify-between items-center hover:bg-slate-100">
        <span> {{ file.name }}</span>
        <span>
          <span class="mr-8">{{ fileSizeFormat(file.size!) }}</span>
            <el-link :underline="false" @click="handleRemove(file,fileList)">
              <el-icon size="20"><Close /></el-icon>
            </el-link>
          </span>
      </div>
    </el-scrollbar>
    <div 
      v-if="props.base?.type === 'personal' && fileList.length > 0"
      class="flex items-center">
      <el-text>是否将文件共享至公共库</el-text>
      <el-radio-group v-model="data.is_share" class="ml-4">
        <el-radio :value="'False'" size="large">否</el-radio>
        <el-radio :value="'True'" size="large">是</el-radio>
      </el-radio-group>
    </div>
    <el-form-item label="公共知识库名称" v-if="data.is_share === 'True'">
      <el-select
        v-model="data.sid"
        placeholder="未选择"
      >
        <el-option
          v-for="item in options"
          :key="item.value"
          :label="item.label"
          :value="item.value">
        </el-option>
      </el-select>
    </el-form-item>
</template>
<style scoped lang="scss">
.file-item{
  border-radius: 20px;
  &:hover{
    background-color: red;
  }
}
</style>