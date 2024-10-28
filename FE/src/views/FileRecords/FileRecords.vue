<script setup lang="ts">
import { ref, reactive,onMounted,nextTick,watch } from "vue";
import { useUserStore } from "@/stores/user";
const userStore = useUserStore();
import { ElMessage, ElMessageBox } from 'element-plus'
import BaseType from "@/components/BaseType.vue"
import { getAllFileRecordsAPI ,getAdminFileRecordsAPI} from "@/services/base";

const tableData = ref();
const currentPage = ref(1)
const baseTotal = ref(0)
const getFileRecords = async () => {
  let result
  if (userStore.user.type === 'normal') {
    result = await getAllFileRecordsAPI(currentPage.value)
  } else {
    result = await getAdminFileRecordsAPI(currentPage.value)
  }
  console.log(result);
  let interval
  if (result.transforming === 'True') {
    interval = setTimeout(() => {
      getFileRecords()
    }, 10000);
  } else {
    interval = null
  }
  tableData.value = result.data
  baseTotal.value = result.total_num
}
onMounted(() => {
  getFileRecords()
})
watch(currentPage, () => {
  getFileRecords()
})
</script>

<template>
  <div class="library w-[90vw] md:w-[60vw] mx-auto">
    <div class="flex flex-col my-5">
        <h2 class="text-lg font-semibold my-3">文件记录</h2>
    </div>
      <div class="flex flex-col p-5 bg-white rounded-xl shadow-xl">
        <el-table :data="tableData" row-class-name="row" height="66vh">
          <el-table-column label="文件名称" prop="file_name">
            <template #default="scope">
              <el-link v-if="scope.row.status === 'success'" :href="scope.row.f_url" target="_blank" type="primary">
                {{ scope.row.file_name }}
              </el-link>
              <el-text v-else>{{ scope.row.file_name }}</el-text>
            </template>
          </el-table-column>
          <el-table-column label="归属知识库" prop="name" width="150"/>
          <el-table-column 
            v-if="userStore.user.type === 'admin'" 
            label="知识库类型" prop="type" align="center" width="100">
            <template #default="scope">
              <BaseType :type="scope.row.type" />
            </template>
          </el-table-column>
          <el-table-column label="是否共享" prop="is_share" align="center" width="80">
            <template #default="scope">
              <template v-if="scope.row.is_share === 'True'">是</template>
              <template v-else-if="scope.row.is_share === 'False'">否</template>
            </template>
          </el-table-column>
          <el-table-column label="共享知识库" prop="share_collection" width="150">
            <template #default="scope">
              {{ scope.row.share_collection === 'Unknow' ? '无': scope.row.share_collection}}
            </template>
          </el-table-column>
          <el-table-column label="结果" prop="status" align="center" width="100">
            <template #default="scope">
              <el-tag v-if="scope.row.status === 'success'" type="success">入库成功</el-tag>
              <el-tag v-else-if="scope.row.status === 'failure'" type="danger">入库失败</el-tag>
              <el-tag v-else-if="scope.row.status === 'false'" type="info">已删除</el-tag>
              <el-tag v-else type="warning">转换中</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="上传时间" prop="upload_time" width="180"/>
        </el-table>
        <div class="mt-5 flex justify-between">
          <el-text>共{{baseTotal}}条文件记录</el-text>
          <el-pagination
            v-model:current-page="currentPage"
            layout="prev, pager, next, jumper"
            :total="baseTotal"
          />
        </div>
      </div>
  </div>
</template>
<style lang="scss">
.el-table .row {
  height: 50px;
}
</style>