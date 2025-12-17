<script setup lang="ts">
type SearchResultType = 'entity' | 'service' | 'controller' | 'page' | 'sql' | 'other'

interface SearchResultItem {
  id: string
  type: SearchResultType
  name: string
  path: string
  snippet: string
}

const props = defineProps<{
  keyword: string
  results: SearchResultItem[]
}>()

const emit = defineEmits<{
  (e: 'select', item: SearchResultItem): void
}>()
</script>

<template>
  <el-card class="w-2/5 flex flex-col" shadow="never">
    <template #header>
      <div class="flex items-center justify-between">
        <span>搜索结果</span>
        <span v-if="props.keyword" class="text-xs text-gray-500">
          关键字：“{{ props.keyword }}” 共 {{ props.results.length }} 条
        </span>
      </div>
    </template>

    <div class="flex-1 overflow-auto">
      <el-empty v-if="!props.results.length" description="暂无搜索结果" />
      <el-timeline v-else>
        <el-timeline-item
          v-for="item in props.results"
          :key="item.id"
          placement="top"
          type="primary"
          @click="emit('select', item)"
        >
          <div class="cursor-pointer hover:bg-gray-100 rounded px-2 py-1">
            <div class="flex items-center justify-between mb-1">
              <span class="font-medium text-sm">
                {{ item.name }}
              </span>
              <el-tag size="small">
                {{ item.type }}
              </el-tag>
            </div>
            <div class="text-xs text-gray-500 mb-1">
              {{ item.path }}
            </div>
            <pre class="bg-gray-100 text-gray-800 rounded p-2 text-xs whitespace-pre-wrap">
{{ item.snippet }}
            </pre>
          </div>
        </el-timeline-item>
      </el-timeline>
    </div>
  </el-card>
</template>