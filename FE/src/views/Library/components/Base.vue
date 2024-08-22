<script setup lang="ts">
import { ref, reactive,onMounted, watch } from "vue";
import { UploadFilled } from "@element-plus/icons-vue";
import UploadPopup from "@/components/UploadPopup.vue"
import DeleteIcon from "./icons/DeleteIcon.vue"
import BaseType from "@/components/BaseType.vue"
import { useUserStore } from "@/stores/user";
import { getPersonalFileAPI , getPublicFileAPI ,deleteFileAPI } from "@/services/base";
import { ElMessage, ElMessageBox } from 'element-plus'

const userStore = useUserStore();

const uploadVisible = ref(false);
const dialogVisible = ref(false);
// const props = defineProps<{
//   baseType: string;
// }>()
const emit = defineEmits(['close'])

const base = ref({
  id:"",
  name: "",
  type:""
});
const tableData = ref();
const currentPage = ref(1)
const fileTotal = ref(0)
const getFile = async () => {
  // tableData.value = []
  let result
  if (base.value.type == "public") {
    result = await getPublicFileAPI(currentPage.value, base.value.id)
  } else {
    result = await getPersonalFileAPI(currentPage.value, base.value.id)
  }
  console.log(result);
  tableData.value = result.data
  fileTotal.value = result.total_num
}
watch(currentPage, () => {
  getFile()
})
const openBaseDialog = (id:string,name: string,type:string) => {
  // console.log(id, name, type);
  base.value.id = id
  base.value.name = name
  base.value.type = type
  getFile()
  dialogVisible.value = true
}
defineExpose({
  openBaseDialog
})
const handleDelete = (index: number, row: any) => {
  ElMessageBox.confirm(
    '是否确认删除该文件?',
    '删除文件',
    {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning',
    }
  )
    .then(async() => {
      console.log(index, row);
      await deleteFileAPI(base.value.id, row.fid,row.type)
      ElMessage({
        type: 'success',
        message: '删除成功',
        duration: 1000,
      })
      getFile()
    })
    .catch(() => {
      // ElMessage({
      //   type: 'info',
      //   message: 'Delete canceled',
      // })
    })
};
const handleClose = () => {
  tableData.value = []
  emit('close')
  fileTotal.value = 0
};
</script>

<template>
  <el-dialog
    v-model="dialogVisible"
    @close="handleClose"
    width="60vw"
    :z-index="100"
  >
    <template #header>
        <h2 class="text-lg font-semibold">
          {{base.name}}  
          <BaseType :type="base.type"/>
        </h2>
    </template>
        <div class="flex flex-col">
            <div 
              v-if="base.type === 'personal' || base.type === 'public' && userStore.user.type==='admin'"  
              class="flex justify-end">
              <!-- <el-button class="w-20" type="danger" plain>删除文件</el-button> -->
              <el-button class="w-20" type="primary" @click="uploadVisible = true;">上传文件</el-button>
            </div>
            <el-table :data="tableData" row-class-name="row" height="60vh">
              <!-- <el-table-column 
                v-if="base.type === 'personal' || base.type === 'public' && userStore.user.type==='admin'"   
                type="selection" 
              /> -->
              <el-table-column label="文件名称" prop="file_name">
                <template #default="scope">
                  <!-- <EditText :index="scope.$index" v-model:text="scope.row.file_name">
                    <el-link :href="scope.row.f_url" target="_blank" type="primary">
                      {{ scope.row.file_name }}
                    </el-link>   
                  </EditText> -->
                  <el-link :href="scope.row.f_url" target="_blank" type="primary">
                    {{ scope.row.file_name }}
                  </el-link>   
                </template>
              </el-table-column> 
              <el-table-column v-if="base.type === 'public'" label="上传用户" prop="upload_user" width="160"/>
              <el-table-column v-if="base.type === 'personal'" label="是否共享" prop="is_share" align="center" width="100">
                <template #default="scope">
                  <template v-if="scope.row.is_share === 'True'">是</template>
                  <template v-else>否</template>
                </template>
              </el-table-column> 
              <el-table-column v-if="base.type === 'personal'"  label="共享知识库" prop="share_collection" align="center" width="200"/>
              <el-table-column label="上传时间" prop="upload_time" align="center" width="200"/>
              <el-table-column 
                v-if="base.type === 'personal' || base.type === 'public' && userStore.user.type==='admin'"   
                label="操作" align="center" width="100">
                <template #default="scope">
                    <el-link
                      :underline="false"
                      class="icon-delete"
                      @click="handleDelete(scope.$index, scope.row)"
                      >
                      <DeleteIcon />
                    </el-link>
                </template>
              </el-table-column>
            </el-table>
            <div class="mt-5 flex justify-between">
              <el-text>共{{fileTotal}}个文件</el-text>
              <el-pagination
                v-model:current-page="currentPage"
                layout="prev, pager, next, jumper"
                :total="fileTotal"
              />
            </div>
        </div>
        <upload-popup v-model:isShow="uploadVisible" :base="base"/>
  </el-dialog>
</template>
<style scoped lang="scss">
.icon-delete {
  &:hover {
    color: var(--el-color-error)
  }
}
</style>
