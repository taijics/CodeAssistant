<script setup lang="ts">
const props = defineProps<{
  filePath: string
  content: string
}>()
</script>

<template>
  <el-card class="flex-1 flex flex-col" shadow="never">
    <template #header>
      <div class="flex items-center justify-between">
        <span>文件内容</span>
        <span class="text-xs text-gray-500">
          {{ props.filePath || '未选择文件' }}
        </span>
      </div>
    </template>

    <div class="flex-1 overflow-auto bg-gray-900 text-gray-100 rounded text-left p-3 text-xs font-mono">
      <pre class="whitespace-pre-wrap"><code>{{ props.content }}</code></pre>
    </div>
  </el-card>
</template>