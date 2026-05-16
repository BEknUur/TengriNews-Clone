import * as React from 'react';

import { Label } from '@/common/components/ui/label';
import { cn } from '@/common/lib/utils';

const Textarea = React.forwardRef<
  HTMLTextAreaElement,
  React.ComponentProps<'textarea'> & {
    label?: string;
    error?: string;
  }
>(({ className, label, error, id, ...props }, ref) => {
  const textareaId = id ?? props.name;

  return (
    <div className="flex flex-col gap-2">
      {label ? <Label htmlFor={textareaId}>{label}</Label> : null}
      <textarea
        ref={ref}
        id={textareaId}
        data-slot="textarea"
        aria-invalid={Boolean(error)}
        className={cn(
          'border-input placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-ring/50 flex min-h-20 w-full rounded-md border bg-transparent px-3 py-2 text-base shadow-xs transition-[color,box-shadow] outline-none focus-visible:ring-[3px] disabled:cursor-not-allowed disabled:opacity-50 md:text-sm',
          'aria-invalid:ring-destructive/20 aria-invalid:border-destructive',
          className,
        )}
        {...props}
      />
      {error ? <span className="text-sm text-destructive">{error}</span> : null}
    </div>
  );
});

Textarea.displayName = 'Textarea';

export { Textarea };
