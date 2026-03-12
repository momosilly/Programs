import { useState, useEffect } from "react";
import { View, Text, FlatList, Pressable, StyleSheet } from "react-native";
import { fetchRequests } from "../../src/api";
import { useLocalSearchParams, useRouter } from "expo-router";
import { DropdownMenu } from "../(components)/DropdownMenu";
import { MenuOption } from "../(components)/MenuOption";
import { getAuthKey } from "../../src/storage/keys";
import AsyncStorage from "@react-native-async-storage/async-storage";

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
        <View style={{ padding: 20 }}>
            <Text style={{ fontSize: 22, fontWeight: "bold" }}>
                Your requests
            </Text>
            <View style={styles.container}>
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
                data={filteredProjects}
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

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5fcff',
  },
  triggerStyle: {
    height: 40,
    backgroundColor: '#f5fcff',
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    width: 100,
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 5,
  },
  triggerText: {
    fontSize: 16,
  }
});