<template>
  <div class="relative">
    <!-- Debug display -->
    <div
      class="sticky top-2 text-xs p-2 bg-gray-100 dark:bg-gray-800 flex items-center justify-between"
    >
      <div>
        STORE: {{ stateStore.ongoingSMS?.phones?.length || 0 }} phones • Last
        updated: {{ stateStore.ongoingSMS?.timestamp }}
      </div>
      <UButton
        icon="i-lucide-arrow-left"
        color="neutral"
        size="sm"
        variant="outline"
        label="SMS"
        @click="$router.push('/sms/')"
      />
    </div>
  </div>
  <div class="space-y-6 py-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
        Phone Number Selector
      </h1>
      <div class="flex items-center gap-3">
        <UBadge
          color="primary"
          size="lg"
          v-if="Object.keys(rowSelection).length"
        >
          {{ Object.keys(rowSelection).length }} users •
          {{ validPhoneCount }} valid
        </UBadge>
        <UButton
          color="success"
          icon="i-heroicons-check-circle"
          @click="submitToStore"
          :loading="submitting"
          :disabled="!allPhones.length"
          size="md"
        >
          Submit {{ allPhones.length }} Phones
        </UButton>
      </div>
    </div>

    <!-- Search Filters -->
    <UCard v-if="showFilter" class="shadow-sm">
      <template #header>
        <div
          class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between"
        >
          <div>
            <h2 class="text-lg font-semibold">Search Filters</h2>
            <p class="text-sm text-gray-500">
              Refine your search with the options below
            </p>
          </div>

          <div class="flex gap-2">
            <UButton
              color="neutral"
              variant="soft"
              icon="i-heroicons-arrow-path"
              :loading="loading"
              @click="resetFilters"
            >
              Reset
            </UButton>
            <UButton
              color="primary"
              icon="i-heroicons-magnifying-glass"
              :loading="loading"
              @click="search"
            >
              Search
            </UButton>
          </div>
        </div>
      </template>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        <!-- Location -->
        <div class="flex flex-col gap-3 min-w-0">
          <UFormField label="Country">
            <UInput
              class="min-w-0"
              v-model="filters.country"
              placeholder="e.g Kenya"
              icon="i-heroicons-map-pin"
            />
          </UFormField>

          <UFormField label="City">
            <UInput
              class="min-w-0"
              v-model="filters.city"
              placeholder="e.g Nairobi"
              icon="i-heroicons-building-office-2"
            />
          </UFormField>
        </div>

        <!-- Professional Info -->
        <div class="flex flex-col gap-3 min-w-0">
          <UFormField label="Department">
            <USelect
              class="min-w-0"
              v-model="filters.department"
              :items="departmentOptions"
              placeholder="Select department"
              clearable
            />
          </UFormField>

          <UFormField label="Expertise Level">
            <USelect
              class="min-w-0"
              v-model="filters.expertise_level"
              :items="expertiseOptions"
              placeholder="Select level"
              clearable
            />
          </UFormField>

          <UFormField label="Experience (Years)">
            <UInput
              class="min-w-0"
              v-model="filters.min_experience"
              type="number"
              min="0"
              max="50"
              placeholder="e.g 3"
            />
          </UFormField>
        </div>

        <!-- Skills & Languages -->
        <div class="flex flex-col gap-3 min-w-0">
          <UFormField label="Skills">
            <USelectMenu
              class="min-w-0"
              v-model="filters.required_skills"
              :items="commonSkills"
              multiple
              searchable
              placeholder="Select skills"
            />
          </UFormField>

          <UFormField label="Languages">
            <USelectMenu
              class="min-w-0"
              v-model="filters.languages"
              :items="commonLanguages"
              multiple
              placeholder="Select languages"
            />
          </UFormField>
        </div>

        <!-- Age Range -->
        <div class="flex flex-col gap-3 min-w-0">
          <UFormField label="Age Range">
            <div class="flex gap-2">
              <UInput
                class="min-w-0"
                v-model="filters.min_age"
                type="number"
                min="18"
                max="100"
                placeholder="Min"
              />
              <UInput
                class="min-w-0"
                v-model="filters.max_age"
                type="number"
                min="18"
                max="100"
                placeholder="Max"
              />
            </div>
          </UFormField>
        </div>

        <!-- Identity -->
        <div class="flex flex-col gap-3 min-w-0">
          <UFormField label="Name">
            <UInput
              class="min-w-0"
              v-model="filters.name_contains"
              placeholder="Search by name"
              icon="i-heroicons-user"
            />
          </UFormField>
        </div>

        <!-- Status -->
        <div class="flex flex-col gap-3 min-w-0">
          <UFormField label="Status">
            <USelect
              class="min-w-0"
              v-model="filters.is_active"
              :items="statusOptions"
              placeholder="Any"
              clearable
            />
          </UFormField>
        </div>

        <!-- Contact -->
        <div class="flex flex-col gap-3 min-w-0">
          <UFormField label="Phone">
            <UInput
              class="min-w-0"
              v-model="filters.phone_contains"
              placeholder="Partial phone number"
              icon="i-heroicons-phone"
            />
          </UFormField>

          <UFormField label="Has Phone">
            <USelect
              class="min-w-0"
              v-model="filters.has_phone"
              :items="[
                { label: 'Yes', value: true },
                { label: 'No', value: false },
              ]"
              placeholder="Any"
              clearable
            />
          </UFormField>

          <UFormField label="SMS Enabled">
            <USelect
              class="min-w-0"
              v-model="filters.sms_enabled"
              :items="[
                { label: 'Yes', value: true },
                { label: 'No', value: false },
              ]"
              placeholder="Any"
              clearable
            />
          </UFormField>
        </div>
      </div>
    </UCard>

    <!-- Bulk Actions -->
    <div
      class="flex items-center justify-between gap-4 flex-wrap"
      v-if="Object.keys(rowSelection).length || manualPhones.length"
    >
      <div class="flex items-center gap-2 flex-wrap">
        <UDropdownMenu :items="bulkSelectionItems">
          <UButton
            color="neutral"
            variant="soft"
            icon="i-heroicons-adjustments-horizontal"
            >Smart Select</UButton
          >
        </UDropdownMenu>

        <!-- Manual Phone Input -->
        <UPopover>
          <UButton color="neutral" variant="soft" icon="i-heroicons-phone-plus"
            >Add Manual</UButton
          >
          <template #panel>
            <div class="p-4 w-80">
              <h3 class="font-medium mb-3">Add Phone Number Manually</h3>
              <UFormGroup label="Phone Number" required>
                <UInput v-model="manualPhone.phone" placeholder="+1234567890" />
              </UFormGroup>
              <UFormGroup label="Name (optional)">
                <UInput v-model="manualPhone.name" placeholder="Contact name" />
              </UFormGroup>
              <div class="flex justify-end gap-2 mt-4">
                <UButton
                  size="xs"
                  color="neutral"
                  @click="manualPhone = { phone: '', name: '' }"
                  >Clear</UButton
                >
                <UButton
                  size="xs"
                  color="primary"
                  @click="addManualPhone"
                  :disabled="!manualPhone.phone"
                  >Add</UButton
                >
              </div>
            </div>
          </template>
        </UPopover>

        <UButton color="neutral" variant="ghost" @click="clearSelection"
          >Clear All</UButton
        >
        <UButton
          color="primary"
          variant="soft"
          size="sm"
          @click="previewSelection"
        >
          Preview ({{ validPhoneCount + manualPhones.length }})
        </UButton>
      </div>
      <div class="text-sm text-gray-500 flex items-center gap-2">
        <span>{{ selectedUsersWithPhone.length }} with phone</span>
        <span class="w-1 h-1 rounded-full bg-gray-400"></span>
        <span>{{ selectedUsersWithoutPhone.length }} without</span>
        <span class="w-1 h-1 rounded-full bg-gray-400"></span>
        <span class="font-mono text-green-600 dark:text-green-400"
          >{{ validPhoneCount }} valid</span
        >
        <span
          v-if="manualPhones.length"
          class="font-mono text-blue-600 dark:text-blue-400"
          >+{{ manualPhones.length }} manual</span
        >
      </div>
    </div>

    <!-- Results -->
    <UCard>
      <template #header>
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-4">
            <h2 class="text-lg font-semibold">Users</h2>
            <UBadge color="neutral" variant="solid" size="sm"
              >{{ totalCount }} total</UBadge
            >
          </div>
          <div class="flex items-center gap-2">
            <span class="text-xs text-gray-500">Sort by:</span>
            <USelect
              v-model="sortBy"
              :items="sortOptions"
              size="xs"
              class="w-32"
            />
            <UButton
              size="xs"
              color="neutral"
              variant="ghost"
              :icon="
                sortOrder === 'asc'
                  ? 'i-heroicons-arrow-up'
                  : 'i-heroicons-arrow-down'
              "
              @click="toggleSortOrder"
            />
          </div>
        </div>
      </template>

      <!-- Users Table -->
      <div class="overflow-x-auto">
        <div
          class="flex px-4 py-3.5 border-b border-gray-200 dark:border-gray-700 justify-between"
        >
          <UInput
            v-model="globalFilter"
            class="max-w-sm"
            placeholder="Filter..."
          />
          <div  class="flex items-center gap-2">
            <UDropdownMenu
              :items="
                table?.tableApi
                  ?.getAllColumns()
                  .filter((column) => column.getCanHide())
                  .map((column) => ({
                    label: upperFirst(column.id),
                    type: 'checkbox' as const,
                    checked: column.getIsVisible(),
                    onUpdateChecked(checked: boolean) {
                      table?.tableApi
                        ?.getColumn(column.id)
                        ?.toggleVisibility(!!checked);
                    },
                    onSelect(e: Event) {
                      e.preventDefault();
                    },
                  }))
              "
              :content="{ align: 'end' }"
            >
              <UButton
                label="Columns"
                color="neutral"
                variant="outline"
                trailing-icon="i-lucide-chevron-down"
              />
            </UDropdownMenu>

            <UButton
              icon="i-lucide-sliders-horizontal"
              size="md"
              color="primary"
              @click="showFilter = !showFilter"
              variant="solid"
            />
          </div>
        </div>

        <UTable
          ref="table"
          v-model:global-filter="globalFilter"
          v-model:row-selection="rowSelection"
          v-model:sort="sortState"
          v-model:column-visibility="columnVisibility"
          :data="users"
          :columns="columns"
          :loading="loading"
        />
      </div>

      <!-- Manual Phones Display -->
      <div
        v-if="manualPhones.length"
        class="border-t border-gray-200 dark:border-gray-700 px-4 py-3"
      >
        <UInput v-model="value" />
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm font-medium"
            >Manual Entries ({{ manualPhones.length }})</span
          >
          <UButton
            size="xs"
            color="neutral"
            variant="ghost"
            icon="i-heroicons-x-mark"
            @click="manualPhones = []"
            >Clear</UButton
          >
        </div>
        <div class="flex flex-wrap gap-2">
          <div
            v-for="(phone, idx) in manualPhones"
            :key="idx"
            class="bg-blue-50 dark:bg-blue-900/20 rounded-lg px-3 py-1.5 flex items-center gap-2"
          >
            <span class="font-mono text-sm">{{
              formatPhoneNumber(phone.phone)
            }}</span>
            <span v-if="phone.name" class="text-xs text-gray-500">{{
              phone.name
            }}</span>
            <UButton
              size="2xs"
              color="neutral"
              variant="ghost"
              icon="i-heroicons-x-mark"
              @click="removeManualPhone(idx)"
            />
          </div>
        </div>
      </div>

      <!-- Selection Info & Footer -->
      <template #footer>
        <div class="space-y-3">
          <!-- Selection count from table -->
          <div class="px-1 text-sm text-gray-500">
            {{
              table?.tableApi?.getFilteredSelectedRowModel().rows.length || 0
            }}
            of
            {{ table?.tableApi?.getFilteredRowModel().rows.length || 0 }} row(s)
            selected.
            <span v-if="manualPhones.length" class="ml-2 text-blue-500"
              >+{{ manualPhones.length }} manual</span
            >
          </div>

          <!-- Phone numbers display -->
          <div
            v-if="selectedUsersWithPhone.length || manualPhones.length"
            class="border-t border-gray-200 dark:border-gray-700 pt-3"
          >
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center gap-2">
                <span class="text-sm font-medium">
                  Selected Numbers ({{
                    selectedUsersWithPhone.length + manualPhones.length
                  }})
                </span>
                <UBadge color="success" variant="soft" size="xs"
                  >{{ validPhoneCount + manualPhones.length }} ready</UBadge
                >
                <UBadge
                  v-if="selectedUsersWithoutPhone.length"
                  color="warning"
                  variant="soft"
                  size="xs"
                  >{{ selectedUsersWithoutPhone.length }} invalid</UBadge
                >
              </div>
              <div class="flex gap-1">
                <UButton
                  size="xs"
                  color="neutral"
                  variant="ghost"
                  icon="i-heroicons-clipboard"
                  @click="copyPhonesToClipboard"
                  :disabled="!allPhones.length"
                />
                <UButton
                  size="xs"
                  color="neutral"
                  variant="ghost"
                  icon="i-heroicons-arrow-down-tray"
                  @click="downloadPhones"
                  :disabled="!allPhones.length"
                />
              </div>
            </div>
            <div
              class="bg-gray-50 dark:bg-gray-800 rounded-lg p-3 max-h-32 overflow-y-auto font-mono text-sm"
            >
              <!-- User phones -->
              <div
                v-for="(user, index) in selectedUsersWithPhone"
                :key="user.id"
                class="py-0.5 flex items-center gap-2"
              >
                <span class="text-gray-400">{{ index + 1 }}.</span>
                <span
                  :class="{
                    'text-green-600 dark:text-green-400': user.sms_enabled,
                    'text-yellow-600 dark:text-yellow-400': !user.sms_enabled,
                  }"
                >
                  {{ formatPhoneNumber(user.phone) }}
                </span>
                <UBadge v-if="!user.sms_enabled" color="warning" size="xs"
                  >SMS disabled</UBadge
                >
                <span class="text-xs text-gray-400 ml-2">{{ user.name }}</span>
              </div>
              <!-- Manual phones -->
              <div
                v-for="(phone, idx) in manualPhones"
                :key="'manual-' + idx"
                class="py-0.5 flex items-center gap-2"
              >
                <span class="text-gray-400"
                  >{{ selectedUsersWithPhone.length + idx + 1 }}.</span
                >
                <span class="text-blue-600 dark:text-blue-400">{{
                  formatPhoneNumber(phone.phone)
                }}</span>
                <UBadge color="info" size="xs">manual</UBadge>
                <span class="text-xs text-gray-400 ml-2">{{
                  phone.name || "Unnamed"
                }}</span>
              </div>
            </div>
          </div>

          <!-- Controls -->
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-4">
              <div class="flex items-center gap-2">
                <span class="text-sm text-gray-500">Rows:</span>
                <USelect
                  v-model="limit"
                  :items="[5, 10, 20, 50, 100]"
                  size="xs"
                  class="w-20"
                />
              </div>

              <div class="flex items-center gap-2" v-if="allPhones.length">
                <span class="text-sm text-gray-500">Take:</span>
                <UInput
                  v-model.number="phoneSliceCount"
                  type="number"
                  min="1"
                  :max="allPhones.length"
                  size="xs"
                  class="w-20"
                />
                <UButton
                  size="xs"
                  color="primary"
                  variant="soft"
                  @click="slicePhones"
                  :disabled="!phoneSliceCount"
                  >Get</UButton
                >
              </div>
            </div>

            <div class="flex items-center gap-4">
              <span class="text-sm text-gray-500"
                >Showing {{ offset + 1 }}-{{
                  Math.min(offset + limit, totalCount)
                }}
                of {{ totalCount }}</span
              >
              <UButtonGroup size="sm">
                <UButton
                  color="neutral"
                  variant="ghost"
                  icon="i-heroicons-chevron-left"
                  :disabled="offset === 0"
                  @click="prevPage"
                />
                <UButton
                  color="neutral"
                  variant="ghost"
                  icon="i-heroicons-chevron-right"
                  :disabled="offset + limit >= totalCount"
                  @click="nextPage"
                />
              </UButtonGroup>
            </div>
          </div>

          <!-- Quick stats -->
          <div
            class="flex justify-between items-center border-t border-gray-200 dark:border-gray-700 pt-2"
          >
            <div class="flex gap-4 text-xs">
              <span class="text-gray-400"
                >📱 In view: {{ totalPhoneCount }}</span
              >
              <span class="text-green-600 dark:text-green-400"
                >✅ Valid: {{ validPhoneCount }}</span
              >
              <span class="text-blue-600 dark:text-blue-400"
                >✍️ Manual: {{ manualPhones.length }}</span
              >
              <span class="text-purple-600 dark:text-purple-400"
                >📦 Stored:
                {{ stateStore.ongoingSMS?.phones?.length || 0 }}</span
              >
            </div>
            <div class="flex items-center gap-3">
              <!-- View Stored Modal Button -->
              <UModal
                v-model:open="showStoredModal"
                :title="`Stored Phones (${stateStore.ongoingSMS?.phones?.length || 0})`"
              >
                <UButton
                  color="purple"
                  size="xs"
                  variant="soft"
                  icon="i-heroicons-eye"
                  :disabled="!stateStore.ongoingSMS?.phones?.length"
                >
                  View Stored
                </UButton>
                <template #body>
                  <UCard class="w-full">
                    <div class="max-h-96 overflow-y-auto space-y-2">
                      <div v-if="stateStore.ongoingSMS?.phones?.length">
                        <div
                          v-for="(phone, index) in stateStore.ongoingSMS.phones"
                          :key="index"
                          class="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg flex items-center justify-between"
                        >
                          <div>
                            <div class="font-mono text-sm">
                              {{
                                phone.formatted ||
                                formatPhoneNumber(phone.phone)
                              }}
                            </div>
                            <div class="text-xs text-gray-500">
                              {{ phone.name }} • {{ phone.source }} •
                              {{ phone.department || "N/A" }}
                            </div>
                          </div>
                          <div class="flex gap-1">
                            <UButton
                              size="xs"
                              color="primary"
                              variant="soft"
                              icon="i-heroicons-plus"
                              @click="addStoredToSelection(phone)"
                            />
                            <UButton
                              size="xs"
                              color="neutral"
                              variant="ghost"
                              icon="i-heroicons-clipboard"
                              @click="copySinglePhone(phone.phone)"
                            />
                          </div>
                        </div>
                      </div>
                      <div v-else class="text-center py-8 text-gray-500">
                        No phones stored yet
                      </div>
                    </div>

                    <template #footer>
                      <div class="flex justify-end gap-2">
                        <UButton color="primary" @click="copyAllStored"
                          >Copy All</UButton
                        >
                        <UButton
                          color="error"
                          variant="soft"
                          @click="resetStore"
                          >Clear Store</UButton
                        >
                      </div>
                    </template>
                  </UCard>
                </template>
              </UModal>

              <UButton
                color="success"
                size="xs"
                icon="i-heroicons-check"
                @click="submitToStore"
                :loading="submitting"
                :disabled="!allPhones.length"
              >
                Submit {{ allPhones.length }}
              </UButton>
            </div>
          </div>
        </div>
      </template>
    </UCard>
  </div>
