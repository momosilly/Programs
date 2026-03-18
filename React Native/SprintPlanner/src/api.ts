import AsyncStorage from "@react-native-async-storage/async-storage";
import { getAuthKey } from "./storage/keys";
import { Alert } from "react-native";

interface LoginPayload {
    email: string
    password: string
}

interface SignupPayload extends LoginPayload {
    name: string
}

interface submitFetch {
    text: string
    startDate: string
    deadline: string
}

const API_URL = 'http://10.0.2.2:5000';

export const signup = async ({name, email, password}: SignupPayload) => {
    const response = await fetch(`${API_URL}/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body:JSON.stringify({ name, email, password })
    });

    const data = await response.json();
    return data;
};

export const login = async ({email, password}: LoginPayload) => {
    const response = await fetch(`${API_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
    });

    const data = await response.json();
    if (data.access_token && data.refresh_token) {
        await AsyncStorage.setItem(getAuthKey("access_token"), data.access_token);
        await AsyncStorage.setItem(getAuthKey("refresh_token"), data.refresh_token);
    }

    return data;
};

const getAccessToken = async () => {
    return AsyncStorage.getItem(getAuthKey("access_token"));
};

const getRefreshToken = async () => {
    return AsyncStorage.getItem(getAuthKey("refresh_token"));
};

const refreshAccessToken = async () => {
    const refreshToken = await getRefreshToken();
    console.log("Attempting refresh with token:", refreshToken ? "✓ exists" : "✗ missing");
    if (!refreshToken) return null;

    const response = await fetch(`${API_URL}/refresh`, {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${refreshToken}`
        }
    });

    console.log("Refresh response status:", response.status);
    if (!response.ok) {
        const errorData = await response.json();
        console.log("Refresh failed:", errorData);
        // 422 means refresh token is invalid/expired - don't retry
        if (response.status === 422) {
            await AsyncStorage.multiRemove([getAuthKey("access_token"), getAuthKey("refresh_token")]);
        }
        return null;
    }

    const data = await response.json();
    console.log("Refresh succeeded, got token:", data?.access_token ? "✓ yes" : "✗ no");
    if (data?.access_token) {
        await AsyncStorage.setItem(getAuthKey("access_token"), data.access_token);
        return data.access_token;
    }

    return null;
};

export const authFetch = async(url: string, options: RequestInit = {}) => {
    let accessToken = await getAccessToken();
    if (!accessToken) {
        accessToken = await refreshAccessToken();
    }

    const buildHeaders = (token?: string) => ({
        ...(options.headers || {}),
        ...(token ? { Authorization: `Bearer ${token}` } : {})
    });

    const doRequest = async (token?: string) => {
        const response = await fetch(url, {
            ...options,
            headers: buildHeaders(token)
        });

        let data: any = null;
        try {
            data = await response.json();
        } catch {}

        const shouldRefresh =
            response.status === 401 &&
            (data?.msg === "Token has expired" || data?.msg === "Missing Authorization Header");

        if (shouldRefresh) {
            const newToken = await refreshAccessToken();
            if (!newToken) {
                // Refresh failed - clear tokens and return 401
                await AsyncStorage.multiRemove([getAuthKey("access_token"), getAuthKey("refresh_token")]);
                return { response, data };
            }

            const retryResponse = await fetch(url, {
                ...options,
                headers: buildHeaders(newToken)
            });
            const retryData = await retryResponse.json();
            return { response: retryResponse, data: retryData };
        }

        return { response, data };
    };

    return doRequest(accessToken || undefined);
};

    export const submitRequest = async ({ text, startDate, deadline }: submitFetch) => {
    const { response, data } = await authFetch(`${API_URL}/submit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
        learning_objectives: text,
        start_date: startDate,
        deadline: deadline
        })
    });

    if (!response.ok) {
        Alert.alert("Error", data?.error || data?.msg || "Something went wrong");
        return;
    }

    Alert.alert("Success", "Project submitted!");
    return data;
    };

export const fetchRequests = async () => {
    const { data } = await authFetch(`${API_URL}/projects`);

    console.log(data);
    return data;
};

export const logout = async () => {
  await AsyncStorage.setItem(getAuthKey("manual_logout"), "true");
  await AsyncStorage.multiRemove([getAuthKey("access_token"), getAuthKey("refresh_token")]);
};

export const getProject = async (id: number) => {
    const { data } = await authFetch(`${API_URL}/projects/${id}`);

    console.log(data);
    return data;
}

export const updateStatus = async (id: number, body: any) => {
    const { data } = await authFetch(`${API_URL}/projects/${id}/status`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
    });

    return data;
};