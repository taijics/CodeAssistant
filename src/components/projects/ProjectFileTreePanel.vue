<script setup lang="ts">
import { ref } from 'vue'
import type { ElTree } from 'element-plus'

interface FileNode {
  id: string
  name: string
  path: string
  type: 'file' | 'dir'
  children?: FileNode[]
}

const props = defineProps<{
  data: FileNode[]
}>()

const emit = defineEmits<{
  (e: 'select-file', node: FileNode): void
}>()

const treeRef = ref<InstanceType<typeof ElTree>>()

function handleNodeClick(node: FileNode) {
  if (node.type === 'dir')
    return
  emit('select-file', node)
}
</script>
<template>
  <el-card class="w-1/3 flex flex-col" shadow="never">
    <template #header>
      <span>项目文件</span>
    </template>

    <div class="flex-1 overflow-auto">
      <el-tree
        ref="treeRef"
        :data="props.data"
        node-key="id"
        default-expand-all
        highlight-current
        :props="{ label: 'name', children: 'children' }"
        @node-click="handleNodeClick"
      >
        <template #default="{ data }">
          <span class="flex items-center">
            <i
              v-if="data.type === 'dir'"
              class="i-ep-folder mr-1 text-amber-500"
            />
            <i
              v-else
              class="i-ep-document mr-1 text-gray-500"
            />
            <span>{{ data.name }}</span>
          </span>
        </template>
      </el-tree>
    </div>
  </el-card>
</template>