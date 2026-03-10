import { useState } from "react";
import { View, TextInput, Button, Text, Alert } from 'react-native'
import { useRouter } from "expo-router";
import { login } from "../../src/api";
import { getUserFromToken } from "../../src/auth";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { getAuthKey } from "../../src/storage/keys";

export default function LoginModal() {
    const router = useRouter();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    const handleLogin = async () => {
        const result = await login({ email, password });
        if (result?.access_token && result?.refresh_token) {
            await AsyncStorage.setItem(getAuthKey("access_token"), result.access_token);
            await AsyncStorage.setItem(getAuthKey("refresh_token"), result.refresh_token);

            const user = await getUserFromToken();
            router.dismissAll();
            router.replace(user?.is_admin ? '/(tabs)/admin' : '/(tabs)/project');
        } else {
            console.log('Login failed:', result.error);
            Alert.alert('Login failed', result.error);
        }
    };

    return (
        <View style={{ padding: 20 }}>
            <Text style={{ fontSize: 22, fontWeight: "bold" }}>Login</Text>

            <TextInput 
                placeholder="Email"
                value={email}
                onChangeText={setEmail}
                style={{ marginVertical: 10 }}
            />
            <TextInput 
                placeholder="Password"
                secureTextEntry
                value={password}
                onChangeText={setPassword}
                style={{ marginVertical: 10 }}
            />

            <Button title="Login" onPress={handleLogin} />
            <Button title="Don't have an account? Signup" onPress={() => router.push("/(modals)/signup")} />
        </View>
    )
}