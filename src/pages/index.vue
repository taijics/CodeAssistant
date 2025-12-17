<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import ProjectListHeader from '~/components/projects/ProjectListHeader.vue'
import ProjectTable from '~/components/projects/ProjectTable.vue'
import ProjectCreateDialog from '~/components/projects/ProjectCreateDialog.vue'
import ProjectEditDialog from '~/components/projects/ProjectEditDialog.vue'

// 引入我们刚建的 api
import {
  fetchProjects,
  createProject,
  updateProject,
  deleteProject,
  type Project,
  type ProjectPayload,
} from '~/api/project'

const router = useRouter()

const projects = ref<Project[]>([])

// 统计信息
const totalProjects = computed(() => projects.value.length)
const totalFiles = computed(() =>
  projects.value.reduce((sum, p) => sum + p.totalFiles, 0),
)
const totalModifyCount = computed(() =>
  projects.value.reduce((sum, p) => sum + p.modifyCount, 0),
)

// ========== 加载列表 ==========
const listLoading = ref(false)

async function loadProjects() {
  try {
    listLoading.value = true
    projects.value = await fetchProjects()
  } catch (e) {
    console.error('加载项目列表失败', e)
  } finally {
    listLoading.value = false
  }
}

onMounted(() => {
  loadProjects()
})

// ========== 新增 ==========
const createDialogVisible = ref(false)
const createProjectLoading = ref(false)

async function handleCreate(payload: {
  name: string
  rootPath: string
  frontendPath?: string
  serverPath?: string
  adminPath?: string
  description?: string
  feArch?: string
  serverArch?: string
  adminArch?: string
}) {
  try {
    createProjectLoading.value = true

    const body: ProjectPayload = {
      name: payload.name,
      rootPath: payload.rootPath,
      frontendPath: payload.frontendPath,
      serverPath: payload.serverPath,
      adminPath: payload.adminPath,
      description: payload.description,
      feArch: payload.feArch,
      serverArch: payload.serverArch,
      adminArch: payload.adminArch,
    }

    const created = await createProject(body)
    // 加到列表最前面
    projects.value.unshift(created)
    createDialogVisible.value = false
  } catch (e) {
    console.error('创建项目失败', e)
  } finally {
    createProjectLoading.value = false
  }
}

// ========== 编辑 ==========
const editDialogVisible = ref(false)
const editingProject = ref<Project | null>(null)
const editProjectLoading = ref(false)

function handleOpenEdit(row: Project) {
  editingProject.value = { ...row }
  editDialogVisible.value = true
}

async function handleUpdate(project: Project) {
  if (!project.id)
    return

  try {
    editProjectLoading.value = true

    const payload: ProjectPayload = {
      name: project.name,
      rootPath: project.rootPath,
      frontendPath: project.frontendPath ?? undefined,
      serverPath: project.serverPath ?? undefined,
      adminPath: project.adminPath ?? undefined,
      description: project.description ?? undefined,
      feArch: project.feArch ?? undefined,
      serverArch: project.serverArch ?? undefined,
      adminArch: project.adminArch ?? undefined,
    }

    const updated = await updateProject(project.id, payload)

    const index = projects.value.findIndex(p => p.id === updated.id)
    if (index !== -1)
      projects.value[index] = updated

    editDialogVisible.value = false
  } catch (e) {
    console.error('更新项目失败', e)
  } finally {
    editProjectLoading.value = false
  }
}

// ========== 跳详情 ==========
function handleDetail(row: Project) {
  router.push(`/projects/detail/${row.id}`)
}

// ========== 删除（现在可以真正调后端了） ==========
const deleteLoading = ref(false)

async function handleDelete(row: Project) {
  if (!row.id)
    return

  try {
    deleteLoading.value = true
    await deleteProject(row.id)
    projects.value = projects.value.filter(p => p.id !== row.id)
  } catch (e) {
    console.error('删除项目失败', e)
  } finally {
    deleteLoading.value = false
  }
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