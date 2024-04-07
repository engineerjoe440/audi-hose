import * as React from 'react';
import AudioDialog from "./components/AudioDialog";
import RecordButton from "./components/RecordButton";

export default function EmbedableRecorder(props) {
  const [open, setOpen] = React.useState(false);

  const handleClose = () => {
    setOpen(false);
  }

  return (
    <div>
      <RecordButton
        color={props.color}
        prompt={props.prompt}
        onClick={() => {setOpen(true)}}
      />
      <AudioDialog
        open={open}
        groupId={props.groupId}
        onClose={handleClose}
      />
    </div>
  );
}
