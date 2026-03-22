import type { NavigationMenuItem } from '@nuxt/ui'
import { useAuthStore } from '~/stores/auth'

export const useNavLinks = () => {
  const authStore = useAuthStore()

  return computed(() => {
    const links: NavigationMenuItem[] = [
      {
        label: 'Home',
        icon: 'i-lucide-home',
        to: '/'
      },
      {
        label: 'Sms',
        icon: 'i-lucide-message-circle',
        to: '/sms'
      },
     
      {
        label: 'About',
        icon: 'i-lucide-info',
        to: '/about'
      },
        {
        label: 'Data',
        icon: 'i-lucide-book',
        to: '/data'
      }
    ]

    if (authStore.isLoggedIn) {
      links.push({
        label: 'Logout',
        icon: 'i-lucide-log-out',
        to: '/logout'
      })
    } else {
      links.push({
        label: 'Login',
        icon: 'i-lucide-log-in',
        to: '/login'
      })
    }

    return links
  })
}
