import * as React from 'react';

import { Label } from '@/common/components/ui/label';
import { cn } from '@/common/lib/utils';

const Input = React.forwardRef<
  HTMLInputElement,
  React.ComponentProps<'input'> & {
    label?: string;
    error?: string;
  }
>(({ className, type, label, error, id, ...props }, ref) => {
  const inputId = id ?? props.name;

  return (
    <div className="flex flex-col gap-2">
      {label ? <Label htmlFor={inputId}>{label}</Label> : null}
      <input
        ref={ref}
        id={inputId}
        type={type}
        data-slot="input"
        aria-invalid={Boolean(error)}
        className={cn(
          'file:text-foreground placeholder:text-muted-foreground selection:bg-primary selection:text-primary-foreground border-input flex h-9 w-full min-w-0 rounded-md border bg-transparent px-3 py-1 text-base shadow-xs transition-[color,box-shadow] outline-none file:inline-flex file:h-7 file:border-0 file:bg-transparent file:text-sm file:font-medium disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 md:text-sm',
          'focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px]',
          'aria-invalid:ring-destructive/20 aria-invalid:border-destructive',
          className,
        )}
        {...props}
      />
      {error ? <span className="text-sm text-destructive">{error}</span> : null}
    </div>
  );
});

Input.displayName = 'Input';

export { Input };
