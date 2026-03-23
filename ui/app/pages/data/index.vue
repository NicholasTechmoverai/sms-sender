
<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useApi } from "~/composables/useApi";
import { useEndpoints } from "~/composables/useEndpoints";
import { useAuthStore } from "~/stores/auth";
import DataFormModal from "~/components/data/DataFormModal.vue";
import { definePageMeta } from "#imports";


definePageMeta({
  middleware: "auth",
});

useSeoMeta({
  title: "Manage",
  ogTitle: "Manage",
  description: "Manage database",
  ogDescription: "Manage database"
})

interface Person {
  id: number;
  name: string;
  email: string;
  age?: number;
  phone?: string;
  country: string;
  city: string;
  department: string;
  expertise_level?: string;
  years_experience: number;
  is_active: boolean;
  skills?: string[];
  languages?: string[];
  tags?: string[];
  sms_enabled?: boolean;
  preferred_contact_method?: string;
  [key: string]: any;
}

const { get, del } = useApi();
const endpoints = useEndpoints();
const authStore = useAuthStore();
const toast = useToast();

// State
const people = ref<Person[]>([]);
const loading = ref(false);
const showModal = ref(false);
const selectedPerson = ref<Person | null>(null);
const searchQuery = ref("");
const skip = ref(0);
const limit = ref(10);
const total = ref(0);
const departments = ref<any[]>([]);
const expertiseLevels = ref<any[]>([]);

// Fetch people
const fetchPeople = async () => {
  loading.value = true;
  try {
    const response = await get<{ items: Person[]; total: number }>(
      endpoints.data.people,
      {
        skip: skip.value,
        limit: limit.value,
        search: searchQuery.value || undefined,
      },
      true,
    );

    people.value = response.items || [];
    total.value = response.total || 0;
  } catch (error: any) {
    toast.add({
      title: "Error",
      description: error.data?.detail || "Failed to load people",
      color: "red",
    });
  } finally {
    loading.value = false;
  }
};

// Fetch reference data
const fetchReferenceData = async () => {
  try {
    const [depts, levels] = await Promise.all([
      get<any[]>(endpoints.data.departments, undefined, true),
      get<any[]>(endpoints.data.expertiseLevels, undefined, true),
    ]);
    departments.value = depts || [];
    expertiseLevels.value = levels || [];
  } catch (error) {
    console.error("Failed to load reference data:", error);
  }
};

// Open create modal
const openCreateModal = () => {
  selectedPerson.value = null;
  showModal.value = true;
};

// Open edit modal
const openEditModal = (person: Person) => {
  selectedPerson.value = person;
  showModal.value = true;
};

// Handle modal save
const handleSave = async () => {
  showModal.value = false;
  await fetchPeople();
  toast.add({
    title: "Success",
    description: selectedPerson.value?.id
      ? "Record updated successfully"
      : "Record created successfully",
    color: "green",
  });
};

// Delete person
const deletePerson = async (id: number) => {
  if (!confirm("Are you sure you want to delete this record?")) return;

  try {
    await del(`${endpoints.data.person(id)}`, true);
    await fetchPeople();
    toast.add({
      title: "Success",
      description: "Record deleted successfully",
      color: "green",
    });
  } catch (error: any) {
    toast.add({
      title: "Error",
      description: error.data?.detail || "Failed to delete record",
      color: "red",
    });
  }
};

// Pagination
const nextPage = () => {
  skip.value += limit.value;
  fetchPeople();
};

const previousPage = () => {
  skip.value = Math.max(0, skip.value - limit.value);
  fetchPeople();
};

// Initialize
onMounted(() => {
  fetchPeople();
  fetchReferenceData();
});
</script>

