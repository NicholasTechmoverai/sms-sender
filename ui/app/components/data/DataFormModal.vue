<template>
  <UModal  scrollable v-model:open="isOpen">
    <template #content>
    <UCard class="max-w-3xl w-full">
      <!-- Header -->
      <template #header>
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-lg font-semibold">
              {{ person ? 'Edit Record' : 'Create New Record' }}
            </h2>
            <p class="text-sm text-muted">Manage person details</p>
          </div>

          <UButton icon="i-lucide-x" variant="ghost" @click="close" />
        </div>
      </template>

      <!-- Form -->
      <UForm @submit="submitForm" class="space-y-6">

        <!-- Personal -->
        <div>
          <h3 class="font-medium mb-3">Personal Information</h3>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">

            <UFormField label="Name" required>
              <UInput v-model="form.name" />
            </UFormField>

            <UFormField label="Email" required>
              <UInput v-model="form.email" type="email" />
            </UFormField>

            <UFormField label="Age">
              <UInput v-model.number="form.age" type="number" />
            </UFormField>

            <UFormField label="Phone">
              <UInput v-model="form.phone" />
            </UFormField>

          </div>
        </div>

        <!-- Location -->
        <div>
          <h3 class="font-medium mb-3">Location</h3>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">

            <UFormField label="Country" required>
              <UInput v-model="form.country" />
            </UFormField>

            <UFormField label="City" required>
              <UInput v-model="form.city" />
            </UFormField>

            <UFormField label="Address" class="sm:col-span-2">
              <UTextarea v-model="form.address" />
            </UFormField>

            <UFormField label="Postal Code">
              <UInput v-model="form.postal_code" />
            </UFormField>

            <UFormField label="Timezone">
              <UInput v-model="form.timezone" />
            </UFormField>

          </div>
        </div>

        <!-- Professional -->
        <div>
          <h3 class="font-medium mb-3">Professional</h3>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">

            <UFormField label="Department" required>
              <USelect
                            value-key="value"

                v-model="form.department"
                :items="departments"
                option-attribute="label"
                value-attribute="value"
              />
            </UFormField>

            <UFormField label="Expertise Level">
              <USelect
                            value-key="value"

                v-model="form.expertise_level"
                :items="expertiseLevels"
                option-attribute="label"
                value-attribute="value"
              />
            </UFormField>

            <UFormField label="Years Experience">
              <UInput v-model.number="form.years_experience" type="number" />
            </UFormField>

            <UFormField label="Current Position">
              <UInput v-model="form.current_position" />
            </UFormField>

            <UFormField label="Company">
              <UInput v-model="form.company" />
            </UFormField>

            <UFormField label="Skills" class="sm:col-span-2">
              <UTextarea
                :value="form.skills.join(', ')"
                @input="form.skills = ($event.target.value || '').split(',').map(s => s.trim()).filter(Boolean)"
              />
            </UFormField>

          </div>
        </div>

        <!-- Additional -->
        <div>
          <h3 class="font-medium mb-3">Additional</h3>
          <div class="space-y-4">

            <UFormField label="Languages">
              <UTextarea
                :value="form.languages.join(', ')"
                @input="form.languages = ($event.target.value || '').split(',').map(s => s.trim()).filter(Boolean)"
              />
            </UFormField>

            <UFormField label="Bio">
              <UTextarea v-model="form.bio" />
            </UFormField>

            <UFormField label="Notes">
              <UTextarea v-model="form.notes" />
            </UFormField>

            <UFormField label="Tags">
              <UTextarea
                :value="form.tags.join(', ')"
                @input="form.tags = ($event.target.value || '').split(',').map(s => s.trim()).filter(Boolean)"
              />
            </UFormField>

          </div>
        </div>

        <!-- Preferences -->
        <div>
          <h3 class="font-medium mb-3">Preferences</h3>
          <div class="space-y-3">

            <div class="flex items-center justify-between">
              <span class="text-sm">SMS Enabled</span>
              <USwitch v-model="form.sms_enabled" />
            </div>

            <UFormField label="Preferred Contact">
              <USelect
              value-key="value"
                v-model="form.preferred_contact_method"
                :items="[
                  { label: 'SMS', value: 'sms' },
                  { label: 'Email', value: 'email' },
                  { label: 'WhatsApp', value: 'whatsapp' },
                  { label: 'Phone', value: 'phone' }
                ]"
              />
            </UFormField>

            <div class="flex items-center justify-between">
              <span class="text-sm">Active</span>
              <USwitch v-model="form.is_active" />
            </div>

          </div>
        </div>

        <!-- Actions -->
        <div class="flex justify-end gap-2 pt-4">
          <UButton variant="ghost" @click="close">Cancel</UButton>

          <UButton type="submit" :loading="submitting">
            {{ person ? 'Update' : 'Create' }}
          </UButton>
        </div>

      </UForm>
    </UCard>
    </template>
  </UModal>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'

const isOpen = computed({
  get: () => true,
  set: (val) => { if (!val) close() }
})

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
