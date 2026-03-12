import { TouchableOpacity } from "react-native";
import React, { ReactNode } from "react";

export const MenuOption = ({
    onSelect,
    children
}: {
    onSelect: () => void;
    children: ReactNode;
}) => {
    return (
        <TouchableOpacity onPress={onSelect} style={{padding: 5}}>
            {children}
        </TouchableOpacity>
    );
};