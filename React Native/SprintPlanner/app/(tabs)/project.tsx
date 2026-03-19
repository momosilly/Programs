import { StatusBar } from 'expo-status-bar';
import { useRouter } from 'expo-router';
import { StyleSheet, Text, View, Pressable, TextInput, Button, Image, Platform } from 'react-native';
import React, { useState } from "react";
import DateTimePicker, { DateTimePickerEvent } from '@react-native-community/datetimepicker';
import { submitRequest, logout } from '../../src/api';
import { SafeAreaView } from 'react-native-safe-area-context';

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

    return (
        <SafeAreaView style={[styles.container, { padding: 20, paddingTop: 10, marginBottom: 34 }]}>
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
                <Pressable 
                    onPress={() => setShowstart(true)} 
                    style={({ pressed }) => [
                        styles.pressable,
                        pressed && styles.pressablePressed
                    ]}
                >
                    <Text style={styles.pressableText}>Select start date</Text>
                </Pressable>
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

                <Pressable 
                    onPress={() => setShowDeadline(true)} 
                    style={({ pressed }) => [
                        styles.pressable,
                        pressed && styles.pressablePressed
                    ]}
                >
                    <Text style={styles.pressableText}>Select deadline</Text>
                </Pressable>
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
                style={({ pressed }) => [
                    styles.pressable,
                    pressed && styles.pressablePressed
                ]}
            >
                <Text style={styles.pressableText}>Submit</Text>
            </Pressable>
            <Pressable 
                onPress={async () => {
                    await logout();
                    router.replace("/(modals)/login")
                }}
                style={({ pressed }) => [
                    styles.logout, 
                    pressed && styles.pressablePressed, 
                    {
                        position: 'absolute', 
                        bottom: 80, 
                        left: 20, 
                        borderTopWidth: StyleSheet.hairlineWidth
                    }]}
            >
                <Image 
                    source={require("../../assets/logout.png")}
                    style={{ height: 24, width: 24 }}
                />
            </Pressable>
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#fff',
        justifyContent: 'center',
    },
    input: {
        paddingVertical: Platform.OS === "android" ? 12 : 10,
        paddingHorizontal: 14,
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
        fontSize: 18
    },
    pressablePressed: {
        opacity: Platform.OS === 'ios' ? 0.5 : 1,
        transform: Platform.OS === 'android' ? [{ scale: 0.97 }] : undefined
    },
    logout: {
        borderColor: '#1b6cef',
        borderStyle: 'solid',
        borderRadius: 50,
        backgroundColor: '#1b6cef',
        padding: 10,
        width: 50,
        alignItems: 'center'
    }
});