<template>
  <div class="min-h-screen py-8 md:px-4">
    <div class="max-w-7xl mx-auto space-y-6">
      <!-- Header -->
      <div
        class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4"
      >
        <div>
          <h1 class="text-2xl font-semibold">Data Admin</h1>
          <p class="text-sm text-muted">Manage your database records</p>
        </div>

        <UButton icon="i-heroicons-plus" @click="openCreateModal">
          Add New Record
        </UButton>
      </div>

      <!-- Search -->
      <UCard>
        <div class="flex flex-col sm:flex-row gap-4 items-end">
          <UFormField label="Search" class="flex-1 min-w-0">
            <UInput
              v-model="searchQuery"
              placeholder="Search by name or email..."
              icon="i-heroicons-magnifying-glass"
            />
          </UFormField>

          <UButton @click="fetchPeople"> Search </UButton>
        </div>
      </UCard>

      <!-- List / Loading -->
      <UCard>
        <div v-if="loading" class="flex justify-center py-10">
          <ULoader />
          <span class="text-sm text-muted">Loading...</span>
        </div>

        <div v-else>
          <div
            v-if="people.length === 0"
            class="text-center py-10 text-sm text-muted"
          >
            No records found. Create your first record to get started.
          </div>

          <!-- Manual List -->
          <div v-else class="overflow-x-auto">
            <div class="min-w-[900px] divide-y">
              <div
                v-for="person in people"
                :key="person.id"
                class="py-4 flex items-center justify-between gap-6"
              >
                <!-- Main Row -->
                <div class="flex items-center gap-6 flex-1">
                  <!-- Avatar -->
                  <UAvatar
                    :src="person.profile_picture_url"
                    :alt="person.name"
                  />

                  <!-- Name -->
                  <div class="min-w-[150px]">
                    <div class="font-medium">{{ person.name }}</div>
                    <div class="text-xs text-muted">{{ person.email }}</div>
                  </div>

                  <!-- Phone -->
                  <div class="min-w-[140px] text-sm">
                    <div>{{ person.phone || "—" }}</div>
                    <div class="flex gap-1 pt-1">
                      <UBadge
                        size="xs"
                        :color="person.phone_verified ? 'success' : 'neutral'"
                      >
                        {{ person.phone_verified ? "Verified" : "Unverified" }}
                      </UBadge>
                      <UBadge
                        size="xs"
                        :color="person.sms_enabled ? 'success' : 'neutral'"
                      >
                        SMS
                      </UBadge>
                    </div>
                  </div>

                  <!-- Location -->
                  <div class="min-w-[140px] text-sm">
                    {{ person.city }}, {{ person.country }}
                  </div>

                  <!-- Department -->
                  <div class="min-w-[140px]">
                    <UBadge>
                      {{
                        person.department
                          ? person.department.replace("_", " ").toUpperCase()
                          : "—"
                      }}
                    </UBadge>
                  </div>

                  <!-- Status -->
                  <div class="min-w-[120px]">
                    <UBadge :color="person.is_active ? 'success' : 'neutral'">
                      {{ person.is_active ? "Active" : "Inactive" }}
                    </UBadge>
                  </div>

                  <!-- Created / Updated -->
                  <div class="min-w-[180px] text-xs text-muted">
                    <div>
                      Created:
                      {{ new Date(person.created_at).toLocaleDateString() }}
                    </div>
                    <div>
                      Updated:
                      {{ new Date(person.updated_at).toLocaleDateString() }}
                    </div>
                  </div>
                </div>

                <!-- Actions -->
                <div class="flex gap-2">
                  <UButton
                    size="xs"
                    variant="soft"
                    @click="openEditModal(person)"
                  >
                    Edit
                  </UButton>

                  <UButton
                    size="xs"
                    variant="soft"
                    color="error"
                    @click="deletePerson(person.id)"
                  >
                    Delete
                  </UButton>
                </div>
              </div>
            </div>
          </div>

          <!-- Pagination -->
          <div
            v-if="people.length"
            class="flex items-center justify-between pt-4"
          >
            <span class="text-sm text-muted">
              Showing {{ skip + 1 }} to {{ Math.min(skip + limit, total) }} of
              {{ total }}
            </span>

            <div class="flex gap-2">
              <UButton
                size="sm"
                variant="outline"
                :disabled="skip === 0"
                @click="previousPage"
              >
                Previous
              </UButton>

              <UButton
                size="sm"
                variant="outline"
                :disabled="skip + limit >= total"
                @click="nextPage"
              >
                Next
              </UButton>
            </div>
          </div>
        </div>
      </UCard>

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

