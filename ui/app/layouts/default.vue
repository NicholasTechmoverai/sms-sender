<script setup lang="ts">
import { useNavLinks } from '~/utils/links'

definePageMeta({
  middleware: 'auth'
})

</script>

<template>
  <div>
    <UContainer class="sm:border-x border-default pt-10">
      <AppHeader :links="useNavLinks()" />
      <slot />
      <AppFooter />
    </UContainer>
  </div>
</template>