</template>

<script setup lang="ts">
import { h, resolveComponent } from "vue";
import type { TableColumn } from "@nuxt/ui";
import type { Column } from "@tanstack/vue-table";
import { upperFirst } from "scule";

const showFilter = ref(false);
const UBadge = resolveComponent("UBadge");
const UButton = resolveComponent("UButton");
const UDropdownMenu = resolveComponent("UDropdownMenu");
const UCheckbox = resolveComponent("UCheckbox");

const stateStore = useAuthStore();

interface User {
  id: string;
  name: string;
  email: string;
  phone: string;
  department: string;
  country: string;
  city: string;
  skills: string[];
  languages: string[];
  years_experience: number;
  age?: number;
  is_active: boolean;
  sms_enabled: boolean;
}

interface ManualPhone {
  phone: string;
  name: string;
}

const props = defineProps<{ initialFilters?: Record<string, any> }>();

// Table ref
const table = useTemplateRef("table");

// State
const loading = ref(false);
const submitting = ref(false);
const showStoredModal = ref(false);
const users = ref<User[]>([]);
const totalCount = ref(0);
const globalFilter = ref("");
const phoneSliceCount = ref(10);
const manualPhones = ref<ManualPhone[]>([]);
const manualPhone = ref<ManualPhone>({ phone: "", name: "" });

