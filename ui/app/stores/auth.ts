import { defineStore } from 'pinia'

export const useAuthStore = defineStore('app', {
  state: () => ({
    count: 0,
    ongoingSMS:{},
    message:"" as String,
    history:[]
  }),

  getters: {
    doubleCount: (state) => state.count * 2
  },

  actions: {
    increment() {
      this.count++
    }
  }
})