import React, { ReactNode } from 'react';
import { AuthProvider } from '../contexts/AuthContext';
import BrowserOnly from '@docusaurus/BrowserOnly';
import ChatWidget from '../components/ChatWidget';

interface RootProps {
  children: ReactNode;
}

const Root: React.FC<RootProps> = ({ children }) => {
  return (
    <BrowserOnly
      fallback={<div>{children}</div>}
    >
      {() => (
        <AuthProvider>
          {children}
          <ChatWidget
            apiUrl={process.env.REACT_APP_API_URL || 'http://localhost:8000'}
            position="bottom-right"
            minimized={true}
          />
        </AuthProvider>
      )}
    </BrowserOnly>
  );
};

export default Root;
