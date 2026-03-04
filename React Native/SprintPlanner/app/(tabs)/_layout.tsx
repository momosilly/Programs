import { Tabs } from 'expo-router';
import { useEffect, useState } from 'react';
import { getUserFromToken } from '../../src/auth';

export default function TabLayout() {
    const [isAdmin, setIsAdmin] = useState<boolean | null>(null);

    useEffect(() => {
        getUserFromToken().then((user) => {
            console.log('User from token:', user);
            const adminStatus = user?.is_admin ?? false;
            setIsAdmin(adminStatus);
        });
    }, []);

    if (isAdmin === null) return null;

    return (
        <Tabs initialRouteName={isAdmin ? 'admin' : 'project'}>
            <Tabs.Screen name="project" options={{ title: "Projects", href: !isAdmin ? 'project' : null}} />
            <Tabs.Screen name="submitted" options={{ title: "Submitted", href: !isAdmin ? 'submitted' : null }} />
            <Tabs.Screen name="admin" options={{ title: "Admin Panel" , href: isAdmin ? 'admin' : null}} />
        </Tabs>
    )
}