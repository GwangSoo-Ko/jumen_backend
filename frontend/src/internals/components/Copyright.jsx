import * as React from 'react';
import Link from '@mui/material/Link';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';

export default function Copyright(props) {
  return (
    <Box sx={{ textAlign: 'center', py: 2 }}>
      <Typography variant="body2" color="text.secondary" align="center" {...props}>
        {'Copyright © '}
        <Link color="inherit" href="https://yourdomain.com/">
          Jumen
        </Link>{' '}
        {new Date().getFullYear()}
        {'.'}
      </Typography>
      <Typography variant="caption" color="text.secondary" align="center" display="block" sx={{ mt: 1 }}>
        UI components powered by&nbsp;
        <Link color="inherit" href="https://mui.com/" target="_blank" rel="noopener">
          MUI (Material-UI)
        </Link>
        .<br />
        Copyright (c) 2014-present MUI contributors.<br />
        Released under the MIT license.
      </Typography>
    </Box>
  );
}
