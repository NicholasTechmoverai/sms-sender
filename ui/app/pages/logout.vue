<template>
  <div class="min-h-screen flex items-center justify-center">
    <p class="text-gray-600">Signing out...</p>
  </div>
</template>

<script setup lang="ts">
const authStore = useAuthStore()
const router = useRouter()

onMounted(async () => {
  authStore.logout()
  await router.push('/login')
})
</script>