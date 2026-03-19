import React from "react";
import { useLocalSearchParams, useSegments, useRouter } from "expo-router";
import { useEffect, useState } from "react";
import { View, Text, Button, StyleSheet, Pressable, BackHandler } from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { getProject, updateStatus } from "../../src/api";
import { getUserFromToken } from "../../src/auth";
import { getAuthKey } from "../../src/storage/keys";
import { SafeAreaView } from "react-native-safe-area-context";
import { Platform } from "react-native";

export default function projectDetail() {
    interface Project {
    id: number
    name: string
    learning_objectives: string
    start_date: string
    deadline: string
    user_id: number
    };

    type myPressable = {
        title: string,
        onPress: any,
        isDisabled: any
    }

    const MyPressable = ({ title, onPress, isDisabled }: myPressable)  => {
            return (
                <Pressable
                    onPress={onPress}
                    disabled={isDisabled}
                    style={({ pressed }) => [
                    styles.pressable,
                    isDisabled ? styles.pressableDisabled : (pressed && styles.pressablePressed)
                    ]}
                >
                <Text style={[styles.pressableText, isDisabled && styles.pressableTextDisabled]}>
                    {title}
                </Text>
            </Pressable>
        );
    };


    const { id } = useLocalSearchParams();
    const [project, setProject] = useState<Project | null>(null);
    const [status, setStatus] = useState<any | null>(null);
    const [name, setName] = useState<string | null>(null);
    const [isAdmin, setIsAdmin] = useState(false);
    const segments = useSegments();
    const router = useRouter();

    useEffect(() => {
        async function load() {
            const user = await getUserFromToken();
            setIsAdmin(user?.is_admin ?? false);

            const data = await getProject(Number(id));
            setProject(data.project);
            setStatus(data.status);
            setName(data.name)
        }

        load();

        if (segments.includes('[id]') && segments.includes('projects')) {

            const onBackPress = () => {
                isAdmin ? router.replace('/admin') : router.replace('/submitted');
                return true;
            }

            const subscription = BackHandler.addEventListener(
                'hardwareBackPress',
                onBackPress
            )
            return () => subscription.remove();
        }
    }, [])

    async function handleUpdate(field: string) {
        const token = await AsyncStorage.getItem(getAuthKey("access_token"))
        if (!token) return;
        const updated = await updateStatus(Number(id), { [field]: true });

        const data = await getProject(Number(id));
        setStatus(data.status);
    }

    if (!project || !status || !name) return null;

    const getStatusLabel = (status: any) => {
        if (status.signed) return "Signed";
        if (status.handed_in) return "Handed in";
        if (status.approved) return "Approved";
        if (status.pending) return "Pending";
    }

    return (
        <SafeAreaView style={{ padding: 20, paddingTop: 10, flex: 1 }}>
            <View>
                {isAdmin && (
                    <Text style={[styles.title, {textTransform: 'capitalize'}]}>{name}'s Project</Text>
                )}
                <Text style={styles.text}><Text style={styles.spanText}>Objectives:</Text> {project.learning_objectives}</Text>
                <Text style={styles.text}><Text style={styles.spanText}>Start date:</Text> {project.start_date}</Text>
                <Text style={styles.text}><Text style={styles.spanText}>Deadline:</Text> {project.deadline}</Text>
                <Text style={styles.text}><Text style={styles.spanText}>Status:</Text> {getStatusLabel(status)}</Text>
            </View>

            {!isAdmin && (
                <MyPressable
                    title="Mark as handed in"
                    isDisabled={(!status.approved || status.signed || status.handed_in) ? true : false}
                    onPress={() => handleUpdate("handed_in")}
                />
            )}

            {isAdmin && (
                <>
                    <MyPressable
                        title="Approve"
                        isDisabled={(status.approved || status.signed || status.handed_in) ? true : false}
                        onPress={() => handleUpdate("approved")}
                    />
                    <MyPressable
                        title="Sign"
                        isDisabled={(status.approved || status.signed || !status.handed_in) ? true : false}
                        onPress={() => handleUpdate("signed")}
                    />
                </>
            )}
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    title: {
        fontSize: 20,
        fontWeight: 'bold',
        marginBottom: 17
    },
    text: {
        fontSize: 16
    },
    spanText: {
        fontWeight: 'bold'
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

    pressableDisabled: {
        backgroundColor: '#f0f2f5',
        borderColor: '#d7d7d7'
    },
    pressablePressed: {
        opacity: Platform.OS === 'ios' ? 0.5 : 1,
        transform: Platform.OS === 'android' ? [{ scale: 0.97 }] : undefined
    },
    pressableText: {
        color: '#fff',
        fontSize: 18
    },
    pressableTextDisabled: {
        color:'#797979',
        opacity: 0.4,
        ...(Platform.OS === "android" ? {elevation: 0} : {})
    }
})