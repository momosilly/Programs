import { useState, useEffect } from "react";
import { View, Text, FlatList, Button, Pressable, BackHandler, StyleSheet } from "react-native";
import { fetchRequests } from "../../src/api";
import { useRouter } from "expo-router";
import { logout } from "../../src/api";
import { DropdownMenu } from "../(components)/DropdownMenu";
import { MenuOption } from "../(components)/MenuOption";

export default function Submitted() {
    const router = useRouter()
    const [projects, setProjects] = useState<any[]>([]);
    const [filter, setFilter] = useState<any | null>(null);
    const [visible, setVisible] = useState(false);
    const filteredProjects = filter ? projects.filter(p => p?.status?.[filter]) : projects;

    useEffect(() => {
    fetchRequests().then((data) => {
        console.log("Fetched data:", data);
        console.log("Is array:", Array.isArray(data));
        setProjects(Array.isArray(data) ? data : []);
    });

    const onBackPress = () => {
        return true;
    }

    const subscription = BackHandler.addEventListener(
        'hardwareBackPress',
        onBackPress
    );

    return () => subscription.remove();
    }, []);

    
    return (
        <View style={{ padding: 20 }}>
            <Text style={{ fontSize: 22, fontWeight: "bold" }}>
                Available requests
            </Text>
            <View style={styles.container}>
                <DropdownMenu
                    visible={visible}
                    handleOpen={() => setVisible(true)}
                    handleClose={() => setVisible(false)}
                    trigger={
                        <View style={styles.triggerStyle}>
                            <Text style={styles.triggerText}>Filter</Text>
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
                <Pressable onPress={() => router.push(`/projects/${item.id}`)}>
                    <View style={{ marginVertical: 10 }}>
                        <Text>Name: {item.user_name}</Text>
                        <Text>Objectives: {item.learning_objectives}</Text>
                        <Text>Start: {item.start_date}</Text>
                        <Text>Deadline: {item.deadline}</Text>
                    </View>
                </Pressable>
                )}
            />
            <Button title='Logout' onPress={async () => {
                await logout();
                router.replace("/(modals)/login");
            }} />
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