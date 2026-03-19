<script setup lang="ts">
import type { FormError, FormSubmitEvent } from "@nuxt/ui";
import { useAuthStore } from "../../stores/auth";
const stateStore = useAuthStore();
const openSelector = ref(false);
const showManualInput = ref(false);

// Constants
const SMS_CHAR_LIMIT = 160;
const SMS_CHAR_LIMIT_UNICODE = 70;
const SMS_UNIT_COST = 0.99;

// Types
interface BalanceResponse {
  remaining_balance: number;
  currency?: string;
}

interface SendSmsPayload {
  message: string;
  recipient: string[];
}

// State
const state = reactive({
  phone_numbers: [] as string[],
  phone_input: "",
  country_code: "+254",
  text: "",
});

const loading = ref(false);
const balance = ref<BalanceResponse | null>(null);
const toast = useToast();
const { get, post } = useApi();
const endpoints = useEndpoints();

// Computed properties
const characterCount = computed(() => state.text.length);

const hasUnicode = computed(() => /[^\u0000-\u00FF]/.test(state.text));

const smsLimit = computed(() =>
  hasUnicode.value ? SMS_CHAR_LIMIT_UNICODE : SMS_CHAR_LIMIT,
);

const smsCount = computed(() => {
  if (characterCount.value === 0) return 0;
  return Math.ceil(characterCount.value / smsLimit.value);
});

const smsRemaining = computed(() => {
  if (characterCount.value === 0) return smsLimit.value;
  const totalChars = smsCount.value * smsLimit.value;
  return totalChars - characterCount.value;
});

function getSmsUnits(balance: BalanceResponse, unitCost: number): number {
  const numericBalance = parseFloat(
    balance.remaining_balance.toString().replace(/[^\d.]/g, ""),
  );
  return Math.floor(numericBalance / unitCost);
}

const remainingSmsCount = computed(() => {
  if (!balance.value?.remaining_balance) return 0;
  return getSmsUnits(balance.value, SMS_UNIT_COST);
});

const canSend = computed(
  () =>
    state.phone_numbers.length > 0 &&
    state.text.trim().length > 0 &&
    !loading.value,
);

const recipientCount = computed(() => state.phone_numbers.length);

// Phone utilities
function formatPhoneNumber(phone: string) {
  if (!phone) return "";
  const cleaned = phone.replace(/\D/g, "");
  if (cleaned.length === 10)
    return `(${cleaned.slice(0, 3)}) ${cleaned.slice(3, 6)}-${cleaned.slice(6)}`;
  if (cleaned.length === 11 && cleaned.startsWith("1"))
    return `+1 (${cleaned.slice(1, 4)}) ${cleaned.slice(4, 7)}-${cleaned.slice(7)}`;
  return phone;
}

// Country codes
const countryCodes = [
  { label: "+254 (Kenya)", value: "+254" },
];

// Get display numbers (latest first, limited to 5)
const displayNumbers = computed(() => {
  // Show latest first (reverse order)
  const reversed = [...state.phone_numbers].reverse();
  return {
    latest: reversed.slice(0, 5),
    remaining: Math.max(0, state.phone_numbers.length - 5)
  };
});

// Manual phone handling
function addPhoneNumber() {
  if (!state.phone_input?.trim()) return;

  const cleanedNumber = state.phone_input.trim().replace(/\s+/g, "");
  const fullNumber = `${state.country_code}${cleanedNumber}`;

  if (!state.phone_numbers.includes(fullNumber)) {
    state.phone_numbers.push(fullNumber);
    state.phone_input = "";
    showManualInput.value = false;
    
    toast.add({
      title: "Number added",
      description: "Phone number added to recipients",
      color: "success",
      icon: "i-heroicons-check-circle",
    });
  } else {
    toast.add({
      title: "Duplicate number",
      description: "This phone number is already in the list",
      color: "warning",
      icon: "i-heroicons-exclamation-triangle",
    });
  }
}

function removePhoneNumber(index: number) {
  state.phone_numbers.splice(index, 1);
}

function handlePhoneInputKeydown(event: KeyboardEvent) {
  if (event.key === "Enter") {
    event.preventDefault();
    addPhoneNumber();
  }
}

// Stored phones handling
function addToRecipients(phone: any) {
  if (!state.phone_numbers.includes(phone.phone)) {
    state.phone_numbers.push(phone.phone);
    toast.add({
      title: "Added",
      description: "Phone added to recipients",
      color: "success"
    });
  } else {
    toast.add({
      title: "Duplicate",
      description: "Phone already in list",
      color: "warning"
    });
  }
}