// Row selection
const rowSelection = ref({});

// Sorting
const sortState = ref([{ id: "name", desc: false }]);
const sortBy = ref("name");
const sortOrder = ref("asc");

// Pagination
const limit = ref(10);
const offset = ref(0);

// Filters
const filters = ref({
  country: "",
  city: "",
  department: "",
  expertise_level: "",
  min_experience: null as number | null,
  required_skills: [] as string[],
  languages: [] as string[],
  min_age: null as number | null,
  max_age: null as number | null,
  name_contains: "",
  is_active: null as boolean | null,
  phone_contains: "",
  has_phone: null as boolean | null,
  sms_enabled: null as boolean | null,
});

// Options
const departmentOptions = [
  { label: "Engineering", value: "engineering" },
  { label: "Marketing", value: "marketing" },
  { label: "Sales", value: "sales" },
  { label: "HR", value: "human_resources" },
  { label: "Finance", value: "finance" },
  { label: "R&D", value: "research_development" },
];
const expertiseOptions = [
  { label: "Junior", value: "junior" },
  { label: "Mid", value: "mid_level" },
  { label: "Senior", value: "senior" },
  { label: "Lead", value: "lead" },
];
const statusOptions = [
  { label: "Active", value: true },
  { label: "Inactive", value: false },
];
const commonSkills = [
  "Python",
  "JavaScript",
  "React",
  "Vue",
  "Node.js",
  "AWS",
  "Docker",
  "SQL",
];
const commonLanguages = ["English", "Spanish", "French", "German", "Chinese"];
const sortOptions = [
  { label: "Name", value: "name" },
  { label: "Email", value: "email" },
  { label: "Department", value: "department" },
  { label: "Country", value: "country" },
  { label: "City", value: "city" },
  { label: "Experience", value: "years_experience" },
  { label: "Age", value: "age" },
  { label: "Phone", value: "phone" },
  { label: "Time", value: "created_at" },
];

