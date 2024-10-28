<script setup lang="ts">
import { ref } from 'vue'
import { useChatStore } from '@/stores/chat';
const chatStore = useChatStore();
import { useUserStore } from '@/stores/user';
const userStore = useUserStore();
import { useRouter } from 'vue-router'
import { postLogin } from '@/services/user';
import { ElMessage } from 'element-plus'

const router = useRouter()

const status = defineModel('status')

const loginData = ref({
    account: '',
    password: ''
})
const login = async () => {
    const result = await postLogin(loginData.value.account,loginData.value.password)
    // console.log(result);
    if (result.code === 200) {
        userStore.setUser(
            result.account,
            result.username,
            result.type
        )
        // console.log(userStore.user);
        ElMessage({
            type: 'success',
            message: '登录成功',
            duration: 1000
        })
        setTimeout(() => {
            router.push('/index')
        }, 1000)
    } else {
        ElMessage({
            type: 'error',
            message: '账号或密码错误，请重新输入！'
        })
    }
}
</script>
<template>
    <span class="text-2xl pb-4">欢迎使用{{ chatStore.title }}</span>
    <el-form class="w-full">
        <el-form-item label="账号" class="w-full">
        <el-input v-model="loginData.account" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="密码" class="w-full">
        <el-input v-model="loginData.password" type="password" placeholder="请输入登录密码" />
        </el-form-item>
    </el-form>
    <div class="flex justify-between w-full mb-4">
        <el-link class="text-xs" @click="status = 'register'">注册账号</el-link>
        <el-link class="text-xs">忘记密码？</el-link>
    </div>
    <el-button 
        :disabled="!loginData.account || !loginData.password" round color="#01358e" size="large" @click="login">
        <span class="px-4 text-md">登录</span>
    </el-button>
</template>

<style scoped lang='scss'>
.el-form-item__label{
    font-size: 30px;
}

</style>