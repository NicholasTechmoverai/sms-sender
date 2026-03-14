import { useAppConfig } from '#imports'
import { useAuthStore } from '~/stores/auth'
import type { ApiOptions, ApiError } from '~/types/api'

export const useApi = () => {
  const { site } = useAppConfig()


  const toast = useToast()
  const authStore = useAuthStore()
  const loading = ref(false)

  const buildHeaders = (
    options: ApiOptions,
    authenticate: boolean
  ): Record<string, string> => {
    const headers: Record<string, string> = { ...options.headers }

    if (authenticate && authStore.token) {
      headers.Authorization = `Bearer ${authStore.token}`
    }

    const isFormData = options.body instanceof FormData
    if (!isFormData && !headers['Content-Type']) {
      headers['Content-Type'] = 'application/json'
    }

    if (isFormData) {
      delete headers['Content-Type']
    }

    return headers
  }

  const handleError = (error: any, endpoint: string): never => {
    const apiError: ApiError = new Error(
      error?.data?.message ||
      error?.data?.detail ||
      error?.message ||
      'Request failed'
    )

    apiError.status = error?.status || 500
    apiError.response = error?.data

    // Prevent leaking endpoint / request info
    let message = apiError.message

    if (message.includes('Failed to fetch')) {
      message = 'Network error. Please check your connection.'
    }

    toast.add({
      title: 'Error',
      description: message,
      icon: 'i-heroicons-exclamation-triangle',
      color: 'error'
    })

    // keep detailed error only in console
    console.error(`API Error [${endpoint}]`, error)

    throw apiError
  }

  const request = async <T>(
    method: string,
    endpoint: string,
    body?: any,
    authenticate = false,
    options: ApiOptions = {}
  ): Promise<T> => {
    const url = new URL(`${endpoint}`)

    if (options.params) {
      Object.entries(options.params).forEach(([k, v]) => {
        if (v !== undefined && v !== null) {
          url.searchParams.append(k, String(v))
        }
      })
    }

    loading.value = true

    try {
      return await $fetch<T>(url.toString(), {
        method,
        body,
        headers: buildHeaders({ ...options, body }, authenticate),
        timeout: options.timeout
      })
    } catch (error: any) {
      handleError(error, endpoint)
    } finally {
      loading.value = false
    }
  }

  const get = <T>(
    endpoint: string,
    params?: Record<string, any>,
    authenticate = false,
    options: ApiOptions = {}
  ) =>
    request<T>('GET', endpoint, undefined, authenticate, {
      ...options,
      params
    })

  const post = <T>(
    endpoint: string,
    body?: any,
    authenticate = false,
    options: ApiOptions = {}
  ) => request<T>('POST', endpoint, body, authenticate, options)

  const put = <T>(
    endpoint: string,
    body?: any,
    authenticate = false,
    options: ApiOptions = {}
  ) => request<T>('PUT', endpoint, body, authenticate, options)

  const patch = <T>(
    endpoint: string,
    body?: any,
    authenticate = false,
    options: ApiOptions = {}
  ) => request<T>('PATCH', endpoint, body, authenticate, options)

  const del = <T>(
    endpoint: string,
    authenticate = false,
    options: ApiOptions = {}
  ) => request<T>('DELETE', endpoint, undefined, authenticate, options)

  const upload = <T>(
    endpoint: string,
    formData: FormData,
    authenticate = false,
    options: ApiOptions = {}
  ) => post<T>(endpoint, formData, authenticate, options)

  const download = async (
    endpoint: string,
    filename = 'download',
    params?: Record<string, any>,
    authenticate = false
  ) => {
    const blob = await get<Blob>(endpoint, params, authenticate, {
      responseType: 'blob'
    })

    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)
  }

  return {
    get,
    post,
    put,
    patch,
    del,
    upload,
    download,
    request,
    loading: readonly(loading)
  }
}

export type UseApiReturn = ReturnType<typeof useApi>