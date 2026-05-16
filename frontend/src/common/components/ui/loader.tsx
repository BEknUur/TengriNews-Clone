import { Loader2Icon } from 'lucide-react';

import { cn } from '@/common/lib/utils';

interface LoaderProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const sizeClasses = {
  sm: 'size-4',
  md: 'size-8',
  lg: 'size-12',
};

export const Loader = ({ size = 'md', className }: LoaderProps) => {
  return (
    <Loader2Icon
      className={cn('animate-spin text-primary', sizeClasses[size], className)}
      aria-label="Loading"
    />
  );
};
