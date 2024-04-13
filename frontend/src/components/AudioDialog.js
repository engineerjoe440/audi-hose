import * as React from 'react';
import {
  Button, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle,
  Grid, TextField
} from '@mui/material';
import axios from "axios";
import { AudioRecorder } from 'react-audio-voice-recorder';

export default function AudioDialog(props) {
  const audio = document.createElement('audio');
  const [audioBlob, setAudioBlob] = React.useState(null);

  const addAudioElement = (blob) => {
    setAudioBlob(blob.slice());
    const url = URL.createObjectURL(blob);
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
        PaperProps={{
          component: 'form',
          onSubmit: (event) => {
            event.preventDefault();
            const formData = new FormData(event.currentTarget);
            const formJson = Object.fromEntries(formData.entries());

            // Set Up and Submit the Audio File
            const submissionData = new FormData();
            submissionData.append('recording', audioBlob);
            axios({
              url: `${props.audihoseUrl}api/v1/recordings/`,
              method: 'put',
              data: submissionData,
              params: {
                subject: formJson.subject,
                email: formJson.email,
                group_id: props.groupId,
              },
              headers: {
                'Accept': 'application/json',
                'Content-Type': 'multipart/form-data'
              },
            }).then(response=>{console.log(response)}).catch(error=>{console.log(error)});

            // Close the Dialog
            props.onClose(event);
          }
        }}
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
          <Button type="submit">Submit</Button>
        </DialogActions>
      </Dialog>
    </React.Fragment>
  );
}
