import { useState } from "react";
import { View, Text, TextInput, Button } from 'react-native'
import { useRouter } from "expo-router";
import { signup } from "../../src/api";
import { getUserFromToken } from "../../src/auth";

export default function SignupModal() {
    const router = useRouter();
    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    const handleSignup = async () => {
        const result = await signup({ name, email, password });
        if (result?.token) {
            const user = await getUserFromToken();
            router.replace(user?.is_admin ? '/(tabs)/admin' : '/(tabs)/project');
        } else {
            console.log('Login failed:', result.error);
        }
    };

    return (
        <View style={{ padding: 20 }}>
            <Text style={{ fontSize: 22, fontWeight: "bold" }}>Signup</Text>

            <TextInput 
                placeholder="Name"
                value={name}
                onChangeText={setName}
                style={{ marginVertical: 10 }}
            />
            <TextInput 
                placeholder="Email"
                value={email}
                onChangeText={setEmail}
                style={{ marginVertical: 10 }}
            />
            <TextInput 
                placeholder="Password"
                value={password}
                onChangeText={setPassword}
                style={{ marginVertical: 10 }}
            />

            <Button title="Signup" onPress={handleSignup} />
            <Button title="Already have an account? Login" onPress={() => router.push("/(modals)/login")} />
        </View>
    );
}