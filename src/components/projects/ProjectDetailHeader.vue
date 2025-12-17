<script setup lang="ts">
interface Props {
  name: string
  rootPath: string
}
const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'search'): void
}>()
</script>

<template>
  <div class="flex items-center justify-between mb-4">
    <div>
      <h2 class="text-2xl font-semibold mb-1">
        {{ props.name }}
      </h2>
      <p class="text-gray-500 text-xs">
        根路径：{{ props.rootPath }}
      </p>
    </div>
    <el-button type="primary" @click="emit('search')">
      搜索项目
    </el-button>
  </div>
</template>