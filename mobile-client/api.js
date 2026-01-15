import axios from 'axios';
import * as SecureStore from 'expo-secure-store';

// Replace with your computer's IP address if running on physical device
// For Android Emulator, 10.0.2.2 is localhost
// For iOS Simulator, localhost works
const BASE_URL = 'http://10.23.130.167:5000/api';

const api = axios.create({
    baseURL: BASE_URL,
});

api.interceptors.request.use(async (config) => {
    const token = await SecureStore.getItemAsync('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export default api;
