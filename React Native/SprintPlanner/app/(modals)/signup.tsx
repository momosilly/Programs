import { useEffect, useState } from "react";
import { View, Text, TextInput, Button, BackHandler, Alert, StyleSheet, Platform, Pressable } from 'react-native'
import { useRouter } from "expo-router";
import { signup } from "../../src/api";
import { getUserFromToken } from "../../src/auth";
import { SafeAreaView } from "react-native-safe-area-context";

export default function SignupModal() {
    const router = useRouter();
    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    const handleSignup = async () => {
        const result = await signup({ name, email, password });
        if (result?.token) {
            const user = await getUserFromToken();
            router.dismissAll();
            router.replace(user?.is_admin ? '/(tabs)/admin' : '/(tabs)/project');
        } else {
            console.log('Signup failed:', result.error);
            Alert.alert("Signup failed", result.error);
        }
    };

    useEffect(() => {
        const onBackPress = () => {
            return true
        };

        const subscription = BackHandler.addEventListener(
            'hardwareBackPress',
            onBackPress
        );

        return () => subscription.remove();
    } ,[])

    return (
        <SafeAreaView style={styles.container}>
            <Text style={{ fontSize: 25, fontWeight: "bold", alignSelf: 'center', marginBottom: 20 }}>Signup</Text>

            <TextInput 
                placeholder="Name"
                value={name}
                onChangeText={setName}
                style={styles.input}
            />
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
                onPress={handleSignup}
                style={styles.pressable}
            >
                <Text style={styles.pressableText}>Sign up</Text>
            </Pressable>
            <Pressable
                onPress={() => router.push("/(modals)/login")}
            >
                <Text style={{ fontSize: 18, textAlign: 'center', marginVertical: 20 }}>Already have an account? <Text style={{ color: 'blue' }}>Login</Text></Text>
            </Pressable>
        </SafeAreaView>
    );
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