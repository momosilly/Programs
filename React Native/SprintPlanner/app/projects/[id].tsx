import { useLocalSearchParams } from "expo-router";
import { useEffect, useState } from "react";
import { View, Text, Button } from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { getProject, updateStatus } from "../../src/api";
import { getUserFromToken } from "../../src/auth";
import { getAuthKey } from "../../src/storage/keys";

export default function projectDetail() {
    interface Project {
    id: number
    learning_objectives: string
    start_date: string
    deadline: string
    user_id: number
    };


    const { id } = useLocalSearchParams();
    const [project, setProject] = useState<Project | null>(null);
    const [status, setStatus] = useState<any | null>(null);
    const [isAdmin, setIsAdmin] = useState(false);

    useEffect(() => {
        async function load() {
            const token = await AsyncStorage.getItem(getAuthKey("access_token"));
            if (!token) return;

            const user = await getUserFromToken();
            setIsAdmin(user?.is_admin ?? false);

            const data = await getProject(Number(id), token);
            setProject(data.project);
            setStatus(data.status);
        }

        load();
    }, [])

    async function handleUpdate(field: string) {
        const token = await AsyncStorage.getItem(getAuthKey("access_token"))
        if (!token) return;
        const updated = await updateStatus(Number(id), { [field]: true }, token);

        const data = await getProject(Number(id), token);
        setStatus(data.status);
    }

    if (!project || !status) return null;

    const getStatusLabel = (status: any) => {
        if (status.signed) return "Signed";
        if (status.handed_in) return "Handed in";
        if (status.approved) return "Approved";
        if (status.pending) return "Pending";
    }

    return (
        <View>
            <Text>Objectives: {project.learning_objectives}</Text>
            <Text>Start date: {project.start_date}</Text>
            <Text>Deadline: {project.deadline}</Text>
            <Text>Status: {getStatusLabel(status)}</Text>

            {!isAdmin && (
                <Button title="Mark as handed in" onPress={() => handleUpdate("handed_in")} disabled={!status.approved}/>
            )}

            {isAdmin && (
                <>
                    <Button title="Approve" onPress={() => handleUpdate("approved")} disabled={(status.approved || status.signed) ? true : false}/>
                    <Button title="Sign" onPress={() => handleUpdate("signed")} disabled={(!status.approved || !status.handed_in) ? true : false} />
                </>
            )}
        </View>
    );
}