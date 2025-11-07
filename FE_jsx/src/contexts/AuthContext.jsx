import { createContext, useContext, useState, useEffect } from 'react';
import {
    signInWithEmailAndPassword,
    createUserWithEmailAndPassword,
    signOut,
    onAuthStateChanged,
    GoogleAuthProvider,
    signInWithPopup
} from 'firebase/auth';
import { auth } from '../firebase/config';

const AuthContext = createContext();

export function useAuth() {
    return useContext(AuthContext);
}

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [token, setToken] = useState(null);

    useEffect(() => {
        const unsubscribe = onAuthStateChanged(auth, async (user) => {
            setUser(user);
            if (user) {
                const idToken = await user.getIdToken();
                setToken(idToken);
                localStorage.setItem('authToken', idToken);
            } else {
                setToken(null);
                localStorage.removeItem('authToken');
            }
            setLoading(false);
        });

        return unsubscribe;
    }, []);

    const login = async (email, password) => {
        const result = await signInWithEmailAndPassword(auth, email, password);
        const idToken = await result.user.getIdToken();
        setToken(idToken);
        localStorage.setItem('authToken', idToken);
        return result;
    };

    const signup = async (email, password) => {
        const result = await createUserWithEmailAndPassword(auth, email, password);
        const idToken = await result.user.getIdToken();
        setToken(idToken);
        localStorage.setItem('authToken', idToken);
        return result;
    };

    const loginWithGoogle = async () => {
        const provider = new GoogleAuthProvider();
        const result = await signInWithPopup(auth, provider);
        const idToken = await result.user.getIdToken();
        setToken(idToken);
        localStorage.setItem('authToken', idToken);
        return result;
    };

    const logout = async () => {
        await signOut(auth);
        setToken(null);
        localStorage.removeItem('authToken');
    };

    const refreshToken = async () => {
        if (user) {
            const idToken = await user.getIdToken(true);
            setToken(idToken);
            localStorage.setItem('authToken', idToken);
            return idToken;
        }
        return null;
    };

    const value = {
        user,
        token,
        login,
        signup,
        loginWithGoogle,
        logout,
        refreshToken,
        loading,
        isAuthenticated: !!user
    };

    return (
        <AuthContext.Provider value={value}>
            {!loading && children}
        </AuthContext.Provider>
    );
}
