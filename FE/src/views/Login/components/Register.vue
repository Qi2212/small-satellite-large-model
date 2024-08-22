<script setup lang="ts">
import { ref } from 'vue'
import { useChatStore } from '@/stores/chat';
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { UploadProps } from 'element-plus'
import { postRegister } from '@/services/user';

const chatStore = useChatStore();
const router = useRouter()

const registerData = ref({
  account: '',
  username:'',
  password1: '',
  password2: '',
})

const imageUrl = ref('')
const beforeAvatarUpload: UploadProps['beforeUpload'] = (rawFile) => {
  //文件类型及文件大小校验
//   if (rawFile.type !== 'image/jpeg') {
//     ElMessage.error('Avatar picture must be JPG format!')
//     return false
//   } else if (rawFile.size / 1024 / 1024 > 2) {
//     ElMessage.error('Avatar picture size can not exceed 2MB!')
//     return false
//   }
  return true
}
const upload:UploadProps['onChange'] = (uploadFile) => {
  imageUrl.value = URL.createObjectURL(uploadFile.raw!)
  console.log(imageUrl.value);
}
const status = defineModel('status')
const register = async () => {
  const result = await postRegister(
    registerData.value.account,
    registerData.value.username,
    registerData.value.password1,
    registerData.value.password2
  )
  console.log(result);
  if (result.code == 200) {
    ElMessage({
      type: 'success',
      message: '注册成功',
      duration:1000
    })
    status.value = 'login'
  }
  
}
</script>
<template>
    <!-- <el-upload
        class="avatar-uploader"
        :show-file-list="false"
        :auto-upload="false"
        :before-upload="beforeAvatarUpload"
        :on-change="upload"
    >
        <img v-if="imageUrl" :src="imageUrl" class="avatar" />
        <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
    </el-upload> -->
    <span class="flex justify-between w-full">
      <el-link class="text-xs decoration-slice" @click="status = 'login'" type="primary"> 
        << 返回
      </el-link>
      <span></span>
    </span>
    <el-form label-width="auto" label-position="left" class="w-full">
      <el-form-item label="账号" class="w-full">
      <el-input v-model="registerData.account" placeholder="请输入手机号" />
      </el-form-item>
      <el-form-item label="用户名" class="w-full">
        <el-input v-model="registerData.username" placeholder="请输入用户名" />
      </el-form-item>
      <el-form-item label="设置密码" class="w-full">
        <el-input v-model="registerData.password1" placeholder="请输入登录密码" />
      </el-form-item>
      <el-form-item label="确认密码" class="w-full">
        <el-input v-model="registerData.password2" placeholder="请再次输入登录密码" />
      </el-form-item>
    </el-form>
    <div>
      <el-button 
        :disabled="!registerData.username || !registerData.account || !registerData.password1 || !registerData.password2"
        round color="#01358e" size="large" 
        @click="register">
        <span class="px-4 text-md">注册</span>
      </el-button>
    </div>
</template>
<style>
.avatar-uploader .el-upload {
  border: 1px dashed var(--el-border-color);
  border-radius: 50%;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: var(--el-transition-duration-fast);
}

.avatar-uploader .el-upload:hover {
  border-color: var(--el-color-primary);
}

.el-icon.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 100px;
  height: 100px;
  text-align: center;
  border-radius: 50%;
}

.avatar-uploader .avatar {
  width: 100px;
  height: 100px;
  display: block;
}
</style>