import { useState, useEffect } from "react";
import { View, Text, FlatList, Button } from "react-native";
import { fetchRequests } from "../../src/api";
import { useRouter } from "expo-router";
import { logout } from "../../src/api";

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
                Available requests
            </Text>
            <FlatList 
                data={projects}
                keyExtractor={(item) => item.id.toString()}
                renderItem={({ item }) => (
                <View style={{ marginVertical: 10 }}>
                    <Text>Objectives: {item.learning_objectives}</Text>
                    <Text>Start: {item.start_date}</Text>
                    <Text>Deadline: {item.deadline}</Text>
                </View>
                )}
            />
            <Button title='Logout' onPress={async () => {
                await logout();
                router.replace("/(modals)/login");
            }} />
        </View>
    )
}