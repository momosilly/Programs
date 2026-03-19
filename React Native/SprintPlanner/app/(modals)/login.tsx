import { useState } from "react";
import { View, TextInput, Button, Text, Alert, StyleSheet, Pressable, Platform } from 'react-native'
import { useRouter } from "expo-router";
import { login } from "../../src/api";
import { getUserFromToken } from "../../src/auth";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { getAuthKey } from "../../src/storage/keys";
import { SafeAreaView } from "react-native-safe-area-context";

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
        <SafeAreaView style={styles.container}>
            <Text style={{ fontSize: 25, fontWeight: "bold", alignSelf: 'center', marginBottom: 20 }}>Login</Text>

            <TextInput 
                placeholder="Email"
                value={email}
                onChangeText={setEmail}
                style={styles.input}
            />
            <TextInput 
                placeholder="Password"
                secureTextEntry
                value={password}
                onChangeText={setPassword}
                style={styles.input}
            />

            <Pressable 
                onPress={handleLogin} 
                style={({pressed}) => [styles.pressable, pressed && styles.pressablePressed]}
            >
                <Text style={styles.pressableText}>Login</Text>
            </Pressable>
            <Pressable 
                onPress={() => router.push("/(modals)/signup")}
            >
                <Text style={{ fontSize: 18, textAlign: 'center', marginVertical: 20 }}>Don't have an account? <Text style={{color: 'blue'}}>Sign up</Text></Text>
            </Pressable>
        </SafeAreaView>
    )
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        marginHorizontal: 30,
        marginVertical: '60%'
    },
    input: {
        paddingVertical: Platform.OS === "android" ? 12 : 10,
        paddingHorizontal: 14,
        marginVertical: 10,
        backgroundColor: "#fff",
        fontSize: Platform.OS === "android" ? 16 : 17,

        ...(Platform.OS === "android"
        ? {
            borderRadius: 6,
            borderWidth: 1,
            borderColor: "#ccc",
            elevation: 1,
            }
        : {
            borderRadius: 10,
            borderWidth: StyleSheet.hairlineWidth,
            borderColor: "#ccc",
            }),

    },
    pressable: {
        marginTop: 20,
        paddingTop: 3,
        paddingBottom: 3,
        alignItems: 'center',
        alignSelf: 'center',
        borderColor: '#1b6cef',
        borderStyle: 'solid',
        borderWidth: 1,
        borderRadius: 10,
        backgroundColor: '#1b6cef',
        width: 240,

        ...(Platform.OS === 'android'
            ? {
                elevation: 2
            }
            : {
                borderWidth: StyleSheet.hairlineWidth
            }
        ) 
    },
    pressableText: {
        color: "#fff",
        fontSize: 18,
        textAlign: 'center'
    },
    pressablePressed: {
        opacity: Platform.OS === 'ios' ? 0.5 : 1,
        transform: Platform.OS === 'android' ? [{ scale: 0.97 }] : undefined
    },
})