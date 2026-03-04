import { StatusBar } from 'expo-status-bar';
import { useRouter } from 'expo-router';
import { StyleSheet, Text, View, Pressable, TextInput, Button, Alert } from 'react-native';
import React, { useState } from "react";
import DateTimePicker, { DateTimePickerEvent } from '@react-native-community/datetimepicker';
import { submitRequest, logout } from '../../src/api';

export default function App() {
    const router = useRouter();

    const [text, setOnChangeText] = useState("");
    const [startDate, setStartDate] = useState(new Date);
    const [deadline, setDeadline] = useState(new Date());
    const [showStart, setShowstart] = useState(false);
    const [showDeadline, setShowDeadline] = useState(false);
    
    //Datepicker configuration
    const onStartChange = (_: any, selectedDate ?: Date) => {
        setShowstart(false);
        if (selectedDate) {
            setStartDate(selectedDate);
            setDeadline(selectedDate);
        }
    };
    const onDeadlineChange = (_: any, selectedDate ?: Date) => {
        setShowDeadline(false);
        if (selectedDate) setDeadline(selectedDate);
    };
    const maxDeadline = new Date(startDate);
    maxDeadline.setDate(startDate.getDate() + 7);
    const today = new Date();
    const in7Days = new Date();
    in7Days.setDate(today.getDate() + 7);

    const [height, setHeight] = useState(40);
    const [items, setItems] = useState<[string, string | null][]>([]);

    return (
        <View style={styles.container}>
            <TextInput 
                multiline
                style={[styles.input, {height,}]}
                value={text}
                onChangeText={setOnChangeText}
                placeholder='Learning Objectives'
                onContentSizeChange={(e) => 
                    setHeight(e.nativeEvent.contentSize.height)
                }
            />
            <View>
                <Button title='Select start date' onPress={() => setShowstart(true)}/>
                {showStart && (
                    <DateTimePicker 
                        value={startDate}
                        mode='date'
                        display='default'
                        onChange={onStartChange}
                        minimumDate={startDate}
                        maximumDate={in7Days}
                    />
                )}
                <Button title="Select deadline" onPress={() => setShowDeadline(true)}/>
                {showDeadline && (
                    <DateTimePicker 
                        value={deadline}
                        mode='date'
                        display='default'
                        onChange={onDeadlineChange}
                        minimumDate={startDate}
                        maximumDate={maxDeadline}
                    />
                )}
            </View>
            <Pressable
                onPress={() => 
                    submitRequest({
                        text,
                        startDate: startDate.toISOString().split("T")[0],
                        deadline: deadline.toISOString().split("T")[0]
                    })
                }
            >
                <Text>Submit</Text>
            </Pressable>
            <Button title='Logout' onPress={async () => {
                await logout();
                router.replace("/(modals)/login");
            }} />
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#fff',
        alignItems: 'center',
        justifyContent: 'center',
    },
    input: {
        minHeight: 40,
        padding: 10,
        width: 300,
        borderWidth: 1,
        borderColor: '#ccc',
        borderRadius: 6
    },
});
