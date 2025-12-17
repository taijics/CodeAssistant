<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import ProjectListHeader from '~/components/projects/ProjectListHeader.vue'
import ProjectTable from '~/components/projects/ProjectTable.vue'
import ProjectCreateDialog from '~/components/projects/ProjectCreateDialog.vue'
import ProjectEditDialog from '~/components/projects/ProjectEditDialog.vue'

interface Project {
  id: number
  name: string
  // 原 rootPath 你可以保留为“项目根目录”
  rootPath: string
  // 新增三个子目录字段
  frontendPath: string
  serverPath: string
  adminPath: string

  description: string
  createdAt: string
  totalFiles: number
  modifyCount: number
  frontendFiles: number
  serverFiles: number
  adminFiles: number
  feArch: string
  serverArch: string
  adminArch: string
}

const router = useRouter()

const projects = ref<Project[]>([
  {
    id: 1,
    name: '示例项目 A',
    rootPath: '/Users/taiji/code/project-a',
    frontendPath: '/Users/taiji/code/project-a/apps/web',
    serverPath: '/Users/taiji/code/project-a/apps/server',
    adminPath: '/Users/taiji/code/project-a/apps/admin',
    description: '一个演示性质的电商项目',
    createdAt: '2025-12-01 10:20:00',
    totalFiles: 320,
    modifyCount: 5,
    frontendFiles: 120,
    serverFiles: 150,
    adminFiles: 50,
    feArch: 'Vue3 + Element Plus + Vite',
    serverArch: 'NestJS + PostgreSQL',
    adminArch: 'Vue3 + Element Plus',
  },
])

const totalProjects = computed(() => projects.value.length)
const totalFiles = computed(() =>
  projects.value.reduce((sum, p) => sum + p.totalFiles, 0),
)
const totalModifyCount = computed(() =>
  projects.value.reduce((sum, p) => sum + p.modifyCount, 0),
)

// 新增
const createDialogVisible = ref(false)
const createProjectLoading = ref(false)

function handleCreate(payload: {
  name: string
  rootPath: string
  frontendPath: string
  serverPath: string
  adminPath: string
  description: string
  feArch: string
  serverArch: string
  adminArch: string
}) {
  createProjectLoading.value = true
  const now = new Date()
  const id = Date.now()

  projects.value.unshift({
    id,
    name: payload.name,
    rootPath: payload.rootPath,
    frontendPath: payload.frontendPath,
    serverPath: payload.serverPath,
    adminPath: payload.adminPath,
    description: payload.description,
    createdAt: now.toISOString().slice(0, 19).replace('T', ' '),
    totalFiles: 0,
    modifyCount: 0,
    frontendFiles: 0,
    serverFiles: 0,
    adminFiles: 0,
    feArch: payload.feArch,
    serverArch: payload.serverArch,
    adminArch: payload.adminArch,
  })

  setTimeout(() => {
    createProjectLoading.value = false
    createDialogVisible.value = false
  }, 200)
}

// 编辑
const editDialogVisible = ref(false)
const editingProject = ref<Project | null>(null)
const editProjectLoading = ref(false)

function handleOpenEdit(row: Project) {
  editingProject.value = { ...row }
  editDialogVisible.value = true
}

function handleUpdate(project: Project) {
  editProjectLoading.value = true
  const index = projects.value.findIndex(p => p.id === project.id)
  if (index !== -1)
    projects.value[index] = { ...projects.value[index], ...project }

  setTimeout(() => {
    editProjectLoading.value = false
    editDialogVisible.value = false
  }, 200)
}

// 跳详情
function handleDetail(row: Project) {
  router.push('/projects/detail')
}

// 删除先占位
function handleDelete(row: Project) {
  console.log('delete project', row)
}
</script>

<template>
  <div class="page-projects h-full flex flex-col px-6 py-4">
    <ProjectListHeader
      :total-projects="totalProjects"
      :total-files="totalFiles"
      :total-modify-count="totalModifyCount"
    >
      <template #actions>
        <el-button type="primary" @click="createDialogVisible = true">
          新增项目
        </el-button>
      </template>
    </ProjectListHeader>

    <ProjectTable
      :projects="projects"
      @detail="handleDetail"
      @edit="handleOpenEdit"
      @delete="handleDelete"
    />

    <ProjectCreateDialog
      v-model="createDialogVisible"
      :loading="createProjectLoading"
      @submit="handleCreate"
    />

    <ProjectEditDialog
      v-if="editingProject"
      v-model="editDialogVisible"
      :project="editingProject"
      :loading="editProjectLoading"
      @submit="handleUpdate"
    />
  </div>
</template>

<style scoped>
.page-projects {
  background-color: var(--ep-bg-color-page);
}
</style>