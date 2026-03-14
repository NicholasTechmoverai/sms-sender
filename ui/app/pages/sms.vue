<script setup lang="ts">
import type { FormError, FormSubmitEvent } from "@nuxt/ui";

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
function getSmsUnits(balance: Balance, unitCost: number): number {
  const numericBalance = parseFloat(
    balance.remaining_balance.replace(/[^\d.]/g, ""),
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

// Country codes
const countryCodes = [
  { label: "+254 (Kenya)", value: "+254" },
  // { label: "+1 (USA)", value: "+1" },
  // { label: "+44 (UK)", value: "+44" },
  // { label: "+91 (India)", value: "+91" },
  // { label: "+61 (Australia)", value: "+61" },
  // { label: "+86 (China)", value: "+86" },
  // { label: "+81 (Japan)", value: "+81" },
  // { label: "+49 (Germany)", value: "+49" },
  // { label: "+33 (France)", value: "+33" },
  // { label: "+27 (South Africa)", value: "+27" },
];

// Methods
async function fetchBalance() {
  try {
    const res = await get<BalanceResponse>(endpoints.sms.balance);
    balance.value = res;
  } catch (error) {
    console.error("Failed to fetch balance:", error);
  }
}

function addPhoneNumber() {
  if (!state.phone_input?.trim()) return;

  const cleanedNumber = state.phone_input.trim().replace(/\s+/g, "");
  const fullNumber = `${state.country_code}${cleanedNumber}`;

  if (!state.phone_numbers.includes(fullNumber)) {
    state.phone_numbers.push(fullNumber);
    state.phone_input = "";
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

    // Refresh balance and reset form
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

// Lifecycle
onMounted(() => {
  fetchBalance();
});
</script>

<template>
  <div class="min-h-screen bg-neutral-50 dark:bg-neutral-900 py-8 px-4">
    <div class="max-w-2xl mx-auto">
      <!-- Header -->
      <div class="mb-6 px-4 sm:px-0">
        <div
          class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4"
        >
          <!-- Title -->
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
          <!-- Phone Numbers Section -->
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <label
                class="text-sm font-medium text-neutral-700 dark:text-neutral-300"
              >
                Recipients <span class="text-error-500">*</span>
              </label>
              <UBadge
                v-if="recipientCount > 0"
                color="primary"
                variant="soft"
                size="sm"
              >
                {{ recipientCount }}
                {{ recipientCount === 1 ? "recipient" : "recipients" }}
              </UBadge>
            </div>

            <!-- Selected Numbers -->
            <TransitionGroup
              v-if="state.phone_numbers.length > 0"
              tag="div"
              class="flex flex-wrap gap-2 mb-3"
              enter-active-class="transition duration-200 ease-out"
              enter-from-class="transform scale-95 opacity-0"
              enter-to-class="transform scale-100 opacity-100"
              leave-active-class="transition duration-150 ease-in"
              leave-from-class="transform scale-100 opacity-100"
              leave-to-class="transform scale-95 opacity-0"
            >
              <UBadge
                v-for="(number, index) in state.phone_numbers"
                :key="index"
                color="primary"
                variant="soft"
                size="lg"
                class="flex items-center gap-1 pr-1"
              >
                {{ number }}
                <UButton
                  color="neutral"
                  variant="ghost"
                  size="2xs"
                  icon="i-heroicons-x-mark-20-solid"
                  @click="removePhoneNumber(index)"
                  class="ml-1 hover:bg-error-500/10 hover:text-error-500"
                />
              </UBadge>
            </TransitionGroup>

            <!-- Phone Input Area -->
            <div class="flex gap-2">
              <USelectMenu
                v-model="state.country_code"
                :options="countryCodes"
                value-attribute="value"
                option-attribute="label"
                class="w-32"
                placeholder="Code"
                :disabled="loading"
              >
                <template #leading>
                  <UIcon
                    name="i-heroicons-phone"
                    class="w-4 h-4 text-neutral-400"
                  />
                </template>
              </USelectMenu>

              <UInput
                v-model="state.phone_input"
                placeholder="Enter phone number"
                class="flex-1"
                :disabled="loading"
                @keydown="handlePhoneInputKeydown"
              >
                <template #trailing>
                  <UButton
                    color="primary"
                    variant="ghost"
                    size="2xs"
                    icon="i-heroicons-plus-20-solid"
                    :disabled="!state.phone_input || loading"
                    @click="addPhoneNumber"
                  />
                </template>
              </UInput>
            </div>

            <!-- Helper text -->
            <p class="text-xs text-neutral-500 flex items-center gap-1">
              <UIcon name="i-heroicons-information-circle" class="w-4 h-4" />
              Press Enter or click + to add numbers
            </p>
          </div>

          <!-- Message Section -->
          <div class="space-y-3">
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
          <div class="flex items-center justify-between pt-2">
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

              <div
                v-if="recipientCount > 0"
                class="text-sm text-neutral-600 dark:text-neutral-400"
              >
                <span class="font-medium">{{ recipientCount }}</span>
                recipient{{ recipientCount > 1 ? "s" : "" }}
              </div>
            </div>

            <!-- Cost estimate -->
            <div
              v-if="smsCount > 0 && recipientCount > 0"
              class="text-xs text-neutral-500"
            >
              Est. cost: KES
              {{ (smsCount * recipientCount * SMS_UNIT_COST).toFixed(2) }}
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
              • Each SMS segment can contain up to
              {{ SMS_CHAR_LIMIT }} characters for standard messages
            </p>
            <p>
              • Unicode characters (emojis, special symbols) reduce the limit to
              {{ SMS_CHAR_LIMIT_UNICODE }} characters per segment
            </p>
            <p>• You will be charged for each SMS segment per recipient</p>
          </div>
        </div>
      </UCard>
    </div>
  </div>
</template>
