// src/components/ui/button.tsx
import * as React from 'react';

type Variant = 'default' | 'outline' | 'ghost' | 'destructive' | 'secondary';
type Size = 'sm' | 'md' | 'lg' | 'icon';

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
}

function cn(...classes: Array<string | undefined | false>) {
  return classes.filter(Boolean).join(' ');
}

const variantClasses: Record<Variant, string> = {
  default:
    'bg-primary text-white hover:opacity-90 focus-visible:ring-primary',
  outline:
    'border border-border hover:bg-card/60 text-foreground focus-visible:ring-border',
  ghost:
    'bg-transparent hover:bg-card/60 text-foreground focus-visible:ring-border',
  destructive:
    'bg-destructive text-white hover:opacity-90 focus-visible:ring-destructive',
  secondary:
    'bg-card text-foreground hover:bg-card/80 focus-visible:ring-border',
};

const sizeClasses: Record<Size, string> = {
  sm: 'h-8 px-3 text-sm',
  md: 'h-10 px-4 text-sm',
  lg: 'h-12 px-6 text-base',
  icon: 'h-10 w-10 p-0',
};

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'default', size = 'md', ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(
          'inline-flex items-center justify-center gap-2 rounded-md font-medium transition-colors',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2',
          'disabled:opacity-50 disabled:pointer-events-none',
          variantClasses[variant],
          sizeClasses[size],
          className
        )}
        {...props}
      />
    );
  }
);

Button.displayName = 'Button';

export default Button;
