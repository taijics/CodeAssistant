<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  modelValue: boolean
  loading: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', v: boolean): void
  (e: 'submit', payload: {
    name: string
    rootPath: string
    frontendPath: string
    serverPath: string
    adminPath: string
    description: string
    feArch: string
    serverArch: string
    adminArch: string
  }): void
}>()

const form = ref({
  name: '',
  rootPath: '',
  frontendPath: '',
  serverPath: '',
  adminPath: '',
  description: '',
  feArch: '',
  serverArch: '',
  adminArch: '',
})

const rules = {
  name: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
  rootPath: [{ required: true, message: '请输入项目根路径（绝对路径）', trigger: 'blur' }],
  // 三个子路径可以暂时不必强制必填，看你实际需要
}

function handleClose() {
  emit('update:modelValue', false)
}

function handleSubmit() {
  emit('submit', { ...form.value })
}
</script>

<template>
  <el-dialog
    :model-value="props.modelValue"
    title="新增项目"
    width="720px"
    destroy-on-close
    @close="handleClose"
  >
    <el-form
      :model="form"
      :rules="rules"
      label-width="110px"
      label-position="right"
    >
      <el-form-item label="项目名称" prop="name">
        <el-input v-model="form.name" placeholder="请输入项目名称" />
      </el-form-item>

      <el-form-item label="项目根目录" prop="rootPath">
        <el-input
          v-model="form.rootPath"
          placeholder="如：/Users/you/code/project-a"
        />
        <!-- 将来可以加一个按钮，触发系统选择目录 -->
        <!-- <el-button class="ml-2" @click="selectRootPath">选择目录</el-button> -->
      </el-form-item>

      <el-form-item label="用户前端目录">
        <el-input
          v-model="form.frontendPath"
          placeholder="如：/Users/you/code/project-a/apps/web"
        />
      </el-form-item>

      <el-form-item label="Server 端目录">
        <el-input
          v-model="form.serverPath"
          placeholder="如：/Users/you/code/project-a/apps/server"
        />
      </el-form-item>

      <el-form-item label="管理端前端目录">
        <el-input
          v-model="form.adminPath"
          placeholder="如：/Users/you/code/project-a/apps/admin"
        />
      </el-form-item>

      <el-form-item label="功能简介">
        <el-input
          v-model="form.description"
          type="textarea"
          :rows="2"
          placeholder="简要说明项目的主要功能"
        />
      </el-form-item>

      <el-form-item label="前端架构说明">
        <el-input
          v-model="form.feArch"
          type="textarea"
          :rows="2"
        />
      </el-form-item>

      <el-form-item label="Server 架构说明">
        <el-input
          v-model="form.serverArch"
          type="textarea"
          :rows="2"
        />
      </el-form-item>

      <el-form-item label="管理端架构说明">
        <el-input
          v-model="form.adminArch"
          type="textarea"
          :rows="2"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="handleClose">
        取 消
      </el-button>
      <el-button type="primary" :loading="props.loading" @click="handleSubmit">
        保 存
      </el-button>
    </template>
  </el-dialog>
</template>