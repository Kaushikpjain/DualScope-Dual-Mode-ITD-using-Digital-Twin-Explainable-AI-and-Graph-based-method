import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

export const getDashboardSummary = async () => {
    const response = await axios.get(`${API_BASE_URL}/dashboard/summary`);
    return response.data;
};

export const getUsers = async (limit = 50, offset = 0) => {
    const response = await axios.get(`${API_BASE_URL}/users`, { params: { limit, offset } });
    return response.data;
};

export const searchUsers = async (query) => {
    const response = await axios.get(`${API_BASE_URL}/users/search`, { params: { q: query } });
    return response.data;
};

export const getUserBehavior = async (userId) => {
    const response = await axios.get(`${API_BASE_URL}/users/${userId}/behavior`);
    return response.data;
};

export const getUserExplanation = async (userId) => {
    const response = await axios.get(`${API_BASE_URL}/users/${userId}/explain`);
    return response.data;
};

export const getGraphThreats = async () => {
    const response = await axios.get(`${API_BASE_URL}/graph/threats`);
    return response.data;
};

export const getAnalyticsOverview = async () => {
    const response = await axios.get(`${API_BASE_URL}/analytics/overview`);
    return response.data;
};

export const getAnalyticsTimeline = async () => {
    const response = await axios.get(`${API_BASE_URL}/analytics/timeline`);
    return response.data;
};

export const getUserActivityGraph = async (userId) => {
    const response = await axios.get(`${API_BASE_URL}/graph/user/${userId}`);
    return response.data;
};
