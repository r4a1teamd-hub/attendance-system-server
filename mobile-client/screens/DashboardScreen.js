import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, StyleSheet, Button, ActivityIndicator } from 'react-native';
import * as SecureStore from 'expo-secure-store';
import api from '../api';

export default function DashboardScreen({ navigation }) {
    const [attendances, setAttendances] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchAttendance();
    }, []);

    const fetchAttendance = async () => {
        try {
            const response = await api.get('/attendance/me');
            setAttendances(response.data);
            setLoading(false);
        } catch (error) {
            console.error(error);
            setLoading(false);
        }
    };

    const handleLogout = async () => {
        await SecureStore.deleteItemAsync('token');
        navigation.replace('Login');
    };

    const getStatusText = (status) => {
        const s = status ? status.toLowerCase() : '';
        switch (s) {
            case 'present': return '出席';
            case 'absent': return '欠席';
            case 'late': return '遅刻';
            default: return status;
        }
    };

    const renderItem = ({ item }) => {
        // Force JST (Asia/Tokyo) display regardless of device locale
        // Ensure the timestamp indicates UTC by appending 'Z' if missing (assuming server sends naive UTC)
        const dateStr = item.timestamp.endsWith('Z') ? item.timestamp : item.timestamp + 'Z';
        const dateObj = new Date(dateStr);

        const formattedDate = new Intl.DateTimeFormat('ja-JP', {
            timeZone: 'Asia/Tokyo',
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        }).format(dateObj);

        return (
            <View style={styles.item}>
                <Text style={styles.date}>{formattedDate}</Text>
                <Text style={[styles.status, styles[item.status]]}>{getStatusText(item.status)}</Text>
            </View>
        );
    };

    if (loading) {
        return (
            <View style={styles.center}>
                <ActivityIndicator size="large" />
            </View>
        );
    }

    return (
        <View style={styles.container}>
            <View style={styles.header}>
                <Text style={styles.title}>出席履歴</Text>
                <Button title="ログアウト" onPress={handleLogout} />
            </View>
            <FlatList
                data={attendances}
                renderItem={renderItem}
                keyExtractor={(item) => item.id.toString()}
                ListEmptyComponent={<Text style={styles.empty}>出席記録がありません。</Text>}
            />
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        padding: 20,
        backgroundColor: '#f5f5f5',
    },
    center: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
    },
    header: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 20,
        marginTop: 40,
    },
    title: {
        fontSize: 24,
        fontWeight: 'bold',
    },
    item: {
        backgroundColor: '#fff',
        padding: 15,
        borderRadius: 8,
        marginBottom: 10,
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.1,
        shadowRadius: 2,
        elevation: 2,
    },
    date: {
        fontSize: 16,
    },
    status: {
        fontWeight: 'bold',
    },
    present: { color: 'green' },
    absent: { color: 'red' },
    late: { color: 'orange' },
    empty: {
        textAlign: 'center',
        marginTop: 20,
        color: '#666',
    },
});