// Helper for sortable headers
function getHeader(column: Column<User>, label: string) {
  const isSorted = column.getIsSorted();
  return h(
    UDropdownMenu,
    {
      content: { align: "start" },
      items: [
        {
          label: "Sort Ascending",
          icon: "i-heroicons-arrow-up",
          onSelect: () => column.toggleSorting(false),
        },
        {
          label: "Sort Descending",
          icon: "i-heroicons-arrow-down",
          onSelect: () => column.toggleSorting(true),
        },
        {
          label: "Clear Sort",
          icon: "i-heroicons-x-mark",
          onSelect: () => column.clearSorting(),
        },
      ],
    },
    () =>
      h(UButton, {
        color: "neutral",
        variant: "ghost",
        label,
        icon: isSorted
          ? isSorted === "asc"
            ? "i-heroicons-arrow-up"
            : "i-heroicons-arrow-down"
          : "i-heroicons-arrows-up-down",
        class: "-mx-2.5",
        size: "xs",
      }),
  );
}

const columnVisibility = ref({
  id: false,
  email: false,
  department: false,
  age: false,
  years_experience: false,
  is_active: false,
});

// Table Columns
const columns: TableColumn<User>[] = [
  {
    id: "select",
    header: ({ table }) =>
      h(UCheckbox, {
        modelValue: table.getIsSomePageRowsSelected()
          ? "indeterminate"
          : table.getIsAllPageRowsSelected(),
        "onUpdate:modelValue": (value: boolean | "indeterminate") =>
          table.toggleAllPageRowsSelected(!!value),
      }),
    cell: ({ row }) =>
      h(UCheckbox, {
        modelValue: row.getIsSelected(),
        "onUpdate:modelValue": (value: boolean | "indeterminate") =>
          row.toggleSelected(!!value),
      }),
  },
  {
    accessorKey: "id",
    header: ({ column }) => getHeader(column, "ID"),
    cell: ({ row }) => `#${row.getValue("id")}`,
  },
  { accessorKey: "name", header: ({ column }) => getHeader(column, "Name") },
  { accessorKey: "email", header: ({ column }) => getHeader(column, "Email") },
  { accessorKey: "phone", header: ({ column }) => getHeader(column, "Phone") },
  {
    accessorKey: "is_active",
    header: ({ column }) => getHeader(column, "Status"),
  },
  {
    accessorKey: "sms_enabled",
    header: ({ column }) => getHeader(column, "SMS"),
  },
  {
    accessorKey: "department",
    header: ({ column }) => getHeader(column, "Dept"),
  },
  {
    accessorKey: "country",
    header: ({ column }) => getHeader(column, "Country"),
  },
  { accessorKey: "city", header: ({ column }) => getHeader(column, "City") },
  { accessorKey: "age", header: ({ column }) => getHeader(column, "Age") },
  {
    accessorKey: "years_experience",
    header: ({ column }) => getHeader(column, "Exp"),
  },
  {
    id: "actions",
    header: "",
    cell: ({ row }) =>
      h(UDropdownMenu, { items: actionItems(row.original) }, () =>
        h(UButton, {
          color: "neutral",
          variant: "ghost",
          icon: "i-heroicons-ellipsis-horizontal",
        }),
      ),
  },
];

