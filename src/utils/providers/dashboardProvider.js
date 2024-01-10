import React, { createContext, useContext, useState } from "react";
import { themeChill } from "../colors/colorThemes";

const DashboardContext = createContext();

export const useDashboardContext = () => {
    return useContext(DashboardContext);
};

export const DashboardProvider = ({ children }) => {
    const [openDrawer, setOpenDrawer] = useState(false);
    const [theme, setTheme] = useState(themeChill);
    const [dialogOpen, setDialogOpen] = useState(false);
    const [tagChips, setTagChips] = useState([
        { selected: false, label: 'Tech' },
        { selected: false, label: 'Food' },
        { selected: false, label: 'Metro' },
        { selected: false, label: 'Sport' },
        { selected: false, label: 'World' },
        { selected: false, label: 'Nation' },
        { selected: false, label: 'Business' },
        { selected: false, label: 'Asean+' },
        { selected: false, label: 'Education' },
        { selected: false, label: 'Lifestyle' }
    ]);

    const handleTagChip = (targetChip) => {
        setTagChips((chips) =>
            chips.map((chip) =>
                chip.label === targetChip.label
                    ? { ...chip, selected: !chip.selected }
                    : chip
            )
        );
    };

    const handleDialogOpen = () => setDialogOpen(!dialogOpen);

    const handleDrawer = () => setOpenDrawer(!openDrawer);

    const handleTheme = (selectedTheme) => setTheme(selectedTheme);

    return (
        <DashboardContext.Provider
            value={{ handleTagChip, openDrawer, handleDrawer, handleTheme, theme, tagChips, dialogOpen, handleDialogOpen }}>
            {children}
        </DashboardContext.Provider>
    );
};
