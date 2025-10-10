import React from 'react';

type Props = {
  label: string;
  value: number | string;
  dotClassName: string; // ex.: 'bg-green-500'
  className?: string;
};

export default function StatusItem({ label, value, dotClassName, className }: Props) {
  return (
    <div
      className={`flex items-center justify-between border border-gray-200 rounded-md px-3 py-2 bg-gray-50 hover:bg-gray-100 transition-colors ${
        className || ''
      }`}
      aria-label={`${label}: ${value}`}
    >
      <span className="flex items-center gap-2 text-xs text-gray-700">
        <span className={`w-2 h-2 rounded-full ${dotClassName}`}></span>
        {label}
      </span>
      <span className="font-medium text-gray-900 text-sm">{value}</span>
    </div>
  );
}