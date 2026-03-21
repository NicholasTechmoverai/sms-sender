<template>
  <div class="min-h-screen py-10 px-4 sm:px-6 lg:px-8">
    <div class="max-w-7xl mx-auto">
      <!-- Header -->
      <div class="mb-8">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Data Admin</h1>
            <p class="mt-2 text-gray-600 dark:text-gray-400">Manage your database records</p>
          </div>
          <button
            @click="openCreateModal"
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 dark:focus:ring-offset-slate-950"
          >
            <svg class="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
            </svg>
            Add New Record
          </button>
        </div>
      </div>

      <!-- Search and Filters -->
      <div class="mb-6 rounded-lg shadow p-4">
        <div class="flex flex-col sm:flex-row gap-4">
          <div class="flex-1">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search by name or email..."
              class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-slate-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <button
            @click="fetchPeople"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Search
          </button>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center items-center h-64">
        <div class="text-center">
          <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p class="mt-4 text-gray-600 dark:text-gray-400">Loading...</p>
        </div>
      </div>

      <!-- Table -->
      <div v-else class="rounded-lg shadow overflow-hidden">
        <div v-if="people.length === 0" class="p-8 text-center text-gray-600 dark:text-gray-400">
          <p>No records found. Create your first record to get started.</p>
        </div>
        
        <div v-else class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-gray-100 dark:bg-slate-800 border-b border-gray-200 dark:border-gray-700">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-950 dark:text-white uppercase tracking-wider">Name</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-950 dark:text-white uppercase tracking-wider">Email</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-950 dark:text-white uppercase tracking-wider">Location</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-950 dark:text-white uppercase tracking-wider">Department</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-950 dark:text-white uppercase tracking-wider">Status</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-950 dark:text-white uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="person in people" :key="person.id" class="hover:bg-gray-50 dark:hover:bg-slate-800 transition-colors">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">{{ person.name }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">{{ person.email }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">{{ person.city }}, {{ person.country }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                  <span class="px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200">
                    {{ person.department ? person.department.replace("_", " ").toUpperCase() : "—" }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                  <span v-if="person.is_active" class="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200">
                    Active
                  </span>
                  <span v-else class="px-2 py-1 text-xs font-semibold rounded-full bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200">
                    Inactive
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                  <button
                    @click="openEditModal(person)"
                    class="text-blue-600 dark:text-blue-400 hover:text-blue-900 dark:hover:text-blue-300"
                  >
                    Edit
                  </button>
                  <button
                    @click="deletePerson(person.id)"
                    class="text-red-600 dark:text-red-400 hover:text-red-900 dark:hover:text-red-300"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div v-if="people.length > 0" class="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <div class="text-sm text-gray-600 dark:text-gray-400">
            Showing {{ skip + 1 }} to {{ Math.min(skip + limit, total) }} of {{ total }} results
          </div>
          <div class="space-x-2">
            <button
              @click="previousPage"
              :disabled="skip === 0"
              class="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <button
              @click="nextPage"
              :disabled="skip + limit >= total"
              class="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        </div>
      </div>

      <!-- Modal -->
      <DataFormModal
        v-if="showModal"
        :person="selectedPerson"
        :departments="departments"
        :expertise-levels="expertiseLevels"
        @save="handleSave"
        @close="showModal = false"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useApi } from '~/composables/useApi'
import { useEndpoints } from '~/composables/useEndpoints'
import { useAuthStore } from '~/stores/auth'
import DataFormModal from '~/components/data/DataFormModal.vue'

interface Person {
  id: number
  name: string
  email: string
  age?: number
  phone?: string
  country: string
  city: string
  department: string
  expertise_level?: string
  years_experience: number
  is_active: boolean
  skills: string[]
  languages: string[]
  tags: string[]
  sms_enabled: boolean
  preferred_contact_method: string
  [key: string]: any
}

const { get, del } = useApi()
const endpoints = useEndpoints()
const authStore = useAuthStore()
const toast = useToast()

// State
const people = ref<Person[]>([])
const loading = ref(false)
const showModal = ref(false)
const selectedPerson = ref<Person | null>(null)
const searchQuery = ref('')
const skip = ref(0)
const limit = ref(10)
const total = ref(0)
const departments = ref<any[]>([])
const expertiseLevels = ref<any[]>([])

// Fetch people
const fetchPeople = async () => {
  loading.value = true
  try {
    const response = await get<{ items: Person[]; total: number }>(
      endpoints.data.people,
      { skip: skip.value, limit: limit.value, search: searchQuery.value || undefined },
      true
    )

    people.value = response.items || []
    total.value = response.total || 0
  } catch (error: any) {
    toast.add({
      title: 'Error',
      description: error.data?.detail || 'Failed to load people',
      color: 'error'
    })
  } finally {
    loading.value = false
  }
}

// Fetch reference data
const fetchReferenceData = async () => {
  try {
    const [depts, levels] = await Promise.all([
      get<any[]>(endpoints.data.departments, undefined, true),
      get<any[]>(endpoints.data.expertiseLevels, undefined, true)
    ])
    departments.value = depts || []
    expertiseLevels.value = levels || []
  } catch (error) {
    console.error('Failed to load reference data:', error)
  }
}

// Open create modal
const openCreateModal = () => {
  selectedPerson.value = null
  showModal.value = true
}

// Open edit modal
const openEditModal = (person: Person) => {
  selectedPerson.value = person
  showModal.value = true
}

// Handle modal save
const handleSave = async () => {
  showModal.value = false
  await fetchPeople()
  toast.add({
    title: 'Success',
    description: selectedPerson.value?.id ? 'Record updated successfully' : 'Record created successfully',
    color: 'success'
  })
}

// Delete person
const deletePerson = async (id: number) => {
  if (!confirm('Are you sure you want to delete this record?')) return

  try {
    await del(`${endpoints.data.person(id)}`, true)
    await fetchPeople()
    toast.add({
      title: 'Success',
      description: 'Record deleted successfully',
      color: 'success'
    })
  } catch (error: any) {
    toast.add({
      title: 'Error',
      description: error.data?.detail || 'Failed to delete record',
      color: 'error'
    })
  }
}

// Pagination
const nextPage = () => {
  skip.value += limit.value
  fetchPeople()
}

const previousPage = () => {
  skip.value = Math.max(0, skip.value - limit.value)
  fetchPeople()
}

// Initialize
onMounted(() => {
  fetchPeople()
  fetchReferenceData()
})
</script>
