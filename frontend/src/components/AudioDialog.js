import * as React from 'react';
import {
  Button, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle,
  Grid, IconButton, TextField
} from '@mui/material';
import PlayCircleIcon from '@mui/icons-material/PlayCircle';
import PauseCircleIcon from '@mui/icons-material/PauseCircle';
import { AudioRecorder } from 'react-audio-voice-recorder';

export default function AudioDialog(props) {
  const [playing, setPlaying] = React.useState(false);
  
  const addAudioElement = (blob) => {
    const url = URL.createObjectURL(blob);
    const audio = document.createElement('audio');
    audio.src = url;
    audio.controls = true;
    document.getElementById("audihose-dialog-playback").innerHTML = '';
    document.getElementById("audihose-dialog-playback").appendChild(audio);
  };

  return (
    <React.Fragment>
      <Dialog
        open={props.open}
        onClose={props.onClose}
      >
        <DialogTitle>Record a Message</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Send us a message! We can't wait to hear from you.
          </DialogContentText>
          <TextField
            autoFocus
            margin="dense"
            id="subject"
            name="subject"
            label="Subject"
            type="text"
            fullWidth
            variant="standard"
          />
          <br />
          <br />
          <Grid container spacing={2}>
            <Grid item xs={2}>
              <AudioRecorder
                onRecordingComplete={addAudioElement}
                audioTrackConstraints={{
                  noiseSuppression: true,
                  echoCancellation: true,
                  // autoGainControl,
                  // channelCount,
                  // deviceId,
                  // groupId,
                  // sampleRate,
                  // sampleSize,
                }}
                onNotAllowedOrFound={(err) => console.table(err)}
                downloadOnSavePress={false}
                downloadFileExtension="mp3"
                mediaRecorderOptions={{
                  audioBitsPerSecond: 128000,
                }}
                // showVisualizer={true}
              />
            </Grid>
            <Grid item xs={10}>
              <div id="audihose-dialog-playback"/>
            </Grid>
          </Grid>
          <TextField
            required
            margin="dense"
            id="email"
            name="email"
            label="Email Address"
            type="email"
            fullWidth
            variant="standard"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={props.onClose}>Cancel</Button>
          <Button onClick={props.onClose}>Submit</Button>
        </DialogActions>
      </Dialog>
    </React.Fragment>
  );
}
