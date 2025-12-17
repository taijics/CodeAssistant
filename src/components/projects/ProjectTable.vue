<script setup lang="ts">
interface Project {
  id: number
  name: string
  rootPath: string
  description: string
  createdAt: string
  totalFiles: number
  modifyCount: number
}

const props = defineProps<{
  projects: Project[]
}>()

const emit = defineEmits<{
  (e: 'detail', row: Project): void
  (e: 'edit', row: Project): void
  (e: 'delete', row: Project): void
}>()
</script>

<template>
  <el-card class="flex-1 overflow-hidden" shadow="never">
    <template #header>
      <div class="flex items-center justify-between">
        <span>项目列表</span>
      </div>
    </template>

    <el-table
      :data="props.projects"
      border
      height="100%"
      header-cell-class-name="text-xs"
    >
      <el-table-column prop="name" label="项目名称" min-width="160">
        <template #default="{ row }">
          <el-link
            type="primary"
            @click="emit('detail', row)"
          >
            {{ row.name }}
          </el-link>
        </template>
      </el-table-column>

      <el-table-column prop="rootPath" label="根路径" min-width="220" />

      <el-table-column prop="description" label="简介" min-width="200">
        <template #default="{ row }">
          <span class="truncate block" :title="row.description">
            {{ row.description || '-' }}
          </span>
        </template>
      </el-table-column>

      <el-table-column prop="totalFiles" label="总文件数" width="100" align="center" />
      <el-table-column prop="modifyCount" label="修改次数" width="100" align="center" />
      <el-table-column prop="createdAt" label="创建时间" width="180" />

      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" size="small" @click="emit('detail', row)">
            详情
          </el-button>
          <el-button
            link
            type="info"
            size="small"
            @click="emit('edit', row)"
          >
            编辑
          </el-button>
          <el-button link type="danger" size="small" @click="emit('delete', row)">
            删除（预留）
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>