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
            if (response.data.user && response.data.user.is_password_changed === false) {
                navigation.replace('ChangePassword');
            } else {
                navigation.replace('Dashboard');
            }
        } catch (error) {
            Alert.alert('ログイン失敗', '認証情報が無効です');
        }
    };

    const handleForgotPassword = () => {
        Alert.alert(
            'パスワードを忘れましたか？',
            '管理者にパスワードのリセットを申請しますか？',
            [
                { text: 'キャンセル', style: 'cancel' },
                {
                    text: '申請する',
                    onPress: () => {
                        // TODO: Implement actual API call here later or just alert for now
                        Alert.alert('申請完了', '管理者にリセット依頼を送信しました（デモ）。管理者に直接連絡してください。');
                    }
                }
            ]
        );
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
                secureTextEntry={true}
            />
            <Button title="ログイン" onPress={handleLogin} />
            <View style={{ marginTop: 20 }}>
                <Button title="パスワードを忘れた場合" onPress={handleForgotPassword} color="#888888" />
            </View>
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
