<script setup lang="ts">
import { ref } from 'vue'   // ← 补这一行

const content = ref<string>(`# Code Assistant 项目介绍

这里可以放本项目的使用方式、架构说明、目录结构说明等。
未来可以从本地 README.md 自动加载。`)
</script>

<template>
  <div class="h-full flex flex-col px-6 py-4">
    <div class="flex items-center justify-between mb-4">
      <div>
        <h2 class="text-2xl font-semibold mb-1">
          项目介绍
        </h2>
        <p class="text-gray-500 text-sm">
          维护本工具自身的说明文档，后续可从 README.md 自动同步
        </p>
      </div>
    </div>

    <el-card class="flex-1 flex flex-col" shadow="never">
      <template #header>
        <span>项目说明（Markdown 文本占位）</span>
      </template>

      <el-input
        v-model="content"
        type="textarea"
        :rows="20"
        class="flex-1"
        resize="none"
      />
    </el-card>
  </div>
</template>