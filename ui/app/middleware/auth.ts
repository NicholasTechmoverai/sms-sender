export default defineNuxtRouteMiddleware(async (to) => {
  const authStore = useAuthStore()

  // Client-only init (localStorage not available on server)
  if (process.client && !authStore.isAuthenticated) {
    await authStore.initializeAuth()
  }

  // If not authenticated and trying to access protected route
  if (!authStore.isLoggedIn && to.path.startsWith('/sms')) {
    return navigateTo('/login')
  }

  // If authenticated and trying to access login/register, redirect to sms
  if (authStore.isLoggedIn && (to.path === '/login' || to.path === '/register')) {
    return navigateTo('/sms')
  }
})