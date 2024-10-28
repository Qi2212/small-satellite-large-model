<script setup lang="ts">
import { ref, reactive } from "vue";
import { useUserStore } from "@/stores/user";
const userStore = useUserStore();
import { ElMessage, ElMessageBox } from 'element-plus'
// import { UploadFilled } from "@element-plus/icons-vue";
// import Upload from "@/components/Upload.vue"
import {
  postCreatePersonalBaseAPI,
  postCreatePublicBaseAPI,
} from "@/services/base";
import BaseType from "@/components/BaseType.vue";

// const uploadVisible = ref(false);
const dialogVisible = ref(false);

const emit = defineEmits(['created']);

const base = reactive({
  name: "",
  synopsis: "",
  type: "personal",
});
const createBase = async () => {
  let result
  if (userStore.user.type === 'normal') {
    result = await postCreatePersonalBaseAPI(base.name, base.synopsis)
  }
  else if (userStore.user.type === 'admin') {
    if (base.type === 'public') {
      result = await postCreatePublicBaseAPI(base.name, base.synopsis)
    } else if (base.type === 'personal') {
      result = await postCreatePersonalBaseAPI(base.name, base.synopsis)
    }
  }
  // console.log(result);
  if (result.code === 200) {
    dialogVisible.value = false
    ElMessage({
      message: '创建成功',
      type: 'success'
    })
    emit('created')
  } else {
    ElMessage({
      message: `创建失败,${result.msg}`,
      type: 'error'
    })
  }
}

const options = [
  {
    value: 'personal',
    label: '个人库',
  },
  {
    value: 'public',
    label: '公共库',
  },
]

const openCreateBaseDialog = () => {
  dialogVisible.value = true
}
defineExpose({
  openCreateBaseDialog
})
const handleClose = () => {
  base.name = ""
  base.synopsis = "",
  base.type = "personal"
}
</script>

<template>
  <el-dialog
    v-model="dialogVisible"
    width="40vw"
    :z-index="100"
    @close="handleClose"
  >
    <template #header>
        <h2 class="text-lg font-semibold">
            创建知识库
            <BaseType :type="base.type" />
        </h2>
    </template>
    <el-form-item 
      v-if="userStore.user.type==='admin'"
      label="知识库类型"
    >
      <el-select
        v-model="base.type"
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
    <el-form-item label="知识库名称">
      <el-input v-model="base.name" placeholder="请输入知识库名称"/>
    </el-form-item>
    <el-form-item label="知识库简介">
      <el-input
        v-model="base.synopsis"
        :rows="8"
        resize="none"
        type="textarea"
        maxlength="200"
        show-word-limit
        placeholder="请输入知识库简介"
      />
    </el-form-item>
    <!-- <Upload/> -->
    <template #footer>
        <el-button type="primary" @click="createBase">创建</el-button>
    </template>
  </el-dialog>
</template>
