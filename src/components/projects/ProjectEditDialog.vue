<script setup lang="ts">
import { ref, watch } from 'vue'

interface Project {
  id: number
  name: string
  rootPath: string
  description: string
  feArch: string
  serverArch: string
  adminArch: string
}

const props = defineProps<{
  modelValue: boolean
  loading: boolean
  project: Project
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', v: boolean): void
  (e: 'submit', project: Project): void
}>()

const form = ref<Project>({ ...props.project })

watch(
  () => props.project,
  (val) => {
    form.value = { ...val }
  },
  { deep: true },
)

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
    title="编辑项目"
    width="640px"
    destroy-on-close
    @close="handleClose"
  >
    <el-form
      :model="form"
      label-width="100px"
      label-position="right"
    >
      <el-form-item label="名称">
        <el-input v-model="form.name" placeholder="请输入项目名称" />
      </el-form-item>

      <el-form-item label="本地地址">
        <el-input v-model="form.rootPath" placeholder="请输入项目根路径（绝对路径）" />
      </el-form-item>

      <el-form-item label="功能简介">
        <el-input
          v-model="form.description"
          type="textarea"
          :rows="2"
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

<style scoped>
</style>