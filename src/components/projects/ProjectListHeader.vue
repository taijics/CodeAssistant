<script setup lang="ts">
interface Props {
  totalProjects: number
  totalFiles: number
  totalModifyCount: number
}
const props = defineProps<Props>()
</script>

<template>
  <div>
    <!-- 顶部标题与操作说明交给父组件控制按钮 -->
    <div class="flex items-center justify-between mb-4">
      <div>
        <h2 class="text-2xl font-semibold mb-1">
          项目管理
        </h2>
        <p class="text-gray-500 text-sm">
          管理本地项目，统计文件信息，为后续 LLM 分析做准备
        </p>
      </div>
      <slot name="actions" />
    </div>

    <!-- 概览统计 -->
    <el-row :gutter="16" class="mb-4">
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="flex items-center justify-between">
            <div>
              <div class="text-gray-500 text-xs mb-1">
                项目总数
              </div>
              <div class="text-2xl font-bold">
                {{ props.totalProjects }}
              </div>
            </div>
            <i class="i-ep-document text-3xl text-teal-500" />
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="flex items-center justify-between">
            <div>
              <div class="text-gray-500 text-xs mb-1">
                总文件数（统计）
              </div>
              <div class="text-2xl font-bold">
                {{ props.totalFiles }}
              </div>
            </div>
            <i class="i-ep-folder-opened text-3xl text-indigo-500" />
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="flex items-center justify-between">
            <div>
              <div class="text-gray-500 text-xs mb-1">
                修改次数（累计）
              </div>
              <div class="text-2xl font-bold">
                {{ props.totalModifyCount }}
              </div>
            </div>
            <i class="i-ep-edit-pen text-3xl text-amber-500" />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>