// Computed
const selectedUsers = computed(() => {
  if (!table.value?.tableApi) return [];
  const selectedRows = table.value.tableApi.getFilteredSelectedRowModel().rows;
  return selectedRows.map((row) => row.original);
});

const selectedUsersWithPhone = computed(() =>
  selectedUsers.value.filter((u) => u.phone),
);
const selectedUsersWithoutPhone = computed(() =>
  selectedUsers.value.filter((u) => !u.phone),
);
const validPhoneCount = computed(
  () => selectedUsers.value.filter((u) => u.phone && u.sms_enabled).length,
);
const totalPhoneCount = computed(
  () => users.value.filter((u) => u.phone).length,
);
const allPhones = computed(() => [
  ...selectedUsers.value
    .filter((u) => u.phone && u.sms_enabled)
    .map((u) => ({ phone: u.phone, name: u.name, source: "user", id: u.id })),
  ...manualPhones.value.map((p, idx) => ({
    phone: p.phone,
    name: p.name,
    source: "manual",
    id: `manual-${Date.now()}-${idx}`,
  })),
]);

// Utilities
function formatPhoneNumber(phone: string) {
  if (!phone) return "";
  const cleaned = phone.replace(/\D/g, "");
  if (cleaned.length === 10)
    return `(${cleaned.slice(0, 3)}) ${cleaned.slice(3, 6)}-${cleaned.slice(6)}`;
  if (cleaned.length === 11 && cleaned.startsWith("1"))
    return `+1 (${cleaned.slice(1, 4)}) ${cleaned.slice(4, 7)}-${cleaned.slice(7)}`;
  return phone;
}

