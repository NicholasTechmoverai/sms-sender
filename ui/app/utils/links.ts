import type { NavigationMenuItem } from '@nuxt/ui'

export const navLinks: NavigationMenuItem[] = [{
  label: 'Home',
  icon: 'i-lucide-home',
  to: '/'
}, {
  label: 'Sms',
  icon: 'i-lucide-message-circle',
  to: '/sms'
}, {
  label: 'WhatsApp',
  icon: 'i-simple-icon-whatsapp',
  to: '/whatsapp'
}, {
  label: 'About',
  icon: 'i-lucide-info',
  to: '/about'
}]
