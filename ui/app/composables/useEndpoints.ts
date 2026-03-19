export const useEndpoints = () => {
    const apiBase = useAppConfig().site.apiBase ? `${useAppConfig().site.apiBase}` : 'http://localhost:8000'
    const base = `${apiBase}/api/v1`
    return {
        sms: {
            get: `${base}/sms`,
            send: `${base}/sms`,
            balance: `${base}/sms/balance`
        },
        users: {
            search: `${base}/users/search`,
        }
    }
}