// Manual phone handling
function addManualPhone() {
  if (!manualPhone.value.phone) return;
  manualPhones.value.push({
    phone: manualPhone.value.phone,
    name: manualPhone.value.name || "Manual Entry",
  });
  manualPhone.value = { phone: "", name: "" };
  useToast().add({
    title: "Added",
    description: "Phone added to selection",
    color: "success",
  });
}

function removeManualPhone(index: number) {
  manualPhones.value.splice(index, 1);
}

// Store reset function
function resetStore() {
  stateStore.ongoingSMS = {
    phones: [],
    count: 0,
    timestamp: new Date().toISOString(),
  };
  showStoredModal.value = false;
  useToast().add({
    title: "Store Reset",
    description: "All stored phones cleared",
    color: "info",
  });
}

// Stored phones handling
function loadStoredPhones() {
  if (stateStore.ongoingSMS?.phones) {
    useToast().add({
      title: "Stored Phones",
      description: `${stateStore.ongoingSMS.phones.length} phones in store`,
      color: "info",
    });
  }
}

function addStoredToSelection(phone: any) {
  manualPhones.value.push({
    phone: phone.phone,
    name: phone.name || "From Store",
  });
  useToast().add({
    title: "Added",
    description: "Phone added from store",
    color: "success",
  });
}

async function copyStoredPhones() {
  if (!stateStore.ongoingSMS?.phones) return;
  const phones = stateStore.ongoingSMS.phones.map((p) => p.phone).join("\n");
  await navigator.clipboard.writeText(phones);
  useToast().add({
    title: "Copied!",
    description: `${stateStore.ongoingSMS.phones.length} stored phones copied`,
    color: "green",
  });
}

async function copyAllStored() {
  await copyStoredPhones();
  showStoredModal.value = false;
}

