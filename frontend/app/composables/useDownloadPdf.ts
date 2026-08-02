import { useAuthStore } from '~/stores/auth'
import { useNotification } from '~/composables/useNotification'

export function useDownloadPdf() {
  const auth  = useAuthStore()
  const notif = useNotification()
  const downloading = ref(false)

  async function downloadPdf(studyId: string, patientName = '') {
    downloading.value = true
    try {
      const blob = await $fetch<Blob>(`/api/reports/${studyId}`, {
        responseType: 'blob',
        headers: { Authorization: `Bearer ${auth.accessToken}` },
      })
      const url = URL.createObjectURL(blob)
      const a   = document.createElement('a')
      a.href     = url
      a.download = `reporte-${patientName ? patientName.replace(/\s+/g, '-').toLowerCase() + '-' : ''}${studyId.slice(0, 8)}.pdf`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch (err: unknown) {
      const e = err as { data?: { message?: string } }
      notif.error('Error al descargar PDF', e?.data?.message ?? 'Intenta de nuevo')
    } finally {
      downloading.value = false
    }
  }

  return { downloadPdf, downloading }
}