function addAllToRecipients() {
  if (stateStore.ongoingSMS?.phones) {
    const newPhones = stateStore.ongoingSMS.phones
      .map(p => p.phone)
      .filter(phone => !state.phone_numbers.includes(phone));
    
    state.phone_numbers = [...state.phone_numbers, ...newPhones];
    
    toast.add({
      title: "Added",
      description: `${newPhones.length} phones added to recipients`,
      color: "success"
    });
  }
}

function removeStoredPhone(index: number) {
  if (stateStore.ongoingSMS?.phones) {
    const phoneToRemove = stateStore.ongoingSMS.phones[index];
    const updatedPhones = [...stateStore.ongoingSMS.phones];
    updatedPhones.splice(index, 1);
    
    // Update store
    stateStore.ongoingSMS = {
      ...stateStore.ongoingSMS,
      phones: updatedPhones,
      count: updatedPhones.length
    };
    
    // Also remove from recipients if present
    const recipientIndex = state.phone_numbers.findIndex(p => p === phoneToRemove.phone);
    if (recipientIndex !== -1) {
      state.phone_numbers.splice(recipientIndex, 1);
    }
    
    toast.add({
      title: "Removed",
      description: "Phone removed from store and recipients",
      color: "info"
    });
  }
}

function clearAllStored() {
  // Remove all stored phones from recipients
  if (stateStore.ongoingSMS?.phones) {
    const storedPhones = stateStore.ongoingSMS.phones.map(p => p.phone);
    state.phone_numbers = state.phone_numbers.filter(p => !storedPhones.includes(p));
  }
  
  // Clear store
  stateStore.ongoingSMS = { 
    phones: [], 
    count: 0, 
    timestamp: new Date().toISOString() 
  };
  
  toast.add({
    title: "Cleared",
    description: "All stored phones removed",
    color: "info"
  });
}

async function copySinglePhone(phone: string) {
  await navigator.clipboard.writeText(phone);
  toast.add({
    title: "Copied!",
    description: "Phone number copied",
    color: "green"
  });
}

// Load from store on mount
onMounted(() => {
  fetchBalance();
  if (stateStore.ongoingSMS?.phones?.length) {
    state.phone_numbers = stateStore.ongoingSMS.phones.map(p => p.phone);
  }
});

// Watch for store changes
watch(() => stateStore.ongoingSMS?.phones, (newPhones) => {
  if (newPhones) {
    // Sync recipients with store (add new ones, but don't remove manually added)
    const storePhoneNumbers = newPhones.map(p => p.phone);
    const currentNumbers = state.phone_numbers;
    
    // Add any new store phones not already in recipients
    const newNumbers = storePhoneNumbers.filter(p => !currentNumbers.includes(p));
    if (newNumbers.length) {
      state.phone_numbers = [...currentNumbers, ...newNumbers];
    }
  }
}, { deep: true });

// Methods
async function fetchBalance() {
  try {
    const res = await get<BalanceResponse>(endpoints.sms.balance);
    balance.value = res;
  } catch (error) {
    console.error("Failed to fetch balance:", error);
  }
}

function validate(state: Partial<typeof state>): FormError[] {
  const errors = [];

  if (!state.phone_numbers?.length) {
    errors.push({
      name: "phone_numbers",
      message: "At least one phone number is required",
    });
  }

  if (!state.text?.trim()) {
    errors.push({
      name: "text",
      message: "Message is required",
    });
  }

  return errors;
}

