<script lang="ts" setup>
import {
  Document,
  Collection,
  List,
} from '@element-plus/icons-vue'

// 事件目前只打印日志，可根据需要扩展
function handleOpen(key: string, keyPath: string[]) {
  console.log('open', key, keyPath)
}
function handleClose(key: string, keyPath: string[]) {
  console.log('close', key, keyPath)
}
</script>

<template>
  <el-menu
    router
    default-active="/"
    class="el-menu-vertical-demo"
    @open="handleOpen"
    @close="handleClose"
  >
    <!-- 项目管理 -->
    <el-menu-item index="/">
      <el-icon>
        <Collection />
      </el-icon>
      <template #title>
        项目管理
      </template>
    </el-menu-item>

    <!-- 提示词列表 -->
    <el-menu-item index="/prompts">
      <el-icon>
        <List />
      </el-icon>
      <template #title>
        提示词列表
      </template>
    </el-menu-item>

    <!-- 项目介绍 -->
    <el-menu-item index="/projects/intro">
      <el-icon>
        <Document />
      </el-icon>
      <template #title>
        项目介绍
      </template>
    </el-menu-item>
  </el-menu>
</template>