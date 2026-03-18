import { Slot, useRouter } from "expo-router";
import { useEffect, useRef } from "react";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { Alert } from "react-native";
import { getAuthKey } from "../src/storage/keys";

export default function RootLayout() {
    const router = useRouter();
    const hasShownAlert = useRef(false);

    useEffect(() => {
        const checkAuth = async () => {
            const token = await AsyncStorage.getItem(getAuthKey("access_token"));
            const manualLogout = await AsyncStorage.getItem(getAuthKey("manual_logout"));
            
            if (!token && !hasShownAlert.current) {
                if (!manualLogout) {
                    hasShownAlert.current = true;
                    Alert.alert("Session Expired", "Your session has expired. Please log in again.");
                }
            } else if (token) {
                hasShownAlert.current = false;
                await AsyncStorage.removeItem(getAuthKey("manual_logout"));
            }
        };
        
        checkAuth();

        // Poll for auth changes every 2 seconds
        const interval = setInterval(checkAuth, 2000);

        return () => {
            clearInterval(interval);
        };
    }, [router]);

    return <Slot />
}