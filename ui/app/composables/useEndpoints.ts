export const useEndpoints = () => {
    const apiBase = useAppConfig().site.apiBase ? `${useAppConfig().site.apiBase}` : 'http://localhost:8001'
    const base = `${apiBase}/api/v1`
    return {
        auth: {
            login: `${base}/auth/login`,
            register: `${base}/auth/register`,
            me: `${base}/auth/me`
        },
        sms: {
            get: `${base}/sms`,
            send: `${base}/sms`,
            balance: `${base}/sms/balance`
        },
        users: {
            search: `${base}/users/search`,
        },
        data: {
            people: `${base}/data/people`,
            person: (id: number | string) => `${base}/data/people/${id}`,
            departments: `${base}/data/departments`,
            expertiseLevels: `${base}/data/expertise-levels`
        }
    }
}