async function copySinglePhone(phone: string) {
  await navigator.clipboard.writeText(phone);
  useToast().add({
    title: "Copied!",
    description: "Phone number copied",
    color: "green",
  });
}

// Toggle sort order
function toggleSortOrder() {
  sortOrder.value = sortOrder.value === "asc" ? "desc" : "asc";
  sortState.value = [{ id: sortBy.value, desc: sortOrder.value === "desc" }];
  search();
}

// Bulk selection items
const bulkSelectionItems = [
  {
    label: "Smart Combinations",
    icon: "i-heroicons-sparkles",
    children: [
      {
        label: "Active & With Phone & SMS Enabled",
        onSelect: () =>
          selectByFilter((u) => u.is_active && u.phone && u.sms_enabled),
      },
      {
        label: "Inactive & With Phone",
        onSelect: () => selectByFilter((u) => !u.is_active && u.phone),
      },
      {
        label: "Active & No Phone",
        onSelect: () => selectByFilter((u) => u.is_active && !u.phone),
      },
    ],
  },
  {
    label: "Phone Status",
    icon: "i-heroicons-phone",
    children: [
      { label: "With Phone", onSelect: () => selectByFilter((u) => u.phone) },
      {
        label: "Without Phone",
        onSelect: () => selectByFilter((u) => !u.phone),
      },
      {
        label: "SMS Enabled",
        onSelect: () => selectByFilter((u) => u.sms_enabled),
      },
      {
        label: "SMS Disabled",
        onSelect: () => selectByFilter((u) => !u.sms_enabled),
      },
    ],
  },
  {
    label: "Account Status",
    icon: "i-heroicons-user",
    children: [
      { label: "Active", onSelect: () => selectByFilter((u) => u.is_active) },
      {
        label: "Inactive",
        onSelect: () => selectByFilter((u) => !u.is_active),
      },
    ],
  },
  {
    label: "Demographics",
    icon: "i-heroicons-users",
    children: [
      {
        label: "Age 18-25",
        onSelect: () =>
          selectByFilter((u) => u.age && u.age >= 18 && u.age <= 25),
      },
      {
        label: "Age 26-35",
        onSelect: () =>
          selectByFilter((u) => u.age && u.age >= 26 && u.age <= 35),
      },
      {
        label: "Age 36-50",
        onSelect: () =>
          selectByFilter((u) => u.age && u.age >= 36 && u.age <= 50),
      },
      {
        label: "Age 50+",
        onSelect: () => selectByFilter((u) => u.age && u.age >= 50),
      },
    ],
  },
];

// Selection methods
function selectByFilter(filterFn: (u: User) => boolean) {
  if (!table.value?.tableApi) return;
  const newSelection: Record<string, boolean> = {};
  users.value.forEach((user, index) => {
    if (filterFn(user)) newSelection[index] = true;
  });
  rowSelection.value = newSelection;
  useToast().add({
    title: "Smart Selection",
    description: `${Object.keys(newSelection).length} users selected`,
    color: "success",
  });
}

// Submit to store
function submitToStore() {
  submitting.value = true;
  try {
    const currentSelectedUsers = selectedUsers.value;
    const userPhones = currentSelectedUsers
      .filter((u) => u.phone && u.sms_enabled)
      .map((u) => ({
        phone: u.phone,
        name: u.name,
        id: u.id,
        formatted: formatPhoneNumber(u.phone),
        department: u.department,
        country: u.country,
        source: "user",
        timestamp: new Date().toISOString(),
      }));

    const manualPhoneEntries = manualPhones.value.map((p) => ({
      phone: p.phone,
      name: p.name || "Manual Entry",
      formatted: formatPhoneNumber(p.phone),
      source: "manual",
      id: `manual-${Date.now()}-${Math.random()}`,
      timestamp: new Date().toISOString(),
    }));

    const phonesToSave = [...userPhones, ...manualPhoneEntries];
    const existingPhones = stateStore.ongoingSMS?.phones || [];
    const allPhones = [...existingPhones];
    const existingNumbers = new Set(existingPhones.map((p) => p.phone));

    phonesToSave.forEach((phone) => {
      if (!existingNumbers.has(phone.phone)) {
        allPhones.push(phone);
        existingNumbers.add(phone.phone);
      }
    });

    stateStore.ongoingSMS = {
      phones: allPhones,
      count: allPhones.length,
      timestamp: new Date().toISOString(),
      filters: { ...filters.value },
      lastAdded: phonesToSave.length,
      totalSubmissions: (stateStore.ongoingSMS?.totalSubmissions || 0) + 1,
    };

    useToast().add({
      title: "✅ Submitted!",
      description: `Added ${phonesToSave.length} new phones. Total: ${allPhones.length}`,
      color: "green",
    });
    useRouter().push("/sms");
  } catch (error) {
    console.error("Submit error:", error);
    useToast().add({
      title: "Error",
      description: "Failed to save phones",
      color: "red",
    });
  } finally {
    submitting.value = false;
  }
}

