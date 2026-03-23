<template>
  <div class="min-h-screen flex items-center justify-center">
    <p class="text-gray-600">Signing out...</p>
  </div>
</template>

<script setup lang="ts">
const authStore = useAuthStore()
const router = useRouter()
useSeoMeta({
  title: "Logging out ...",
  ogTitle: "Logging out ...",
  description: "About to logout",
  ogDescription: "About to logout"
})
onMounted(async () => {
  authStore.logout()
  await router.push('/login')
})
</script>