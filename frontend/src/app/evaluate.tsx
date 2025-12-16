import React, { useState } from 'react';
import { StyleSheet, Text, View, ScrollView, ActivityIndicator } from 'react-native';
import { typography } from './styles/typography';
import Icon from '../components/Icon';
import { colors } from './styles/colors';
import PrimaryBtn from '@/components/PrimaryBtn';
import PlaybackControlBtn from '@/components/PlaybackControlBtn';
import { togglePlayback } from '../utils/togglePlayback';
import { startRecording, stopRecording } from '../utils/recording';
import { pickAndUpload, uploadRecordedAudio } from '../utils/upload';
import { EVALUATE_URL } from './constants/constants';



export default function Evaluate() {

    const API_URL = EVALUATE_URL;

    const [loading, setLoading] = useState(false);
    const [recording, setRecording] = useState(null);
    const [recordedUri, setRecordedUri] = useState(null);
    const [currentAudioName, setCurrentAudioName] = useState("");
    const [uploadedUri, setUploadedUri] = useState(null);
    const [sound, setSound] = useState(null);
    const [isPlaying, setIsPlaying] = useState(false);
    const [result, setResult] = useState(null);

    const onTogglePlayback = async () => {
        await togglePlayback(isPlaying, sound, setIsPlaying);
    }
    const onStartRecording = async () => {
        await startRecording(setRecording);
    }
    const onStopRecording = async () => {
        await stopRecording(recording, setRecording, setRecordedUri, setCurrentAudioName);
    }
    const onUploadRecordedAudio = async () => {
        await uploadRecordedAudio(API_URL, recordedUri, setRecordedUri, setLoading, setResult, setIsPlaying, setSound);
    }
    const onPickAndUpload = async () => {
        await pickAndUpload(API_URL, setCurrentAudioName, setUploadedUri, setLoading, setResult, setIsPlaying, setSound);
    }



    return (
        <View style={{ flex: 1, backgroundColor: colors.background }}>

            <Text style={[typography.title, { marginTop: 70 }]}>Evaluate audio</Text>

            <View style={styles.loadingContainer}>
                {loading && <ActivityIndicator size="large" color={colors.green} />}
            </View>
            <ScrollView contentContainerStyle={{ paddingBottom: 120 }}>
                {result && !loading ?
                    <View style={{ marginTop: 70 }}>
                        <Text style={[typography.audio, { alignSelf: 'center' }]}>Audio: {currentAudioName}</Text>

                        <View style={{ marginVertical: 10 }}>
                            <View style={styles.container}>
                                <View style={{ alignItems: 'center' }}>
                                    <Text style={typography.subtitle}>pitch variation</Text>
                                    <Text style={typography.metric}>{Number(result.audio_metrics.jitter.toFixed(2))}</Text>
                                </View>
                                <View style={{ alignItems: 'center' }}>
                                    <Text style={typography.subtitle}>volume variation</Text>
                                    <Text style={typography.metric}>{Number(result.audio_metrics.shimmer.toFixed(2))}</Text>
                                </View>
                            </View>
                            <View style={styles.container}>
                                <View style={{ alignItems: 'center' }}>
                                    <Text style={typography.subtitle}>voice cleanliness</Text>
                                    <Text style={typography.metric}>{Number(result.audio_metrics.hnr.toFixed(2))}</Text>
                                </View>
                                <View style={{ alignItems: 'center' }}>
                                    <Text style={typography.subtitle}>background noise</Text>
                                    <Text style={typography.metric}>{Number(result.audio_metrics.snr.toFixed(2))}</Text>
                                </View>
                            </View>
                        </View>

                        <Text style={[typography.subtitle, { alignSelf: 'center' }]}>Score</Text>

                        <View style={[styles.container, { marginVertical: 20 }]}>
                            <View style={{ alignItems: 'center' }}>
                                <Text style={typography.subtitle}>quality score</Text>
                                <Text style={typography.metric}>{Number(result.score.score.toFixed(1))}</Text>
                            </View>
                            <View style={{ alignItems: 'center' }}>
                                <Text style={typography.subtitle}>label</Text>
                                <Text style={typography.metric}>{result.score.label}</Text>
                            </View>
                        </View>

                        <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', marginTop: 30 }}>
                            <PlaybackControlBtn onPress={onTogglePlayback}>
                                <Icon name='playPause' width={45} height={45}></Icon>
                            </PlaybackControlBtn>
                        </View>

                    </View>
                    : (
                        <Text>Upload or record an audio to evaluate</Text>
                    )
                }
            </ScrollView >


            <View style={[styles.bottomBar, { opacity: !loading ? 1 : 0 }]}
                pointerEvents={loading ? 'none' : 'auto'}
            >

                <View style={{ marginBottom: 20 }}>
                    <View style={{ alignItems: 'center' }}>
                        {recording ? (
                            <PlaybackControlBtn onPress={onStopRecording}>
                                <Icon name='stopRecording' width={40} height={40}></Icon>
                            </PlaybackControlBtn>
                        ) : (
                            <PlaybackControlBtn onPress={onStartRecording}>
                                <Icon name='microphone' width={40} height={40}></Icon>
                            </PlaybackControlBtn>
                        )}
                    </View>

                    <View style={{ opacity: recordedUri && !loading ? 1 : 0, marginBottom: 0, marginTop: 10 }}
                    >
                        <PrimaryBtn title="Evaluate recording" onPress={onUploadRecordedAudio} />
                    </View>
                </View>

                <PrimaryBtn
                    title='Upload audio'
                    onPress={onPickAndUpload}
                ></PrimaryBtn>

            </View>

        </View >
    );
}


const styles = StyleSheet.create({
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