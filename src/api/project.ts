// src/api/project.ts
import http from './http'

export interface Project {
  id: number
  name: string
  rootPath: string
  frontendPath: string | null
  serverPath: string | null
  adminPath: string | null
  description: string | null
  feArch: string | null
  serverArch: string | null
  adminArch: string | null
  totalFiles: number
  frontendFiles: number
  serverFiles: number
  adminFiles: number
  modifyCount: number
  createdAt: string
  updatedAt: string
}

// 创建/更新请求体
export interface ProjectPayload {
  name: string
  rootPath: string
  frontendPath?: string
  serverPath?: string
  adminPath?: string
  description?: string
  feArch?: string
  serverArch?: string
  adminArch?: string
}

// 获取项目列表
export async function fetchProjects() {
  const res = await http.get<Project[]>('/api/projects')
  return res.data
}

// 新增项目
export async function createProject(payload: ProjectPayload) {
  const res = await http.post<Project>('/api/projects', payload)
  return res.data
}

// 更新项目
export async function updateProject(id: number, payload: ProjectPayload) {
  const res = await http.put<Project>(`/api/projects/${id}`, payload)
  return res.data
}

// 删除项目（你现在前端按钮是“删除预留”，想接上就用它）
export async function deleteProject(id: number) {
  await http.delete(`/api/projects/${id}`)
}