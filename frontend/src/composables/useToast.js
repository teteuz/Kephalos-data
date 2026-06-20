import { ref, readonly } from 'vue'

const toasts = ref([])
let _id = 0

export function useToast() {
  function add(message, type = 'info', duration = 3500) {
    const id = ++_id
    toasts.value.push({ id, message, type })
    setTimeout(() => remove(id), duration)
  }

  function remove(id) {
    const i = toasts.value.findIndex(t => t.id === id)
    if (i >= 0) toasts.value.splice(i, 1)
  }

  const success = (msg, dur) => add(msg, 'success', dur)
  const error = (msg, dur) => add(msg, 'error', dur)
  const info = (msg, dur) => add(msg, 'info', dur)

  return { toasts: readonly(toasts), add, remove, success, error, info }
}
