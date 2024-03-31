import React from 'react';
import { Button, SvgIcon } from '@mui/material';

function MicrophoneSvg() {
  return (
    <SvgIcon>
      <svg viewBox="0 0 20 20" enable-background="new 0 0 20 20">
        <path fill="#FFFFFF" d="M16.399,7.643V10.4c0,2.236-1.643,4.629-5.399,4.959V18h2.6c0.22,0,0.4,0.18,0.4,0.4v1.2
                                c0,0.221-0.181,0.4-0.4,0.4H6.4C6.18,20,6,19.82,6,19.6v-1.2C6,18.18,6.18,18,6.399,18H9v-2.641c-3.758-0.33-5.4-2.723-5.4-4.959
                                V7.643c0-0.221,0.18-0.4,0.4-0.4h0.6c0.22,0,0.4,0.18,0.4,0.4V10.4c0,1.336,1.053,3.6,5,3.6c3.946,0,5-2.264,5-3.6V7.643
                                c0-0.221,0.18-0.4,0.399-0.4H16C16.22,7.242,16.399,7.422,16.399,7.643z M10,12c2.346,0,3-0.965,3-1.6V7.242H7V10.4
                                C7,11.035,7.652,12,10,12z M13,1.6C13,0.963,12.346,0,10,0C7.652,0,7,0.963,7,1.6v4.242h6V1.6z"/>
      </svg>
    </SvgIcon>
  )
}

export default function RecordButton(props) {

    return (
      <div style={{right: 20, bottom: 20, position: "fixed"}}>
        <Button
          variant="contained"
          onClick={props.onClick}
          sx={{
            borderRadius: 8,
            backgroundColor: props.color,
            "&:hover": {
              backgroundColor: props.color,
              filter: "brightness(85%)",
            },
          }}
          startIcon={<MicrophoneSvg />}
        >
          <span>Record</span>
        </Button>
      </div>
    );
}