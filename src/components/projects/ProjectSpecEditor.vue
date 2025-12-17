<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  content: string
  saving: boolean
}>()

const emit = defineEmits<{
  (e: 'update:content', content: string): void
  (e: 'generate'): void
  (e: 'save'): void
}>()

const localContent = ref(props.content)

watch(
  () => props.content,
  (val) => {
    localContent.value = val
  },
)

watch(
  () => localContent.value,
  (val) => {
    emit('update:content', val)
  },
)
</script>

<template>
  <el-card class="flex-1 flex flex-col" shadow="never">
    <template #header>
      <div class="flex items-center justify-between">
        <span>整理文档 / Spec</span>
        <div class="space-x-2">
          <el-button size="small" @click="emit('generate')">
            生成 Spec（预留）
          </el-button>
          <el-button
            size="small"
            type="primary"
            :loading="props.saving"
            @click="emit('save')"
          >
            保存 Spec
          </el-button>
        </div>
      </div>
    </template>

    <el-input
      v-model="localContent"
      type="textarea"
      :rows="10"
      class="flex-1"
      resize="none"
    />
  </el-card>
</template>