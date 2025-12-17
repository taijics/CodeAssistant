<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'

import ProjectDetailHeader from '~/components/projects/ProjectDetailHeader.vue'
import ProjectInfoCard from '~/components/projects/ProjectInfoCard.vue'
import ProjectFileTreePanel from '~/components/projects/ProjectFileTreePanel.vue'
import ProjectFileViewer from '~/components/projects/ProjectFileViewer.vue'
import ProjectSearchResultPanel from '~/components/projects/ProjectSearchResultPanel.vue'
import ProjectSpecEditor from '~/components/projects/ProjectSpecEditor.vue'

import type { ElTree } from 'element-plus'

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

// 文件树节点
interface FileNode {
  id: string
  name: string
  path: string
  type: 'file' | 'dir'
  children?: FileNode[]
}

// 搜索结果项
type SearchResultType = 'entity' | 'service' | 'controller' | 'page' | 'sql' | 'other'

interface SearchResultItem {
  id: string
  type: SearchResultType
  name: string
  path: string
  snippet: string
}

const route = useRoute()
const projectId = route.params.id as string | undefined

// ========== 项目信息（mock） ==========
const project = ref<ProjectDetail>({
  id: Number(projectId ?? 1),
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
  // TODO: 接后端接口保存项目信息
  saveInfoLoading.value = true
  setTimeout(() => {
    saveInfoLoading.value = false
  }, 600)
}

// 接收 ProjectInfoCard 的 v-model 更新
function handleUpdateProject(updated: ProjectDetail) {
  project.value = { ...project.value, ...updated }
}

// ========== 文件树（mock） ==========
const fileTreeData = ref<FileNode[]>([
  {
    id: 'src',
    name: 'src',
    path: 'src',
    type: 'dir',
    children: [
      {
        id: 'src/pages',
        name: 'pages',
        path: 'src/pages',
        type: 'dir',
        children: [
          {
            id: 'src/pages/Login.vue',
            name: 'Login.vue',
            path: 'src/pages/Login.vue',
            type: 'file',
          },
          {
            id: 'src/pages/OrderList.vue',
            name: 'OrderList.vue',
            path: 'src/pages/OrderList.vue',
            type: 'file',
          },
        ],
      },
      {
        id: 'src/server',
        name: 'server',
        path: 'src/server',
        type: 'dir',
        children: [
          {
            id: 'src/server/user/UserService.ts',
            name: 'UserService.ts',
            path: 'src/server/user/UserService.ts',
            type: 'file',
          },
        ],
      },
    ],
  },
])

const treeRef = ref<InstanceType<typeof ElTree>>()
const currentFilePath = ref<string>('')
const currentFileContent = ref<string>('请选择左侧文件查看内容')

function handleSelectFile(node: FileNode) {
  currentFilePath.value = node.path
  // TODO: 根据 path 调用后端 API 读取文件内容
  currentFileContent.value = `// Mock 内容：${node.path}\n\nexport const demo = () => {\n  console.log('这里展示文件内容');\n}\n`
}

// ========== 搜索 & 结果 ==========
const searchDialogVisible = ref(false)
const searchKeyword = ref('')
const searchLoading = ref(false)
const searchResults = ref<SearchResultItem[]>([])
const selectedResult = ref<SearchResultItem | null>(null)

function openSearchDialog() {
  searchDialogVisible.value = true
}

function handleSearchProject() {
  if (!searchKeyword.value.trim())
    return

  searchLoading.value = true
  // TODO: 调用后端接口，搜索项目中相关代码
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
  currentFileContent.value = `// ${item.name} (${item.type})\n// ${item.path}\n\n${item.snippet}\n\n// ... 这里展示更多代码内容`
}

// ========== Spec ==========
const specContent = ref<string>('# 功能说明 / Spec\n\n在这里整理你对该功能的理解、接口设计、边界情况等。')
const saveSpecLoading = ref(false)

function handleSaveSpec() {
  // TODO: 将 specContent 保存到后端 / 或本地文件（如 spec.md）
  saveSpecLoading.value = true
  setTimeout(() => {
    saveSpecLoading.value = false
  }, 600)
}

function handleGenerateSpec() {
  // TODO: 调用 LLM 接口生成 Spec（当前仅预留按钮）
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
        <el-button type="primary" :loading="searchLoading" @click="handleSearchProject">
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