<script setup lang="ts">

const config = useAppConfig()
useSeoMeta({
  title: config.site.name,
  ogTitle: config.site.name,
  description: config.site.description,
  ogDescription: config.site.description
})

const isVisible = ref(false);

onMounted(() => {
  // Trigger animation after mount
  setTimeout(() => {
    isVisible.value = true;
  }, 100);
});
</script>

<template>
  <div class="min-h-screen font-mono text-gray-800 dark:text-gray-200">
    <div class="max-w-2xl mx-auto px-6 py-16">
      
      <!-- Main content with fade in -->
      <div 
        class="space-y-8"
        :class="[
          'transition-all duration-700 ease-out',
          isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
        ]"
      >
        
        <!-- Title -->
        <div class="space-y-2">
          <div class="text-sm text-gray-500 dark:text-gray-400">
            personal project / 2026
          </div>
          <h1 class="text-4xl font-light tracking-tight">
            sms sender
          </h1>
        </div>

        <!-- What it does -->
        <div class="space-y-4">
          <p class="text-lg leading-relaxed">
            a simple tool that lets me send sms messages to multiple people at once. 
            built because i needed a way to send quick updates to friends and family 
            without group chat chaos.
          </p>
          
          <p class="text-lg leading-relaxed">
            add phone numbers with country codes, type a message, and it shows you 
            how many sms segments it'll use (160 chars = 1 sms). handy for keeping 
            track of costs.
          </p>
        </div>

        <!-- Features list -->
        <div class="space-y-3">
          <h2 class="text-sm uppercase tracking-wider text-gray-500 dark:text-gray-400">
            what it does
          </h2>
          <ul class="space-y-2">
            <li class="flex items-start gap-3">
              <span class="text-gray-400">—</span>
              <span>multiple phone numbers, select country codes</span>
            </li>
            <li class="flex items-start gap-3">
              <span class="text-gray-400">—</span>
              <span>character counter, shows sms segments</span>
            </li>
            <li class="flex items-start gap-3">
              <span class="text-gray-400">—</span>
              <span>simple form, does one thing</span>
            </li>
          </ul>
        </div>

        <!-- Tech stack -->
        <div class="space-y-3">
          <h2 class="text-sm uppercase tracking-wider text-gray-500 dark:text-gray-400">
            built with
          </h2>
          <div class="flex flex-wrap gap-2">
            <span class="text-sm bg-gray-100 dark:bg-gray-800 px-3 py-1">vue</span>
            <span class="text-sm bg-gray-100 dark:bg-gray-800 px-3 py-1">nuxt ui</span>
            <span class="text-sm bg-gray-100 dark:bg-gray-800 px-3 py-1">tailwind</span>
            <span class="text-sm bg-gray-100 dark:bg-gray-800 px-3 py-1">typescript</span>
          </div>
        </div>

        <!-- Link to the tool -->
        <div class="pt-4">
          <a 
            href="/sms" 
            class="inline-flex items-center gap-2 text-sm border-b border-gray-300 dark:border-gray-600 pb-0.5 hover:border-gray-900 dark:hover:border-gray-300 transition-colors"
          >
            go to the sender
            <span class="text-lg leading-none">→</span>
          </a>
        </div>

        <!-- Footer note -->
        <div class="pt-8 text-xs text-gray-400">
          just a personal thing. works for what i need.
        </div>
      </div>
    </div>
  </div>
</template>

