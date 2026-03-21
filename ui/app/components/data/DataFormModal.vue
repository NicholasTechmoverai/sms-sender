<template>
  <Teleport to="body">
    <!-- Modal Backdrop -->
    <div
      class="fixed inset-0 z-50 bg-black bg-opacity-50 flex items-center justify-center p-4"
      @click.self="close"
    >
      <!-- Modal Content -->
      <div class="bg-white dark:bg-slate-900 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <!-- Header -->
        <div class="sticky top-0 bg-gray-50 dark:bg-slate-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4 flex items-center justify-between">
          <h2 class="text-xl font-bold text-gray-900 dark:text-white">
            {{ person ? 'Edit Record' : 'Create New Record' }}
          </h2>
          <button
            @click="close"
            class="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
          >
            <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>

        <!-- Form -->
        <form @submit.prevent="submitForm" class="p-6 space-y-6">
          <!-- Personal Information Section -->
          <div>
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Personal Information</h3>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <!-- Name -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Name *</label>
                <input
                  v-model="form.name"
                  type="text"
                  required
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-slate-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <!-- Email -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Email *</label>
                <input
                  v-model="form.email"
                  type="email"
                  required
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-slate-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <!-- Age -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Age</label>
                <input
                  v-model.number="form.age"
                  type="number"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-slate-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <!-- Phone -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Phone</label>
                <input
                  v-model="form.phone"
                  type="tel"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-slate-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>

          <!-- Location Information Section -->
          <div>
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Location</h3>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <!-- Country -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Country *</label>
                <input
                  v-model="form.country"
                  type="text"
                  required
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-slate-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <!-- City -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">City *</label>
                <input
                  v-model="form.city"
                  type="text"
                  required
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-slate-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <!-- Address -->
              <div class="sm:col-span-2">
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Address</label>
                <textarea
                  v-model="form.address"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-slate-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows="2"
                ></textarea>
              </div>

              <!-- Postal Code -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Postal Code</label>
                <input
                  v-model="form.postal_code"
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-slate-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <!-- Timezone -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Timezone</label>
                <input
                  v-model="form.timezone"
                  type="text"
                  placeholder="e.g., UTC, EST"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-slate-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>

          <!-- Professional Information Section -->
          <div>
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Professional Information</h3>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <!-- Department -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Department *</label>
                <select
                  v-model="form.department"
                  required
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-slate-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select Department</option>
                  <option v-for="dept in departments" :key="dept.value" :value="dept.value">
                    {{ dept.label }}
                  </option>
                </select>
              </div>

              <!-- Expertise Level -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Expertise Level</label>
                <select
                  v-model="form.expertise_level"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-slate-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select Level</option>
                  <option v-for="level in expertiseLevels" :key="level.value" :value="level.value">
                    {{ level.label }}
                  </option>
                </select>
              </div>

              <!-- Years of Experience -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Years of Experience</label>
                <input
                  v-model.number="form.years_experience"
                  type="number"
                  min="0"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-slate-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <!-- Current Position -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Current Position</label>
                <input
                  v-model="form.current_position"
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-slate-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <!-- Company -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Company</label>
                <input
                  v-model="form.company"
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-slate-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <!-- Skills -->
              <div class="sm:col-span-2">
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Skills (comma-separated)</label>
                <textarea
                  :value="form.skills.join(', ')"
                  @input="form.skills = ($event.target as HTMLTextAreaElement).value.split(',').map(s => s.trim()).filter(Boolean)"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-slate-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows="2"
                ></textarea>
              </div>
            </div>
          </div>

          <!-- Additional Information Section -->
          <div>
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Additional Information</h3>
            <div class="space-y-4">
              <!-- Languages -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Languages (comma-separated)</label>
                <textarea
                  :value="form.languages.join(', ')"
                  @input="form.languages = ($event.target as HTMLTextAreaElement).value.split(',').map(s => s.trim()).filter(Boolean)"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-slate-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows="2"
                ></textarea>
              </div>

              <!-- Bio -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Bio</label>
                <textarea
                  v-model="form.bio"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-slate-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows="3"
                ></textarea>
              </div>

              <!-- Notes -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Notes</label>
                <textarea
                  v-model="form.notes"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-slate-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows="2"
                ></textarea>
              </div>

              <!-- Tags -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Tags (comma-separated)</label>
                <textarea
                  :value="form.tags.join(', ')"
                  @input="form.tags = ($event.target as HTMLTextAreaElement).value.split(',').map(s => s.trim()).filter(Boolean)"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-slate-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows="2"
                ></textarea>
              </div>
            </div>
          </div>

          <!-- Contact Preferences Section -->
          <div>
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Contact Preferences</h3>
            <div class="space-y-3">
              <!-- SMS Enabled -->
              <label class="flex items-center space-x-3">
                <input
                  v-model="form.sms_enabled"
                  type="checkbox"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span class="text-sm text-gray-700 dark:text-gray-300">Can receive SMS</span>
              </label>

              <!-- Preferred Contact Method -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Preferred Contact Method</label>
                <select
                  v-model="form.preferred_contact_method"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-slate-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="sms">SMS</option>
                  <option value="email">Email</option>
                  <option value="whatsapp">WhatsApp</option>
                  <option value="phone">Phone</option>
                </select>
              </div>

              <!-- Active Status -->
              <label class="flex items-center space-x-3">
                <input
                  v-model="form.is_active"
                  type="checkbox"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span class="text-sm text-gray-700 dark:text-gray-300">Active</span>
              </label>
            </div>
          </div>

          <!-- Form Actions -->
          <div class="sticky bottom-0 border-t border-gray-200 dark:border-gray-700 px-6 py-4 flex items-center justify-end space-x-3">
            <button
              type="button"
              @click="close"
              class="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="submitting"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ submitting ? 'Saving...' : (person ? 'Update' : 'Create') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useApi } from '~/composables/useApi'
