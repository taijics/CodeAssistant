import http from './http'
import type { FileNode } from '~/types/file' // 或直接定义

export interface FileNodeDto {
  id: string
  name: string
  path: string
  type: 'file' | 'dir'
  children?: FileNodeDto[]
}

// 触发扫描
export async function scanProjectFiles(projectId: number) {
  await http.post(`/api/projects/${projectId}/scan`)
}

// 获取文件树
export async function fetchProjectFileTree(projectId: number) {
  const res = await http.get<FileNodeDto[]>(`/api/projects/${projectId}/files/tree`)
  return res.data
}

// 获取文件内容
export async function fetchFileContent(projectId: number, path: string) {
  const res = await http.get<string>(`/api/projects/${projectId}/files/content`, {
    params: { path },
  })
  return res.data
}