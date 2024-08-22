<script lang="ts" setup>
defineProps < {
    type:string
}>()
</script>
<template>
    <template v-if="type === 'personal'">
        <el-tag type="primary">个人库</el-tag>
    </template>
    <template v-else-if="type === 'public'">
        <el-tag type="warning">公共库</el-tag>
    </template>
</template>