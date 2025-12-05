import React, { useState } from 'react';
import { View, Text, TextInput, Button, StyleSheet, Alert } from 'react-native';
import * as SecureStore from 'expo-secure-store';
import api from '../api';

export default function LoginScreen({ navigation }) {
    const [studentId, setStudentId] = useState('');
    const [password, setPassword] = useState('');

    const handleLogin = async () => {
        try {
            const response = await api.post('/login', { student_id: studentId, password });
            await SecureStore.setItemAsync('token', response.data.token);
            navigation.replace('Dashboard');
        } catch (error) {
            Alert.alert('ログイン失敗', '認証情報が無効です');
        }
    };

    return (
        <View style={styles.container}>
            <Text style={styles.title}>学生ログイン</Text>
            <TextInput
                style={styles.input}
                placeholder="学籍番号"
                value={studentId}
                onChangeText={setStudentId}
                autoCapitalize="none"
            />
            <TextInput
                style={styles.input}
                placeholder="パスワード"
                value={password}
                onChangeText={setPassword}
                secureTextEntry
            />
            <Button title="ログイン" onPress={handleLogin} />
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        justifyContent: 'center',
        padding: 20,
        backgroundColor: '#fff',
    },
    title: {
        fontSize: 24,
        fontWeight: 'bold',
        marginBottom: 20,
        textAlign: 'center',
    },
    input: {
        borderWidth: 1,
        borderColor: '#ccc',
        padding: 10,
        marginBottom: 15,
        borderRadius: 5,
    },
});
