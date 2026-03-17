import { NativeTabs, Icon, Label } from 'expo-router/unstable-native-tabs';
import { useEffect, useState } from 'react';
import { getUserFromToken } from '../../src/auth';
import { Platform } from 'react-native';

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
        <NativeTabs>
            {!isAdmin && (
                <NativeTabs.Trigger name='project'>
                    <Label>Home</Label>
                    <Icon 
                        sf={{default: 'house', selected: 'house.fill'}}
                        src={Platform.OS === 'android' ? require('../../assets/project.png') : undefined}
                    />
                </NativeTabs.Trigger>
            )}
            {!isAdmin && (
                <NativeTabs.Trigger name='submitted'>
                    <Label>Submitted</Label>
                    <Icon 
                        sf={{ default: 'tray', selected: 'tray.fill' }}
                        src={Platform.OS === 'android' ? require('../../assets/submitted.png') : undefined}
                    />
                </NativeTabs.Trigger>
            )}
            {isAdmin && (
                <NativeTabs.Trigger name='admin'>
                    <Label>Admin Panel</Label>
                    <Icon 
                        src={require('../../assets/admin.png')}
                    />
                </NativeTabs.Trigger>
            )}
        </NativeTabs>
    );
}