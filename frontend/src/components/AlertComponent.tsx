// Component that is just a simple pop up alert that can be used to display messages to the user
// The alert can be closed by clicking the close button

import React from 'react';

interface AlertProps {
  message: string;
}

const AlertComponent: React.FC<AlertProps> = ({ message }) => {
  return (
    <div className="alert">
      <span className="close">
        &times;
      </span>
      {message}
    </div>
  );
};

export default AlertComponent;