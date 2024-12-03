// components/default/overview/card.tsx
import React from 'react';

interface OverviewCardProps {
  mainicon: React.ElementType;
  secicon: React.ElementType;
  label: string;
  onClick?: () => void;
}

const OverviewCard: React.FC<OverviewCardProps> = ({
  mainicon: MainIcon,
  secicon: SecIcon,
  label,
  onClick
}) => {
  return (
    <div
      className="border rounded-lg p-4 flex flex-col hover:border-blue-500 transition-colors cursor-pointer "
      onClick={onClick}
    >
      <div className="flex flex-row justify-between mb-5">
        <div className="flex items-center justify-center w-8 h-8 bg-slate-600 rounded-md">
          <MainIcon className="w-5 h-5 text-white" />
        </div>
        <div className="flex items-center justify-center w-8 h-8 hover:bg-slate-100 rounded-full transition-colors">
          <SecIcon className="w-5 h-5 text-slate-600" />
        </div>
      </div>
      <div className="flex flex-row mt-2">
        <span className="text-md text-slate-600">{label}</span>
      </div>
    </div>
  );
};

export default OverviewCard;
