import React, { useState } from 'react';
import ReactQuill from 'react-quill-new';
import 'react-quill-new/dist/quill.snow.css';

const formats = [
  'header',
  'font',
  'color', 'background',
  'align',
  'bold', 'italic', 'underline', 'strike', 'blockquote',
  'list', 'indent',
  'link', 'image'
];

const modules = {
  toolbar: [
    [{ 'header': [1, 2, false] }],
    [{ 'font': [] }],
    [{ 'color': [] }, { 'background': [] }],
    [{ 'align': [] }],
    ['bold', 'italic', 'underline','strike', 'blockquote'],
    [{'list': 'ordered'}, {'list': 'bullet'}, {'indent': '-1'}, {'indent': '+1'}],
    ['link', 'image'],
    ['clean']
  ]
};

export default function TextEditor(props) {
  const [value, setValue] = useState('');
  return (
    <ReactQuill
      value={value}
      onChange={setValue}
      modules={modules}
      formats={formats}
    />
  );
}