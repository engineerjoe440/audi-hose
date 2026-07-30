import * as React from 'react';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import IconButton from '@mui/material/IconButton';
import PlayCircleIcon from '@mui/icons-material/PlayCircle';
import PauseCircleIcon from '@mui/icons-material/PauseCircle';
import { api_client, fetchToken } from '../auth';

export const AudioPlayerDialog = ({ recordingId, onClose }) => {
  const audioUrl = `/recordings/${recordingId}`;
  const [audioSource, setAudioSource] = React.useState(null);
  const [audioElement, setAudioElement] = React.useState(null);
  const [isPlaying, setIsPlaying] = React.useState(false);
  const [isLoading, setIsLoading] = React.useState(false);
  const [error, setError] = React.useState(null);

  React.useEffect(() => {
    if (!recordingId) return;

    setIsLoading(true);
    setError(null);

    api_client
      .get(audioUrl, {
        responseType: 'blob',
        headers: {
          Authorization: `Bearer ${fetchToken()}`,
          Accept: 'audio/mpeg'
        }
      })
      .then((response) => {
        const blob = response.data;
        const localUrl = URL.createObjectURL(blob);

        setAudioSource(localUrl);
        setAudioElement(new Audio(localUrl));
      })
      .catch((err) => {
        const message =
          err?.response?.status
            ? `Network response failed: ${err.response.status}`
            : err.message || 'Unknown error';

        setError(message);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [recordingId, audioUrl]);

  // 2. Play or Pause the downloaded audio object
  const togglePlay = () => {
    if (!audioElement) return;

    if (isPlaying) {
      audioElement.pause();
      setIsPlaying(false);
    } else {
      audioElement.play()
        .then(() => setIsPlaying(true))
        .catch((err) => setError("Playback failed: " + err.message));
    }
  };

  // 3. Listen for the track ending naturally to update state
  React.useEffect(() => {
    if (!audioElement) return;

    const handleEnded = () => setIsPlaying(false);
    audioElement.addEventListener('ended', handleEnded);

    // Clean up listeners and revoke object URLs to prevent memory leaks
    return () => {
      audioElement.removeEventListener('ended', handleEnded);
      audioElement.pause();
    };
  }, [audioElement]);

  // Clean up the memory object URL when component unmounts
  React.useEffect(() => {
    return () => {
      if (audioSource) {
        URL.revokeObjectURL(audioSource);
      }
    };
  }, [audioSource]);

  return (
    <React.Fragment>
      <Dialog
        open={recordingId !== null}
        onClose={onClose}
        aria-labelledby="audio-player-title"
        aria-describedby="audio-player-description"
      >
        <DialogTitle id="audio-player-title">
          {"Audio Player"}
        </DialogTitle>
        <DialogContent>
        {error ? (
          <DialogContentText style={{ color: 'red' }}>
            Error: {error}
          </DialogContentText>
        ) : (
          <>
          {isLoading ? (
            'Downloading...'
          ) : (
            <div>
              <IconButton onClick={togglePlay}>
                {isPlaying ? <PauseCircleIcon /> : <PlayCircleIcon />}
              </IconButton>
            </div>
          )}
          </>
        )}
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Close</Button>
        </DialogActions>
      </Dialog>
    </React.Fragment>
  );
};
