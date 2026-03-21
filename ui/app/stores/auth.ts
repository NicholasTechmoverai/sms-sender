import { defineStore } from 'pinia'

export interface User {
  id: number
  username: string
  email: string
  is_active: boolean
  is_admin: boolean
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as User | null,
    token: null as string | null,
    isAuthenticated: false,
    ongoingSMS: {},
    message: "" as String,
    history: []
  }),

  getters: {
    isLoggedIn: (state) => state.isAuthenticated && !!state.token
  },

  actions: {
    async login(username: string, password: string) {
      try {
        const { post } = useApi()
        const endpoints = useEndpoints()

        const formData = new URLSearchParams()
        formData.append('username', username)
        formData.append('password', password)

        const response: any = await post(
          endpoints.auth.login,
          formData,
          false,
          { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
        )

        if (!response?.access_token) {
          throw new Error('Auth token not returned from server')
        }

        this.token = response.access_token
        this.isAuthenticated = true

        // Persist token
        if (process.client) {
          localStorage.setItem('auth_token', this.token)
        }

        // Fetch user profile
        await this.fetchUser()

        return { success: true, access_token: this.token }
      } catch (error: any) {
        this.logout()
        return { success: false, error: error?.message || 'Login failed' }
      }
    },

    async register(username: string, email: string, password: string) {
      try {
        const { post } = useApi()
        const endpoints = useEndpoints()
        const user = await post(endpoints.auth.register, {
          username,
          email,
          password
        }, false)

        // Auto login after registration
        return await this.login(username, password)
      } catch (error) {
        return { success: false, error: error.message || 'Registration failed' }
      }
    },

    async fetchUser() {
      if (!this.token) {
        this.logout()
        return false
      }

      try {
        const { get } = useApi()
        const endpoints = useEndpoints()
        const user = await get(endpoints.auth.me,{}, true)

        if (!user) {
          throw new Error('User profile unavailable')
        }

        this.user = user
        this.isAuthenticated = true
        return true
      } catch (error) {
        this.logout()
        return false
      }
    },

    logout() {
      this.user = null
      this.token = null
      this.isAuthenticated = false

      if (process.client) {
        localStorage.removeItem('auth_token')
      }
    },

    async initializeAuth() {
      if (process.client) {
        const token = localStorage.getItem('auth_token')
        if (token) {
          this.token = token
          this.isAuthenticated = true
          await this.fetchUser()
        }
      }
    }
  }
})