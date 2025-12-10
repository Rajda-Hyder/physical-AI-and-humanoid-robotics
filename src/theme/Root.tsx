import React, { ReactNode } from 'react';
import { AuthProvider } from '../contexts/AuthContext';
import BrowserOnly from '@docusaurus/BrowserOnly';

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
        </AuthProvider>
      )}
    </BrowserOnly>
  );
};

export default Root;