async function onSubmit(event: FormSubmitEvent<typeof state>) {
  if (!canSend.value) return;

  loading.value = true;

  const payload: SendSmsPayload = {
    message: state.text,
    recipient: state.phone_numbers,
  };

  try {
    const res = await post(endpoints.sms.send, payload);
    if (res?.status?.error) {
      toast.add({
        title: "Failed to send SMS",
        description: "",
        color: "error",
        icon: "i-heroicons-x-circle",
      });
      return;
    }

    toast.add({
      title: "SMS sent successfully",
      description: `Message sent to ${recipientCount.value} recipient(s) using ${smsCount.value} SMS segment(s)`,
      color: "success",
      icon: "i-heroicons-check-circle",
    });

    await fetchBalance();
    state.phone_numbers = [];
    state.text = "";
  } catch (error) {
    toast.add({
      title: "Failed to send SMS",
      description:
        error instanceof Error ? error.message : "Please try again later",
      color: "error",
      icon: "i-heroicons-x-circle",
    });
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="min-h-screen bg-neutral-50 dark:bg-neutral-900 py-8 lg:px-4">
    <div class="max-w-2xl mx-auto">
      <!-- Header -->
      <div class="mb-6 px-4 sm:px-0">
        <div
          class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4"
        >
          <div>
            <h1
              class="text-xl sm:text-2xl font-bold text-neutral-900 dark:text-white"
            >
              SMS Sender
            </h1>
            <p class="text-sm text-neutral-600 dark:text-neutral-400 mt-1">
              Send messages to multiple recipients via SMS
            </p>
          </div>

          <!-- Balance card -->
          <UPageCard spotlight class="border-none w-full sm:w-auto rounded-lg">
            <div class="text-right">
              <p
                class="text-xs font-medium text-primary-600 dark:text-primary-400"
              >
                Available Balance
              </p>
              <p
                class="text-lg sm:text-xl font-bold text-primary-700 dark:text-primary-300"
              >
                KES {{ balance?.remaining_balance?.toLocaleString() ?? 0 }}
              </p>
              <p class="text-xs text-primary-600 dark:text-primary-400">
                ≈ {{ remainingSmsCount }} SMS remaining
              </p>
            </div>
          </UPageCard>
        </div>
      </div>

      <!-- Main Form Card -->
      <UCard class="border-0 shadow-lg">
        <UForm
          :validate="validate"
          :state="state"
          class="space-y-6"
          @submit="onSubmit"
        >
          <!-- Recipients Section -->
          <div class="space-y-4">
            <!-- Header with actions -->
            <div class="flex items-center justify-between">
              <label class="text-sm font-medium text-neutral-700 dark:text-neutral-300">
                Recipients <span class="text-error-500">*</span>
                <span v-if="recipientCount" class="ml-2 text-xs text-neutral-500">
                  ({{ recipientCount }} selected)
                </span>
              </label>
              
              <div class="flex items-center gap-2">
                <UButton
                  size="xs"
                  color="neutral"
                  variant="ghost"
                  icon="i-heroicons-plus-circle"
                  @click="showManualInput = !showManualInput"
                >
                  {{ showManualInput ? 'Cancel' : 'Add Manual' }}
                </UButton>
                
                <UButton
                  size="xs"
                  color="primary"
                  variant="soft"
                  icon="i-heroicons-users"
                  @click="$router.push('/sms/selector')"
                >
                  Filter Select
                </UButton>
              </div>
            </div>

            <!-- Manual Input (collapsible) -->
            <div v-if="showManualInput" class="bg-neutral-50 dark:bg-neutral-800 rounded-lg p-4 transition-all">
              <div class="flex gap-2">
                <USelect
                  v-model="state.country_code"
                  :items="countryCodes"
                  class="w-32"
                  size="lg"
                />
                <UInput
                  v-model="state.phone_input"
                  placeholder="712345678"
                  class="flex-1"
                  size="lg"
                  @keydown="handlePhoneInputKeydown"
                />
                <UButton
                  color="primary"
                  variant="solid"
                  icon="i-heroicons-plus"
                  @click="addPhoneNumber"
                  :disabled="!state.phone_input"
                />
              </div>
              <p class="text-xs text-neutral-500 mt-2">
                Press Enter to add • Country code will be prepended automatically
              </p>
            </div>

            <!-- Stored Selection Summary -->
            <div v-if="stateStore.ongoingSMS?.phones?.length" class="flex items-center justify-between bg-primary-50 dark:bg-primary-900/20 rounded-lg p-3">
              <div class="flex items-center gap-2">
                <UIcon name="i-heroicons-check-badge" class="w-5 h-5 text-primary-500" />
                <div>
                  <span class="text-sm font-medium">{{ stateStore.ongoingSMS.phones.length }} numbers from filter</span>
                  <p class="text-xs text-neutral-500">Click to view or add individually</p>
                </div>
              </div>
              <div class="flex gap-2">
                <UButton
                  size="xs"
                  color="primary"
                  variant="soft"
                  @click="addAllToRecipients"
                >
                  Add All
                </UButton>
                <UModal v-model="openSelector">
                  <UButton size="xs" color="neutral" variant="ghost" icon="i-heroicons-eye">
                    View
                  </UButton>
                  <template #content>
                    <UCard class="w-full">
                      <template #header>
                        <div class="flex items-center justify-between">
                          <h3 class="text-lg font-semibold">
                            Filtered Numbers ({{ stateStore.ongoingSMS?.phones?.length || 0 }})
                          </h3>
                          <UButton
                            color="neutral"
                            variant="ghost"
                            icon="i-heroicons-x-mark"
                            @click="openSelector = false"
                          />
                        </div>
                      </template>
                      
                      <div class="max-h-96 overflow-y-auto space-y-2">
                        <div v-if="stateStore.ongoingSMS?.phones?.length">
                          <div
                            v-for="(phone, index) in stateStore.ongoingSMS.phones"
                            :key="index"
                            class="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg flex items-center justify-between"
                          >
                            <div class="flex-1">
                              <div class="font-mono text-sm">
                                {{ phone.formatted || formatPhoneNumber(phone.phone) }}
                              </div>
                              <div class="text-xs text-gray-500">
                                {{ phone.name || 'Unknown' }} • {{ phone.department || "N/A" }}
                              </div>
                            </div>
                            <div class="flex gap-1">
                              <UButton
                                size="xs"
                                color="primary"
                                variant="soft"
                                icon="i-heroicons-plus"
                                @click="addToRecipients(phone)"
                              />
                              <UButton
                                size="xs"
                                color="neutral"
                                variant="ghost"
                                icon="i-heroicons-clipboard"
                                @click="copySinglePhone(phone.phone)"
                              />
                              <UButton
                                size="xs"
                                color="error"
                                variant="ghost"
                                icon="i-heroicons-trash"
                                @click="removeStoredPhone(index)"
                              />
                            </div>
                          </div>
                        </div>
                        <div v-else class="text-center py-8 text-gray-500">
                          No numbers stored yet
                        </div>
                      </div>

                      <template #footer>
                        <div class="flex justify-between gap-2">
                          <UButton
                            color="error"
                            variant="soft"
                            size="sm"
                            @click="clearAllStored"
                          >
                            Clear All
                          </UButton>
                          <div class="flex gap-2">
                            <UButton
                              color="neutral"
                              variant="ghost"
                              @click="openSelector = false"
                            >
                              Close
                            </UButton>
                            <UButton
                              color="primary"
                              @click="$router.push('/sms/selector')"
                            >
                              Edit Filter
                            </UButton>
                          </div>
                        </div>
                      </template>
                    </UCard>
                  </template>
                </UModal>
              </div>
            </div>

            <!-- Recipients List - Shows latest first -->
            <div v-if="state.phone_numbers.length" class="mt-2">
              <div class="flex flex-wrap gap-2">
                <!-- Show latest 5 numbers -->
                <UBadge
                  v-for="(phone, idx) in displayNumbers.latest"
                  :key="phone"
                  color="primary"
                  variant="soft"
                  size="lg"
                  class="pl-3 pr-1 py-1.5"
                >
                  <span class="font-mono text-sm">{{ formatPhoneNumber(phone) }}</span>
                  <UButton
                    size="2xs"
                    color="neutral"
                    variant="ghost"
                    icon="i-heroicons-x-mark"
                    class="ml-1"
                    @click="removePhoneNumber(state.phone_numbers.length - 1 - idx)"
                  />
                </UBadge>
                
                <!-- Show remaining count if more than 5 -->
                <UBadge
                  v-if="displayNumbers.remaining > 0"
                  color="neutral"
                  variant="soft"
                  size="lg"
                  class="px-3 py-1.5 cursor-pointer"
                  @click="openSelector = true"
                >
                  +{{ displayNumbers.remaining }} more
                </UBadge>
              </div>
              
              <!-- Hint for viewing all -->
              <p v-if="displayNumbers.remaining > 0" class="text-xs text-neutral-500 mt-2">
                Showing latest {{ displayNumbers.latest.length }} of {{ state.phone_numbers.length }} • 
                <button class="text-primary-500 hover:underline" @click="openSelector = true">
                  Click to view all
                </button>
              </p>
            </div>

            <!-- Empty State -->
            <div v-else class="text-center py-6 border-2 border-dashed border-neutral-200 dark:border-neutral-700 rounded-lg">
              <UIcon name="i-heroicons-phone" class="w-8 h-8 mx-auto text-neutral-400" />
              <p class="mt-2 text-sm text-neutral-500">No recipients yet</p>
              <p class="text-xs text-neutral-400">Add manually or select from filters</p>
            </div>
          </div>

          <!-- Message Section -->
          <div class="space-y-3 pt-4 border-t border-neutral-200 dark:border-neutral-700">
            <div class="flex items-center justify-between">
              <label
                class="text-sm font-medium text-neutral-700 dark:text-neutral-300"
              >
                Message <span class="text-error-500">*</span>
              </label>

              <!-- Character and SMS stats -->
              <div class="flex items-center gap-3 text-xs">
                <div class="flex items-center gap-1">
                  <span class="text-neutral-500">Chars:</span>
                  <span
                    :class="
                      characterCount > 0
                        ? 'text-primary-600 font-medium'
                        : 'text-neutral-400'
                    "
                  >
                    {{ characterCount }}
                  </span>
                </div>
                <div class="w-px h-3 bg-neutral-200 dark:bg-neutral-700" />
                <div class="flex items-center gap-1">
                  <span class="text-neutral-500">SMS:</span>
                  <span
                    :class="
                      smsCount > 0
                        ? 'text-success-600 font-medium'
                        : 'text-neutral-400'
                    "
                  >
                    {{ smsCount }}
                  </span>
                </div>
                <div
                  v-if="characterCount > 0"
                  class="w-px h-3 bg-neutral-200 dark:bg-neutral-700"
                />
                <div v-if="characterCount > 0" class="flex items-center gap-1">
                  <span class="text-neutral-500">Remaining:</span>
                  <span class="text-warning-600 font-medium">{{
                    smsRemaining
                  }}</span>
                </div>
              </div>
            </div>

            <UTextarea
              v-model="state.text"
              :rows="5"
              placeholder="Type your message here..."
              :disabled="loading"
              class="w-full font-mono"
            />

            <!-- SMS Info Bar -->
            <div
              class="flex items-center justify-between p-2 bg-neutral-50 dark:bg-neutral-800 rounded-lg text-xs"
              :class="{
                'bg-success-50 dark:bg-success-950':
                  smsCount > 0 && smsCount <= 2,
                'bg-warning-50 dark:bg-warning-950': smsCount > 2,
              }"
            >
              <div class="flex items-center gap-2">
                <UIcon
                  :name="
                    hasUnicode
                      ? 'i-heroicons-language'
                      : 'i-heroicons-chat-bubble-left-right'
                  "
                  class="w-4 h-4 text-neutral-500"
                />
                <span class="text-neutral-600 dark:text-neutral-400">
                  {{ hasUnicode ? "Unicode message" : "Standard SMS" }}
                </span>
              </div>
              <span class="text-neutral-700 dark:text-neutral-300 font-medium">
                {{
                  smsCount === 0
                    ? "Start typing"
                    : `${smsCount} segment${smsCount > 1 ? "s" : ""}`
                }}
              </span>
            </div>
          </div>

          <!-- Action Area -->
          <div class="flex items-center justify-between pt-4 border-t border-neutral-200 dark:border-neutral-700">
            <div class="flex items-center gap-3">
              <UButton
                type="submit"
                color="primary"
                size="lg"
                :loading="loading"
                :disabled="!canSend"
              >
                <template #leading>
                  <UIcon name="i-heroicons-paper-airplane" class="w-5 h-5" />
                </template>
                {{ loading ? "Sending..." : "Send Message" }}
              </UButton>
            </div>

            <!-- Cost estimate -->
            <div
              v-if="smsCount > 0 && recipientCount > 0"
              class="text-sm text-neutral-600 dark:text-neutral-400"
            >
              <span class="font-medium">{{ recipientCount }}</span> recipient{{ recipientCount > 1 ? "s" : "" }} •
              <span class="font-mono">KES {{ (smsCount * recipientCount * SMS_UNIT_COST).toFixed(2) }}</span>
            </div>
          </div>
        </UForm>
      </UCard>

      <!-- Quick tips -->
      <UCard class="mt-4 bg-neutral-50 dark:bg-neutral-800 border-none">
        <div class="flex items-start gap-3">
          <UIcon
            name="i-heroicons-light-bulb"
            class="w-5 h-5 text-warning-500 flex-shrink-0 mt-0.5"
          />
          <div class="text-xs text-neutral-600 dark:text-neutral-400 space-y-1">
            <p>
              • Each SMS segment: {{ SMS_CHAR_LIMIT }} chars (standard) / {{ SMS_CHAR_LIMIT_UNICODE }} chars (Unicode)
            </p>
            <p>• Cost: KES {{ SMS_UNIT_COST }} per segment per recipient</p>
            <p>• Latest 5 numbers shown • Click "+X more" to view all</p>
            <p>• Numbers sync automatically when removed from store</p>
          </div>
        </div>
      </UCard>
    </div>
  </div>
</template>