// API Methods
async function search() {
  loading.value = true;
  try {
    const params = new URLSearchParams();
    Object.entries(filters.value).forEach(([key, value]) => {
      if (
        value !== null &&
        value !== "" &&
        (!Array.isArray(value) || value.length > 0)
      ) {
        params.append(
          key,
          Array.isArray(value) ? value.join(",") : String(value),
        );
      }
    });
    params.append("limit", String(limit.value));
    params.append("offset", String(offset.value));
    params.append("sort_by", sortBy.value);
    params.append("sort_order", sortOrder.value);

    const { get } = useApi();
    const endpoints = useEndpoints();
    const res = await get(`${endpoints.users.search}?${params.toString()}`);

    if (res) {
      users.value = res.results || [];
      totalCount.value = res.pagination?.total_count || 0;
    }
  } catch (error) {
    console.error("Failed to search users:", error);
    useToast().add({
      title: "Error",
      description: "Failed to search users",
      color: "red",
    });
  } finally {
    loading.value = false;
  }
}

function resetFilters() {
  filters.value = {
    country: "",
    city: "",
    department: "",
    expertise_level: "",
    min_experience: null,
    required_skills: [],
    languages: [],
    min_age: null,
    max_age: null,
    name_contains: "",
    is_active: null,
    phone_contains: "",
    has_phone: null,
    sms_enabled: null,
  };
  offset.value = 0;
  search();
}

function clearSelection() {
  rowSelection.value = {};
  manualPhones.value = [];
  useToast().add({
    title: "Cleared",
    description: "All selections cleared",
    color: "neutral",
  });
}

function previewSelection() {
  useToast().add({
    title: "Preview",
    description: `${selectedUsers.value.length} users, ${validPhoneCount.value} valid, ${manualPhones.value.length} manual`,
    color: "info",
  });
}

async function copyPhonesToClipboard() {
  const phones = allPhones.value.map((p) => p.phone).join("\n");
  await navigator.clipboard.writeText(phones);
  useToast().add({
    title: "Copied!",
    description: `${allPhones.value.length} phone numbers copied`,
    color: "green",
  });
}

function downloadPhones() {
  const content = allPhones.value
    .map((p) => `${p.phone}${p.name ? ` - ${p.name}` : ""}`)
    .join("\n");
  const blob = new Blob([content], { type: "text/plain" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `phones-${new Date().toISOString().slice(0, 10)}.txt`;
  a.click();
  URL.revokeObjectURL(url);
  useToast().add({
    title: "Downloaded",
    description: `${allPhones.value.length} phone numbers saved`,
    color: "green",
  });
}

function slicePhones() {
  if (phoneSliceCount.value && phoneSliceCount.value > 0) {
    const newSelection: Record<string, boolean> = {};
    let count = 0;
    for (
      let i = 0;
      i < users.value.length && count < phoneSliceCount.value;
      i++
    ) {
      const user = users.value[i];
      if (user.phone && user.sms_enabled) {
        newSelection[i] = true;
        count++;
      }
    }
    rowSelection.value = newSelection;
    manualPhones.value = manualPhones.value.slice(
      0,
      Math.max(0, phoneSliceCount.value - count),
    );
    useToast().add({
      title: "Sliced",
      description: `Taking first ${phoneSliceCount.value} phones`,
      color: "green",
    });
  }
}

function prevPage() {
  if (offset.value > 0) {
    offset.value -= limit.value;
    search();
  }
}
function nextPage() {
  if (offset.value + limit.value < totalCount.value) {
    offset.value += limit.value;
    search();
  }
}

function actionItems(row: User) {
  return [
    [
      {
        label: "View Profile",
        icon: "i-heroicons-eye",
        onSelect: () => navigateTo(`/users/${row.id}`),
      },
    ],
    [
      {
        label: "Copy Phone",
        icon: "i-heroicons-clipboard",
        onSelect: () => navigator.clipboard.writeText(row.phone || ""),
      },
    ],
    // [
    //   {
    //     label: "Add to Manual",
    //     icon: "i-heroicons-phone-plus",
    //     onSelect: () => {
    //       if (row.phone) {
    //         manualPhones.value.push({ phone: row.phone, name: row.name });
    //         useToast().add({
    //           title: "Added",
    //           description: "Phone added to manual",
    //           color: "success",
    //         });
    //       }
    //     },
    //   },
    // ],
  ];
}

// Watchers
watch([sortBy, sortOrder], () => {
  sortState.value = [{ id: sortBy.value, desc: sortOrder.value === "desc" }];
  offset.value = 0;
  search();
});
watch([limit], () => {
  offset.value = 0;
  search();
});
watch(
  filters,
  () => {
    offset.value = 0;
    useDebounceFn(() => search(), 500)();
  },
  { deep: true },
);

// Initialize
onMounted(() => {
  if (props.initialFilters)
    filters.value = { ...filters.value, ...props.initialFilters };
  search();
});
</script>
