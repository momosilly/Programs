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

    if (data.token) {
    await AsyncStorage.setItem(getAuthKey('token'), data.token);
    }

    return data;
};

export const login = async ({email, password}: LoginPayload) => {
    const response = await fetch("http://10.0.2.2:5000/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
    });

    const data = await response.json();
    if (data.token) {
    await AsyncStorage.setItem(getAuthKey('token'), data.token);
    }

    return data;
};

export const submitRequest = async ({text, startDate, deadline}: submitFetch) => {
    const token = await AsyncStorage.getItem(getAuthKey('token'));

    if (!token) {
        console.log("No token found");
        return;
    }
    
    const response = await fetch("http://10.0.2.2:5000/submit", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
            learning_objectives: text,
            start_date: startDate,
            deadline: deadline
        })
    });
    
    try {
        const data = await response.json();
        console.log('Response status:', response.status, 'Data:', data);
        if (!response.ok) {
            Alert.alert('Error', data.error || "Something went wrong");
            return;
        }
        Alert.alert("Success", "Project submitted!");
        return data;
    } catch (error) {
        Alert.alert('Error', "Failed to parse response");
        console.log('Parse error:', error);
        return;
    }
};

export const fetchRequests = async () => {
    const token = await AsyncStorage.getItem(getAuthKey('token'));

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
  await AsyncStorage.removeItem(getAuthKey("token"));
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