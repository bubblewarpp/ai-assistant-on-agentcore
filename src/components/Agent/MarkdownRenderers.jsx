import React from "react";

export function CodeRenderer({ inline, className, children, ...props }) {
  const content = String(children ?? "");

  if (inline) {
    return (
      <code className={className} {...props}>
        {children}
      </code>
    );
  }

  return (
    <pre className="overflow-x-auto rounded-lg p-3 text-sm">
      <code className={className} {...props}>
        {content}
      </code>
    </pre>
  );
}

export function LinkRenderer({ href, children, ...props }) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="underline underline-offset-2"
      {...props}
    >
      {children}
    </a>
  );
}

export default {
  code: CodeRenderer,
  a: LinkRenderer
};
