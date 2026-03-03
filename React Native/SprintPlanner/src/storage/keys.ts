export const STORAGE_KEYS = {
    CACHE: '@cache',
    AUTH: '@auth'
};

export const getCacheKey = (endpoint: string): string => {
    return (`${STORAGE_KEYS.CACHE}:${endpoint}`)
};

export const getAuthKey = (endpoint: string): string => {
    return (`${STORAGE_KEYS.AUTH}:${endpoint}`)
};