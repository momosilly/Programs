import AsyncStorage from "@react-native-async-storage/async-storage";
import { getAuthKey } from "./storage/keys";

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
    
    const data = await response.json();
    console.log(data);
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