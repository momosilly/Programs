import { useState, useEffect } from "react";
import { View, Text, FlatList, Pressable } from "react-native";
import { fetchRequests } from "../../src/api";
import { useRouter } from "expo-router";

export default function Submitted() {
    const router = useRouter()
    const [projects, setProjects] = useState<any[]>([]);

    useEffect(() => {
    fetchRequests().then((data) => {
        console.log("Fetched data:", data);
        console.log("Is array:", Array.isArray(data));
        setProjects(Array.isArray(data) ? data : []);
    });
    }, []);

    
    return (
        <View style={{ padding: 20 }}>
            <Text style={{ fontSize: 22, fontWeight: "bold" }}>
                Your requests
            </Text>
            <FlatList
                data={projects}
                keyExtractor={(item) => item.id.toString()}
                renderItem={({ item }) => (
                <Pressable onPress={() => router.push(`projects/${item.id}`)}>
                    <View style={{ marginVertical: 10 }}>
                        <Text>Objectives: {item.learning_objectives}</Text>
                    </View>
                </Pressable>
                )}
            />
        </View>
    )
}