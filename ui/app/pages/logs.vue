<template>
  <div>
    <UPageCard title="Comming soon..." spotlight/>
    <UButton label="Comming soon..." />
  </div>
</template>

<script lang="ts" setup>
import { definePageMeta } from '#imports'

definePageMeta({
  middleware: 'auth'
})

</script>

<style>

</style>