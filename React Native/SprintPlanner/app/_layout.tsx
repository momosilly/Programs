import { Slot, useRouter } from "expo-router";
import { useEffect } from "react";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { getAuthKey } from "../src/storage/keys";

export default function RootLayout() {
    const router = useRouter();

    useEffect(() => {
        const checkAuth = async () => {
            const token = await AsyncStorage.getItem(getAuthKey("access_token"));
            if (!token) {
                router.push("/(modals)/signup");
            }
        };
        checkAuth();
    }, []);

    return <Slot />
}