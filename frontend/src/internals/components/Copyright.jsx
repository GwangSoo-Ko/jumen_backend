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
      본 사이트의 컨텐츠는 투자 정보 제공을 목적으로 작성되었으며, 어떠한 경우에도 투자 결과에 대한 법적 책임 등의 판단 근거로 사용될 수 없습니다. <br />
      모든 투자의 최종 결정과 책임은 투자자 본인에게 있습니다. <br /> <br />
        UI components powered by&nbsp;
        <Link color="inherit" href="https://mui.com/" target="_blank" rel="noopener">
          MUI (Material-UI)
        </Link>
        .<br />
        Copyright (c) 2014-present MUI contributors.<br />
        Released under the MIT license. <br /> <br />
        
      </Typography>
    </Box>
  );
}
