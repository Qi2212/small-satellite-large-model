<script setup lang="ts">
import Header from './header/Header.vue'
import Menu from './menu/Menu.vue';
import Main from "./main/Main.vue"
import { RouterView } from 'vue-router';
</script>
<template>
    <Header />
    <Menu />
    <Main />
</template>
<style scoped>
</style>