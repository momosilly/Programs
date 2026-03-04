import AsyncStorage from "@react-native-async-storage/async-storage";
import { jwtDecode } from "jwt-decode";
import { getAuthKey } from "./storage/keys";

export async function getUserFromToken() {
    const token = await AsyncStorage.getItem(getAuthKey("token"));
    if (!token) return null;

    try {
        const decoded: any = jwtDecode(token);

        return {
            user_id: parseInt(decoded.sub),
            is_admin: decoded.is_admin
        };
    } catch (e) {
        console.log("Failed to decode token:", e);
        return null;
    }
};