<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

import ProjectDetailHeader from '~/components/projects/ProjectDetailHeader.vue'
import ProjectInfoCard from '~/components/projects/ProjectInfoCard.vue'
import ProjectFileTreePanel from '~/components/projects/ProjectFileTreePanel.vue'
import ProjectFileViewer from '~/components/projects/ProjectFileViewer.vue'
import ProjectSearchResultPanel from '~/components/projects/ProjectSearchResultPanel.vue'
import ProjectSpecEditor from '~/components/projects/ProjectSpecEditor.vue'

import { fetchProjectFileTree, fetchFileContent, scanProjectFiles, type FileNodeDto } from '~/api/files'

const route = useRoute()
const projectId = Number(route.params.id ?? 0)

interface ProjectDetail {
  id: number
  name: string
  rootPath: string
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

// ========== 项目信息（暂时还是 mock） ==========
const project = ref<ProjectDetail>({
  id: projectId || 1,
  name: '示例项目 A',
  rootPath: '/Users/taiji/code/project-a',
  description: '一个演示性质的电商项目',
  createdAt: '2025-12-01 10:20:00',
  totalFiles: 320,
  modifyCount: 5,
  frontendFiles: 120,
  serverFiles: 150,
  adminFiles: 50,
  feArch: 'Vue3 + Vite + Element Plus，模块划分为 user / order / product / report',
  serverArch: 'NestJS 分层架构（controller + service + repository），采用 CQRS，PostgreSQL 数据库',
  adminArch: 'Vue3 + Element Plus，采用多标签页布局，权限基于 RBAC 实现',
})

const saveInfoLoading = ref(false)

function handleSaveProjectInfo() {
  // TODO: 后面接 PUT /api/projects/{id}
  saveInfoLoading.value = true
  setTimeout(() => {
    saveInfoLoading.value = false
  }, 600)
}

// 接收 ProjectInfoCard 的 v-model 更新
function handleUpdateProject(updated: ProjectDetail) {
  project.value = { ...project.value, ...updated }
}

// ========== 文件树（真实接口） ==========
const fileTreeData = ref<FileNodeDto[]>([])
const treeLoading = ref(false)

async function loadFileTree() {
  if (!projectId) return
  try {
    treeLoading.value = true
    fileTreeData.value = await fetchProjectFileTree(projectId)
  } catch (e) {
    console.error('加载文件树失败', e)
  } finally {
    treeLoading.value = false
  }
}

// 进入详情页时：先扫描一次，再加载树
onMounted(async () => {
  if (!projectId) return
  try {
    await scanProjectFiles(projectId)
  } catch (e) {
    console.error('扫描项目文件失败', e)
  }
  await loadFileTree()
})

const currentFilePath = ref<string>('')
const currentFileContent = ref<string>('请选择左侧文件查看内容')

async function handleSelectFile(node: FileNodeDto) {
  currentFilePath.value = node.path
  try {
    currentFileContent.value = await fetchFileContent(projectId, node.path)
  } catch (e) {
    console.error('加载文件内容失败', e)
    currentFileContent.value = `// 读取文件失败：${node.path}\n${String(e)}`
  }
}

// ========== 搜索 & 结果（暂时还是 mock） ==========
type SearchResultType = 'entity' | 'service' | 'controller' | 'page' | 'sql' | 'other'

interface SearchResultItem {
  id: string
  type: SearchResultType
  name: string
  path: string
  snippet: string
}

const searchDialogVisible = ref(false)
const searchKeyword = ref('')
const searchLoading = ref(false)
const searchResults = ref<SearchResultItem[]>([])
const selectedResult = ref<SearchResultItem | null>(null)

function openSearchDialog() {
  searchDialogVisible.value = true
}

function handleSearchProject() {
  if (!searchKeyword.value.trim()) return

  searchLoading.value = true
  // TODO: 调后端搜索接口
  setTimeout(() => {
    searchResults.value = [
      {
        id: '1',
        type: 'controller',
        name: 'AuthController',
        path: 'src/server/auth/AuthController.ts',
        snippet: 'POST /login\nasync login(@Body() dto: LoginDto) {\n  return this.authService.login(dto)\n}',
      },
      {
        id: '2',
        type: 'service',
        name: 'UserService',
        path: 'src/server/user/UserService.ts',
        snippet: 'async refreshToken(userId: string) {\n  // ... 刷新 token 逻辑\n}',
      },
      {
        id: '3',
        type: 'page',
        name: 'Login.vue',
        path: 'src/pages/Login.vue',
        snippet: '<el-form @submit.prevent="handleLogin">\n  <!-- 登录表单 -->\n</el-form>',
      },
    ]
    searchLoading.value = false
    searchDialogVisible.value = false
  }, 800)
}

function handleClickSearchResult(item: SearchResultItem) {
  selectedResult.value = item
  currentFilePath.value = item.path
  currentFileContent.value =
    `// ${item.name} (${item.type})\n// ${item.path}\n\n${item.snippet}\n\n// ... 这里展示更多代码内容`
}

// ========== Spec ==========
const specContent = ref<string>('# 功能说明 / Spec\n\n在这里整理你对该功能的理解、接口设计、边界情况等。')
const saveSpecLoading = ref(false)

function handleSaveSpec() {
  // TODO: 保存到后端 spec_document
  saveSpecLoading.value = true
  setTimeout(() => {
    saveSpecLoading.value = false
  }, 600)
}

function handleGenerateSpec() {
  // TODO: 调用 LLM 生成 Spec
}
</script>

<template>
  <div class="page-project-detail h-full flex flex-col px-6 py-4">
    <!-- 顶部 -->
    <ProjectDetailHeader
      :name="project.name"
      :root-path="project.rootPath"
      @search="openSearchDialog"
    />

    <!-- 上半部分：项目信息 + 文件树 + 编辑器 -->
    <div class="flex gap-4 mb-4" style="height: 52vh">
      <ProjectInfoCard
        :project="project"
        :loading="saveInfoLoading"
        @update:project="handleUpdateProject"
        @save="handleSaveProjectInfo"
      />

      <ProjectFileTreePanel
        :data="fileTreeData"
        @select-file="handleSelectFile"
      />

      <ProjectFileViewer
        :file-path="currentFilePath"
        :content="currentFileContent"
      />
    </div>

    <!-- 下半部分：搜索结果 + Spec 编辑区 -->
    <div class="flex gap-4" style="height: 32vh">
      <ProjectSearchResultPanel
        :keyword="searchKeyword"
        :results="searchResults"
        @select="handleClickSearchResult"
      />

      <ProjectSpecEditor
        v-model:content="specContent"
        :saving="saveSpecLoading"
        @generate="handleGenerateSpec"
        @save="handleSaveSpec"
      />
    </div>

    <!-- 搜索项目 Modal -->
    <el-dialog
      v-model="searchDialogVisible"
      title="搜索项目"
      width="480px"
      destroy-on-close
    >
      <el-form label-width="90px">
        <el-form-item label="关键字">
          <el-input
            v-model="searchKeyword"
            placeholder="例如：登录、订单列表、refresh token、UserService..."
            @keyup.enter="handleSearchProject"
          />
        </el-form-item>
        <el-form-item>
          <p class="text-xs text-gray-500">
            将在该项目所有有效文件中搜索相关代码（实体类、Service、Controller、页面、SQL、接口定义等）。
          </p>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="searchDialogVisible = false">
          取 消
        </el-button>
        <el-button
          type="primary"
          :loading="searchLoading"
          @click="handleSearchProject"
        >
          搜 索
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.page-project-detail {
  background-color: var(--ep-bg-color-page);
}
</style>