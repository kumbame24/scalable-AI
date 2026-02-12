import React, { createContext, useState, useContext, useEffect } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchUser = async () => {
            console.log("AuthContext: fetchUser started, token exists:", !!token);

            // Safety timeout to prevent permanent loading loop
            const timeoutId = setTimeout(() => {
                console.warn("AuthContext: Fetch user timeout reached, forcing loading to false");
                setLoading(false);
            }, 3000);

            if (token) {
                localStorage.setItem('token', token);
                try {
                    console.log("AuthContext: fetching /users/me...");
                    const response = await fetch('http://localhost:8000/users/me', {
                        headers: { 'Authorization': `Bearer ${token}` }
                    });
                    console.log("AuthContext: /users/me response status:", response.status);
                    if (response.ok) {
                        const userData = await response.json();
                        console.log("AuthContext: user data received", userData);
                        setUser(userData);
                    } else {
                        console.warn("AuthContext: /users/me failed, clearing token");
                        setToken(null);
                        localStorage.removeItem('token');
                    }
                } catch (error) {
                    console.error("AuthContext: Error fetching user:", error);
                }
            } else {
                console.log("AuthContext: no token, clearing user state");
                localStorage.removeItem('token');
                setUser(null);
            }

            clearTimeout(timeoutId);
            console.log("AuthContext: setting loading to false naturally");
            setLoading(false);
        };
        fetchUser();
    }, [token]);

    const login = async (username, password) => {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);

        const response = await fetch('http://localhost:8000/auth/login', {
            method: 'POST',
            body: formData,
        });

        if (response.ok) {
            const data = await response.json();
            setToken(data.access_token);
            return true;
        }
        return false;
    };

    const register = async (username, email, password, role) => {
        const response = await fetch('http://localhost:8000/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password, role }),
        });
        return response.ok;
    };

    const logout = () => {
        setToken(null);
    };

    return (
        <AuthContext.Provider value={{ user, token, loading, login, register, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
