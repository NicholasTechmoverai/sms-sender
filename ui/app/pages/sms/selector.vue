<template>
    <HandleUsers />
</template>
<script lang="ts" setup>
definePageMeta({
  middleware: 'auth'
})

useSeoMeta({
  title: "Select contacts",
  ogTitle: "Select contacts",
  description: "Select contacts from database",
  ogDescription: "Select contacts from database"
})
</script>
