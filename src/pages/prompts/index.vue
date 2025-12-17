<script setup lang="ts">
import { ref } from 'vue'   // ← 补这一行

interface PromptItem {
  id: number
  name: string
  scene: string
  content: string
  updatedAt: string
}

const prompts = ref<PromptItem[]>([
  {
    id: 1,
    name: '生成接口文档',
    scene: '后端接口说明',
    content: '请基于以下代码生成接口文档，包含请求参数、响应结构和错误码说明：',
    updatedAt: '2025-12-10 12:00:00',
  },
])
</script>

<template>
  <div class="h-full flex flex-col px-6 py-4">
    <div class="flex items-center justify-between mb-4">
      <div>
        <h2 class="text-2xl font-semibold mb-1">
          提示词列表
        </h2>
        <p class="text-gray-500 text-sm">
          管理日常使用的通用提示词（新增 / 修改 / 删除）
        </p>
      </div>
      <el-button type="primary">
        新增提示词（预留）
      </el-button>
    </div>

    <el-card class="flex-1" shadow="never">
      <el-table :data="prompts" border>
        <el-table-column prop="name" label="名称" min-width="160" />
        <el-table-column prop="scene" label="场景" min-width="160" />
        <el-table-column prop="content" label="内容" min-width="260">
          <template #default="{ row }">
            <span class="truncate block" :title="row.content">
              {{ row.content }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="updatedAt" label="更新时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small">
              编辑
            </el-button>
            <el-button link type="danger" size="small">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>