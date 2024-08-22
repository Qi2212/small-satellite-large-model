<script setup lang="ts">
import { ref, reactive,onMounted,watch } from "vue";
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from "@/stores/user";
const userStore = useUserStore();
import {
  getCheckFileListAPI,
  patchCheckFileAPI
} from "@/services/base";
const dialogVisible = ref(false);

const tableData= ref([])
const currentPage = ref(1)
const checkFileTotal = ref(0)

const getCheckFileList = async () => {
  const res = await getCheckFileListAPI(currentPage.value)
  tableData.value = res.data
  checkFileTotal.value = res.total_num
  console.log(res);
  
}
const handleCheckFile = async (operate:boolean,pid: string, fid: string) => {
    const res = await patchCheckFileAPI(operate, pid, fid)
    console.log(res);
    if (res.code === 200) {
        ElMessage({
            message: '操作成功',
            type: 'success',
            duration: 1000,
        })
        getCheckFileList()
    } else {
        ElMessage({
            message: '操作失败',
            type: 'error',
            duration: 1000,
        })
    }
}

watch(currentPage, () => {
    getCheckFileList()
})

const openCheckFileDialog = () => {
    dialogVisible.value = true
    getCheckFileList()
}

defineExpose({
    openCheckFileDialog
})
</script>

<template>
  <el-dialog
    v-model="dialogVisible"
    width="60vw"
    :z-index="100"
  >
    <template #header>
        <h2 class="text-lg font-semibold">
            审核共享文件
        </h2>
    </template>
        <div class="flex flex-col">
            <!-- <div class="flex justify-end">         
              <el-button class="w-20" type="primary" @click="uploadVisible = true;">通过</el-button>
            </div> -->
            <el-table :data="tableData" row-class-name="row" height="60vh">
              <!-- <el-table-column type="selection" /> -->
              <el-table-column label="文件名称" prop="file_name">
                 <template #default="scope">
                      <EditText :index="scope.$index" v-model:text="scope.row.file_name">
                        <el-link :href="scope.row.f_url" target="_blank" type="primary">
                            {{ scope.row.file_name }}
                        </el-link>
                      </EditText>
                    </template>
              </el-table-column> 
              <el-table-column label="状态" prop="status" width="100" align="center">
                 <template #default="scope">
                    <el-tag v-if="scope.row.status === 'pending'" round type="warning">待审核</el-tag>   
                    <el-tag v-else round>已审核</el-tag>   
                </template>
              </el-table-column> 
              <el-table-column label="申请用户" prop="username" align="center" width="120"/>
              <el-table-column label="共享至公共知识库" prop="share_collection" align="center" width="150"/>
              <el-table-column label="申请时间" prop="upload_time" align="center" width="200"/>
              <el-table-column label="审核" align="center" width="180">
              <template #default="scope">
                <template v-if="scope.row.status === 'pending'">
                    <el-button 
                        @click="handleCheckFile(true,scope.row.pid,scope.row.fid)"
                        class="w-16" type="primary" size="small">通过</el-button>
                    <el-button 
                        @click="handleCheckFile(false,scope.row.pid,scope.row.fid)"    
                        class="w-16" type="danger" size="small">拒绝</el-button>
                </template>
                <template v-else>
                    <el-tag v-if="scope.row.is_upload ==='True'" type="success">通过</el-tag>
                    <el-tag v-else type="danger">拒绝</el-tag>
                </template>
              </template>
              </el-table-column>
            </el-table>
            <div class="mt-5 flex justify-between">
                <el-text>共{{checkFileTotal}}条审核记录</el-text>
                <el-pagination
                    v-model:current-page="currentPage"
                    layout="prev, pager, next, jumper"
                    :total="checkFileTotal"
                />
            </div>
        </div>
  </el-dialog>
</template>
<style scoped lang="scss">
.icon-delete {
  &:hover {
    color: var(--el-color-error)
  }
}
</style>
