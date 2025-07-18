import React from 'react';
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

// HTML 태그를 안전하게 처리하는 유틸리티 함수 (XSS 방지)
const sanitizeHtml = (html) => {
  if (!html) return '';
  // 기본적인 XSS 방지 (실제 프로덕션에서는 DOMPurify 같은 라이브러리 사용 권장)
  return html.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
};

export default function TextEditor({ 
  value, 
  onChange, 
  disabled = false, 
  sanitize = true // HTML 정리 옵션 (보안용)
}) {
  
  const handleChange = (content, delta, source, editor) => {
    // React Quill이 HTML을 올바르게 처리하도록 HTML 그대로 사용
    const processedContent = sanitize ? sanitizeHtml(content) : content;
    onChange(processedContent);
  };

  // value 처리: HTML을 그대로 React Quill에 전달
  const processedValue = (() => {
    if (!value) return '';
    return sanitize ? sanitizeHtml(value) : value;
  })();

  return (
    <ReactQuill
      value={processedValue}
      onChange={handleChange}
      modules={modules}
      formats={formats}
      readOnly={disabled}
      style={{ 
        height: '300px',
        marginBottom: '50px' // 툴바가 겹치지 않도록 여백 추가
      }}
    />
  );
}