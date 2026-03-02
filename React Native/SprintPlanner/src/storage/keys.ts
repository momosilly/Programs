export const STORAGE_KEYS = {
    CACHE: '@cache',
    LEARNING_OBJECTIVES: '@learning_objectives'
};

export const getCacheKey = (endpoint: string): string => {
    return (`${STORAGE_KEYS.CACHE}:${endpoint}`)
};

export const getLearningObjectivesKey = (endpoint: string): string => {
    return (`${STORAGE_KEYS.LEARNING_OBJECTIVES}:${endpoint}`)
};