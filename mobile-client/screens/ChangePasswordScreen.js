import React, { useState } from 'react';
import { View, Text, TextInput, Button, StyleSheet, Alert } from 'react-native';
import api from '../api';

export default function ChangePasswordScreen({ navigation }) {
    const [currentPassword, setCurrentPassword] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');

    const handleChangePassword = async () => {
        if (!currentPassword || !newPassword || !confirmPassword) {
            Alert.alert('エラー', '全ての項目を入力してください');
            return;
        }

        if (newPassword !== confirmPassword) {
            Alert.alert('エラー', '新しいパスワードが一致しません');
            return;
        }

        try {
            await api.post('/change_password', {
                current_password: currentPassword,
                new_password: newPassword
            });
            Alert.alert('成功', 'パスワードを変更しました', [
                {
                    text: 'OK',
                    onPress: () => navigation.replace('Dashboard')
                }
            ]);
        } catch (error) {
            console.error(error);
            Alert.alert('エラー', 'パスワードの変更に失敗しました');
        }
    };

    return (
        <View style={styles.container}>
            <Text style={styles.title}>パスワード変更が必要です</Text>
            <Text style={styles.subtitle}>
                初期パスワードを使用しています。セキュリティのため、新しいパスワードを設定してください。
            </Text>

            <TextInput
                style={styles.input}
                placeholder="現在のパスワード（初期は学籍番号）"
                value={currentPassword}
                onChangeText={setCurrentPassword}
                secureTextEntry={true}
            />
            <TextInput
                style={styles.input}
                placeholder="新しいパスワード"
                value={newPassword}
                onChangeText={setNewPassword}
                secureTextEntry={true}
            />
            <TextInput
                style={styles.input}
                placeholder="新しいパスワード（確認）"
                value={confirmPassword}
                onChangeText={setConfirmPassword}
                secureTextEntry={true}
            />

            <Button title="パスワードを変更" onPress={handleChangePassword} />
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
        fontSize: 22,
        fontWeight: 'bold',
        marginBottom: 10,
        textAlign: 'center',
        color: '#e74c3c'
    },
    subtitle: {
        fontSize: 14,
        marginBottom: 30,
        textAlign: 'center',
        color: '#555'
    },
    input: {
        borderWidth: 1,
        borderColor: '#ccc',
        padding: 10,
        marginBottom: 15,
        borderRadius: 5,
    },
});