import { useEndpoints } from '~/composables/useEndpoints'
import { useAuthStore } from '~/stores/auth'

interface Person {
  id?: number
  name: string
  email: string
  age?: number
  phone?: string
  country: string
  city: string
  address?: string
  postal_code?: string
  timezone?: string
  department: string
  expertise_level?: string
  years_experience: number
  skills: string[]
  current_position?: string
  company?: string
  languages: string[]
  bio?: string
  is_active: boolean
  tags: string[]
  notes?: string
  sms_enabled: boolean
  preferred_contact_method: string
  [key: string]: any
}

const props = defineProps<{
  person: Person | null
  departments: any[]
  expertiseLevels: any[]
}>()

const emit = defineEmits<{
  save: []
  close: []
}>()

const { post, put } = useApi()
const endpoints = useEndpoints()
const authStore = useAuthStore()
const toast = useToast()
const submitting = ref(false)

const form = ref<Person>({
  name: '',
  email: '',
  age: undefined,
  phone: '',
  country: '',
  city: '',
  address: '',
  postal_code: '',
  timezone: '',
  department: '',
  expertise_level: '',
  years_experience: 0,
  skills: [],
  current_position: '',
  company: '',
  languages: [],
  bio: '',
  is_active: true,
  tags: [],
  notes: '',
  sms_enabled: true,
  preferred_contact_method: 'sms'
})

// Initialize form when person prop changes
watch(() => props.person, (newPerson) => {
  if (newPerson) {
    form.value = { ...newPerson }
  } else {
    form.value = {
      name: '',
      email: '',
      age: undefined,
      phone: '',
      country: '',
      city: '',
      address: '',
      postal_code: '',
      timezone: '',
      department: '',
      expertise_level: '',
      years_experience: 0,
      skills: [],
      current_position: '',
      company: '',
      languages: [],
      bio: '',
      is_active: true,
      tags: [],
      notes: '',
      sms_enabled: true,
      preferred_contact_method: 'sms'
    }
  }
}, { immediate: true })

const close = () => {
  emit('close')
}

const submitForm = async () => {
  submitting.value = true
  try {
    if (props.person?.id) {
      await put(endpoints.data.person(props.person.id), form.value, true)
    } else {
      await post(endpoints.data.people, form.value, true)
    }

    emit('save')
  } catch (error: any) {
    toast.add({
      title: 'Error',
      description: error.data?.detail || 'Failed to save record',
      color: 'error'
    })
  } finally {
    submitting.value = false
  }
}
</script>
