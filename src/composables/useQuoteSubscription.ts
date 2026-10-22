import { onBeforeUnmount, onMounted, watch, type Ref } from 'vue'
import { useQuotesStore } from '@/stores/quotes'

export function useQuoteSubscription(symbols: Ref<string[]> | (() => string[])) {
  const store = useQuotesStore()
  let release: (() => void) | undefined
  const value = () => typeof symbols === 'function' ? symbols() : symbols.value
  function resubscribe() { release?.(); release = store.subscribe(value()) }
  onMounted(resubscribe)
  if (typeof symbols !== 'function') watch(symbols, resubscribe)
  onBeforeUnmount(() => release?.())
  return store
}
