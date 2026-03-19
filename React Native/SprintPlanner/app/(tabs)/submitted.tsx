import { useState, useEffect } from "react";
import { View, Text, FlatList, Pressable, StyleSheet, Platform, Image } from "react-native";
import { fetchRequests, logout } from "../../src/api";
import { useLocalSearchParams, useRouter } from "expo-router";
import { DropdownMenu } from "../(components)/DropdownMenu";
import { MenuOption } from "../(components)/MenuOption";
import { getAuthKey } from "../../src/storage/keys";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { SafeAreaView } from "react-native-safe-area-context";

export default function Submitted() {
    const router = useRouter();
    const [projects, setProjects] = useState<any[]>([]);
    const [filter, setFilter] = useState<any | null>(null);
    const [visible, setVisible] = useState(false);
    const filteredProjects = filter ? projects.filter(p => p?.status?.[filter] === true) : projects;

    useEffect(() => {
    fetchRequests().then((data) => {
        console.log("Fetched data:", data);
        console.log("Is array:", Array.isArray(data));
        console.log("STATUS OF FIRST PROJECT:", data?.[0]?.status);
        setProjects(Array.isArray(data) ? data : []);
    });

    }, []);
    
    return (
        <SafeAreaView style={{ padding: 20, paddingTop: 10, marginBottom: 34, flex: 1 }}>
            <Text style={{ fontSize: 22, fontWeight: "bold", zIndex: 10}}>
                Your requests
            </Text>
            <View style={{alignItems: 'flex-end', paddingRight: 20, zIndex: 20, top: -20}}>
                <DropdownMenu
                    visible={visible}
                    handleOpen={() => setVisible(true)}
                    handleClose={() => setVisible(false)}
                    trigger={
                        <View style={styles.triggerStyle}>
                            <Text style={[styles.triggerText, {textTransform: 'capitalize'}]}>{filter ? filter : "Filter"}</Text>
                        </View>
                    }
                >
                    <MenuOption onSelect={() => {
                        setVisible(false)
                        setFilter("pending")
                    }}>
                        <Text>Pending</Text>
                    </MenuOption>
                    <MenuOption onSelect={() => {
                        setVisible(false)
                        setFilter("approved")
                    }}>
                        <Text>Approved</Text>
                    </MenuOption>
                    <MenuOption onSelect={() => {
                        setVisible(false)
                        setFilter("handed_in")
                    }}>
                        <Text>Handed in</Text>
                    </MenuOption>
                    <MenuOption onSelect={() => {
                        setVisible(false)
                        setFilter("signed")
                    }}>
                        <Text>Signed</Text>
                    </MenuOption>
                    <MenuOption onSelect={() => {
                        setVisible(false)
                        setFilter(null)
                    }}>
                        <Text>Show all</Text>
                    </MenuOption>
                </DropdownMenu>
            </View>
            <FlatList
                style={{ marginBottom: 70 }}
                contentContainerStyle={{paddingBottom: 16}}
                data={filteredProjects}
                keyExtractor={(item) => item.id.toString()}
                renderItem={({ item }) => (
                <Pressable onPress={() => router.push(`projects/${item.id}`)} style={({pressed}) => [styles.container, pressed && styles.pressablePressed]}>
                    <View style={{ marginVertical: 10 }}>
                        <Text style={{fontSize: 15}}>Objectives: {item.learning_objectives}</Text>
                    </View>
                </Pressable>
                )}
            />
            <Pressable 
                onPress={async () => {
                    await logout();
                    router.replace("/(modals)/login")
                }}
                style={[styles.pressable, {position: 'absolute', bottom: 80, left: 20, borderTopWidth: StyleSheet.hairlineWidth}]}
            >
                <Image 
                    source={require("../../assets/logout.png")}
                    style={{ height: 24, width: 24 }}
                />
            </Pressable>
        </SafeAreaView>
    )
}

const styles = StyleSheet.create({
    filter: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: '#f5fcff',
    },
    triggerStyle: {
        height: 38,
        backgroundColor: '#f5fcff',
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        width: 70,
        paddingHorizontal: 13,
        paddingVertical: 8,
        borderRadius: 5,
        borderColor: '#9f9f9f',
        borderStyle: 'solid',
        borderWidth: 1.5,
        ...(Platform.OS === 'android'
        ? {
            elevation: 2
        }
        : {
            borderWidth: StyleSheet.hairlineWidth
        }
        ) 
    },
    triggerText: {
        fontSize: 16,
    },
    pressable: {
        borderWidth: 1,
        borderColor: '#1b6cef',
        borderStyle: 'solid',
        borderRadius: 50,
        backgroundColor: '#1b6cef',
        padding: 10,
        width: 50,
        alignItems: 'center'
    },    
    pressablePressed: {
        opacity: Platform.OS === 'ios' ? 0.5 : 1,
        transform: Platform.OS === 'android' ? [{ scale: 0.97 }] : undefined
    },
    container: {
        padding: 16,
        marginHorizontal: 16,
        marginTop: 24,
        backgroundColor: "#fff",

        ...(Platform.OS === "android"
        ? {
            borderRadius: 12,
            elevation: 4,
            shadowColor: "#000",
            shadowOpacity: 0.15,
            shadowRadius: 6,
            shadowOffset: { width: 0, height: 3 },
            }
        : {
            backgroundColor: "#fff",
            padding: 16,
            marginBottom: StyleSheet.hairlineWidth,
            borderBottomWidth: StyleSheet.hairlineWidth,
            borderBottomColor: "#ccc"
            }),

        }
});