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

export const signup = async ({name, email, password}: SignupPayload) => {
    const response = await fetch("http://10.0.2.2:5000/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body:JSON.stringify({ name, email, password })
    });

    const data = await response.json();
    return data;
};

export const login = async ({email, password}: LoginPayload) => {
    const response = await fetch("http://10.0.2.2:5000/login", {
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
    if (!refreshToken) return null;

    const response = await fetch("http://10.0.2.2:5000/refresh", {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${refreshToken}`
        }
    });

    if (!response.ok) return null;

    const data = await response.json();
    await AsyncStorage.setItem(getAuthKey("access_token"), data.access_token);
    return data.access_token;
};

export const authFetch = async(url: string, options: RequestInit = {}) => {
    let accessToken = await getAccessToken();

    const doRequest = async (token?: string) => {
        const response = await fetch(url, {
            ...options,
            headers: {
                ...(options.headers || {}),
                "Authorization": token ? `Bearer ${token}` : ""
            }
        });

        let data: any = null;
        try {
            data = await response.json();
        } catch {}

        if (response.status === 401 && data?.msg === "Token has expired") {
            const newToken = await refreshAccessToken();
            if (!newToken) {
                await AsyncStorage.multiRemove([getAuthKey("access_token"), getAuthKey("refresh_token")]);
                Alert.alert("Session expired", "Please log in again.");
                throw new Error("Token expired");
            }
            const retryResponse = await fetch(url, {
                ...options,
                headers: {
                    ...(options.headers || {}),
                    "Authorization": `Bearer ${newToken}`
                }
            });
            const retryData = await retryResponse.json();
            return { response: retryResponse, data: retryData }
        }

        return { response: response, data };
    };

    return doRequest(accessToken || undefined)
};

    export const submitRequest = async ({ text, startDate, deadline }: submitFetch) => {
    const { response, data } = await authFetch("http://10.0.2.2:5000/submit", {
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
    const token = await AsyncStorage.getItem(getAuthKey('access_token'));

    if (!token) {
        console.log("No token found");
        return [];
    }

    const response = await fetch("http://10.0.2.2:5000/projects", {
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });

    const data = await response.json();
    console.log(data);
    return data;
}

export const logout = async () => {
  await AsyncStorage.multiRemove([getAuthKey("access_token"), getAuthKey("refresh_token")]);
};

export const getProject = async (id: number, token: string) => {
    const response = await fetch(`http://10.0.2.2:5000/projects/${id}`, {
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });

    return response.json()
}

export const updateStatus = async (id: number, data: any, token: string) => {
    const response = await fetch (`http://10.0.2.2:5000/projects/${id}/status`, {
        method: "PATCH",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(data)
    });
    
    return response.json();
}