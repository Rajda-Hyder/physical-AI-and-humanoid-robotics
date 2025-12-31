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
            apiUrl="http://physical-ai-and-humanoid-robotics-production-e85e.up.railway.app"
            position="bottom-right"
            minimized={true}
          />
        </AuthProvider>
      )}
    </BrowserOnly>
  );
};

export default Root;
