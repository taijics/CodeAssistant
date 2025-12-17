<script setup lang="ts">
import { ref, watch } from 'vue'

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

const props = defineProps<{
  project: ProjectDetail
  loading: boolean
}>()

const emit = defineEmits<{
  (e: 'update:project', project: ProjectDetail): void
  (e: 'save'): void
}>()

const localProject = ref<ProjectDetail>({ ...props.project })

watch(
  () => props.project,
  (val) => {
    localProject.value = { ...val }
  },
  { deep: true },
)

watch(
  () => localProject.value,
  (val) => {
    emit('update:project', { ...val })
  },
  { deep: true },
)
</script>

<!-- template 保持你现在的即可 -->