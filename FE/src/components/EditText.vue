<script setup lang="ts">
import { ref, nextTick,watch } from 'vue'
import IconEdit from "./icons/IconEdit.vue"

const text = defineModel("text")
const isEditText = ref(false)
const emit = defineEmits(['editFinish'])
const editTextInput = ref()
const isEdit = ref(false)
watch(text, () => {
    isEdit.value = true
})
const editTextInputBlur = () => {
    if(text.value === "") return
    isEditText.value = false
    if (isEdit.value === true) {
        emit('editFinish')
    }
}

const handleEditText = async (index: any) => {
    isEditText.value = true
    await nextTick()
    editTextInput.value.focus()
}
</script>
<template>
    <div class="group flex">
        <el-input class="h-full" ref="editTextInput" @blur="editTextInputBlur" v-if="isEditText" type="text" v-model="text"/>
        <template v-else>
            <slot />
            <button 
                @click="handleEditText" class="group-hover:block hidden ml-1">
                <IconEdit />
            </button>
        </template>
    </div>
</template>