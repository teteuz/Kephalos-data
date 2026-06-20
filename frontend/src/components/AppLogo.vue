<template>
  <img
    :src="isDark ? '/kephalos-logo-dark.png' : '/kephalos-logo-light.png'"
    alt="Kephalos"
    v-bind="$attrs"
  />
</template>

<script setup>
import { useTheme } from '../composables/useTheme'
defineOptions({ inheritAttrs: false })
const { isDark } = useTheme()
</script>
