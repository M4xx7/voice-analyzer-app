import { StyleSheet } from 'react-native';
import { colors } from './colors';

export const styles = StyleSheet.create({
    container: {
        flex: 1,
        flexDirection: 'row',
        gap: 40,
        justifyContent: "center",
        padding: 20,
    },

    iconWrapper: {
        flex: 1,
        flexDirection: 'row',
        gap: 5
    },

    bottomBar: {
        position: 'fixed',
        padding: 20,
        marginBottom: 40,
        backgroundColor: colors.background
    },

    loadingContainer: {
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        justifyContent: 'center',
        alignItems: 'center',
    },

});
