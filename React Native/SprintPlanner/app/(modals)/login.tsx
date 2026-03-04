import { useState } from "react";
import { View, TextInput, Button, Text } from 'react-native'
import { useRouter } from "expo-router";
import { login } from "../../src/api";
import { getUserFromToken } from "../../src/auth";

export default function LoginModal() {
    const router = useRouter();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    const handleLogin = async () => {
        const result = await login({ email, password });
        if (result?.token) {
            const user = await getUserFromToken();
            router.replace(user?.is_admin ? '/(tabs)/admin' : '/(tabs)/project');
        } else {
            console.log('Login failed:', result.error);
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